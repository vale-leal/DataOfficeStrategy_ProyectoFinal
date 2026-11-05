"""Etapa 4 - Calidad: mide nulos, duplicados, atípicos y validez. Solo mide; no modifica ningún dato."""

from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

RAIZ = Path(__file__).resolve().parents[1]  # raíz del repo: el script funciona desde cualquier carpeta
DIR_ENTRADA = RAIZ / "data" / "processed" / "normalizado"
DIR_SALIDA = RAIZ / "data" / "processed" / "calidad"

HORAS = [f"hora_{h:02d}" for h in range(24)]
FECHA_MIN = pd.Timestamp("2022-01-01")
HOY = pd.Timestamp.today().normalize()
FACTOR_IQR = 3  # 3*IQR marca solo valores extremos, no la variación normal de la serie
METRICAS = []  # cada registrar() agrega aquí una fila; al final se vuelca al CSV

# Por colección: medidas, entidad para atípicos y frecuencia (D diaria, MS mensual, None esporádica)
COLECCIONES = {
    "aportes": {"medidas": ["aportes_energia_kwh", "aportes_caudal_m3_s", "aportes_media_historica_energia_kwh",
                            "aportes_media_historica_caudal_m3_s", "aportes_95_pss_energia_kwh",
                            "aportes_95_pss_caudal_m3_s"], "entidad": "nombre_rio", "frecuencia": "MS"},
    "capacidad": {"medidas": ["capacidad_efectiva_neta_kw"], "entidad": "recurso", "frecuencia": "D"},
    "compras_bolsa": {"medidas": HORAS, "entidad": "codigo_agente", "frecuencia": "D"},
    "demanda": {"medidas": ["demanda_energia_sin_kwh", "generacion_kwh", "demanda_no_atendida_kwh",
                            "exportaciones_kwh", "importaciones_kwh"], "entidad": None, "frecuencia": "D"},
    "generacion": {"medidas": HORAS, "entidad": "recurso", "frecuencia": "D"},
    "reservas": {"medidas": ["volumen_util_diario_pct"], "entidad": None, "frecuencia": "D"},
    "vertimientos": {"medidas": ["vertimientos_volumen_miles_m3", "vertimientos_energia_kwh"],
                     "entidad": "nombre_embalse", "frecuencia": None},
}


def registrar(coleccion, regla, valor):
    """Agrega una métrica a la lista que al final se guarda en CSV."""
    METRICAS.append({"coleccion": coleccion, "regla": regla, "valor": valor})


def pct(parte, total):
    """Porcentaje con 4 decimales; con 4 se ven los casos muy raros que con 2 quedarían en 0."""
    return round(100 * parte / total, 4) if total else 0.0


def medir_nulos(nombre, df, medidas):
    """Porcentaje de nulos por medida; las 24 horas se agrupan en total y peor hora."""
    if medidas is HORAS:
        nulos = df[HORAS].isna()
        registrar(nombre, "nulos_pct:horas_total", pct(nulos.values.sum(), nulos.size))
        peor = nulos.mean().idxmax()
        registrar(nombre, f"nulos_pct:peor_hora:{peor}", pct(nulos[peor].sum(), len(df)))
        return
    for col in medidas:
        registrar(nombre, f"nulos_pct:{col}", pct(df[col].isna().sum(), len(df)))


def medir_cobertura(nombre, df, frecuencia):
    """Fechas distintas presentes sobre las esperadas entre la mínima y la máxima."""
    if frecuencia is None:
        # Vertimientos solo tiene filas los días en que hubo vertimiento: los huecos son esperados
        registrar(nombre, "cobertura_fechas_pct", "no aplica: serie esporádica")
        return
    esperadas = pd.date_range(df["fecha"].min(), df["fecha"].max(), freq=frecuencia)
    registrar(nombre, "cobertura_fechas_pct", pct(df["fecha"].nunique(), len(esperadas)))


def medir_duplicados(nombre, df, llave):
    """Cuenta filas con llave repetida; en series con version revisa también la llave sin ella."""
    duplicada = df.duplicated(subset=llave, keep=False)  # todas las copias: ninguna es confiable sola
    registrar(nombre, "duplicados_llave", int(duplicada.sum()))
    if "version" in llave:
        sin_version = [c for c in llave if c != "version"]
        registrar(nombre, "duplicados_llave_sin_version", int(df.duplicated(subset=sin_version, keep=False).sum()))
        # Si un año tuviera dos versiones de liquidación (TX4 y TX5), habría registros repetidos
        for anio, versiones in df.groupby("anio_archivo")["version"].unique().items():
            registrar(nombre, f"versiones:{anio}", ",".join(sorted(str(v) for v in versiones)))
    return duplicada


def contar_atipicos(nombre, etiqueta, valores, grupos):
    """Cuenta valores fuera de [Q1 - 3*IQR, Q3 + 3*IQR], con cuartiles calculados dentro de cada grupo."""
    por_grupo = valores.groupby(grupos)
    q1, q3 = por_grupo.transform("quantile", q=0.25), por_grupo.transform("quantile", q=0.75)
    fuera = (valores < q1 - FACTOR_IQR * (q3 - q1)) | (valores > q3 + FACTOR_IQR * (q3 - q1))
    registrar(nombre, f"atipicos_n:{etiqueta}", int(fuera.sum()))
    registrar(nombre, f"atipicos_pct:{etiqueta}", pct(fuera.sum(), valores.notna().sum()))


def medir_atipicos(nombre, df, conf):
    """Busca atípicos dentro de cada entidad; en series horarias usa el total diario."""
    entidad = conf["entidad"]
    if conf["medidas"] is HORAS:
        # Cada hora por separado tiene muchos ceros (p. ej. solar de noche); el total diario es más estable
        diario = df.groupby([entidad, "fecha"])[HORAS].sum(min_count=1).sum(axis=1, min_count=1)
        contar_atipicos(nombre, "total_diario", diario, diario.index.get_level_values(entidad))
        return
    grupos = df[entidad] if entidad else pd.Series(0, index=df.index)  # sin entidad: un solo grupo
    for col in conf["medidas"]:
        contar_atipicos(nombre, col, df[col], grupos)


def medir_validez(nombre, df, medidas, duplicada):
    """Cuenta registros inválidos y devuelve cuántos cumplen todas las reglas por registro."""
    negativo = (df[medidas] < 0).any(axis=1)
    # Solo reservas tiene porcentaje; en las demás get() devuelve una serie vacía (sin registros fuera)
    porcentaje = df.get("volumen_util_diario_pct", pd.Series(float("nan"), index=df.index))
    pct_fuera = porcentaje.notna() & ~porcentaje.between(0, 100)  # un nulo no invalida el registro
    fecha_mala = df["fecha"].isna() | (df["fecha"] < FECHA_MIN) | (df["fecha"] > HOY)
    registrar(nombre, "registros_medida_negativa", int(negativo.sum()))
    registrar(nombre, "registros_pct_fuera_0_100", int(pct_fuera.sum()))
    registrar(nombre, "registros_fecha_fuera_rango", int(fecha_mala.sum()))
    valido = ~(negativo | pct_fuera | fecha_mala | duplicada)  # nulos y atípicos se reportan aparte
    registrar(nombre, "registros_validos_pct", pct(valido.sum(), len(df)))
    return int(valido.sum())


def medir_bitacoras(nombre):
    """Cuenta los valores que la normalización invalidó e imputó en la colección (0 si no hay filas)."""
    # Las bitácoras las escribe normalizacion.py en esta misma carpeta en cada corrida
    incidentes = pd.read_csv(DIR_SALIDA / "incidentes_validez.csv")
    imputaciones = pd.read_csv(DIR_SALIDA / "imputaciones.csv")
    registrar(nombre, "valores_invalidados_normalizacion", int((incidentes["coleccion"] == nombre).sum()))
    imputados = imputaciones.loc[imputaciones["coleccion"] == nombre, "n_celdas"].sum()
    registrar(nombre, "valores_imputados_normalizacion", int(imputados))


def evaluar(nombre, conf):
    """Lee una colección y aplica las cinco reglas; devuelve (registros válidos, registros totales)."""
    ruta = DIR_ENTRADA / f"{nombre}.parquet"
    # archivo_origen no interviene en ninguna regla; no leerlo ahorra memoria en las tablas grandes
    df = pd.read_parquet(ruta, columns=[c for c in pq.read_schema(ruta).names if c != "archivo_origen"])
    llave = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    registrar(nombre, "registros", len(df))
    medir_nulos(nombre, df, conf["medidas"])
    medir_cobertura(nombre, df, conf["frecuencia"])
    duplicada = medir_duplicados(nombre, df, llave)
    medir_atipicos(nombre, df, conf)
    medir_bitacoras(nombre)
    return medir_validez(nombre, df, conf["medidas"], duplicada), len(df)


def main():
    """Evalúa las colecciones una a una, guarda el CSV de métricas y lo imprime por colección."""
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    resultados = [evaluar(nombre, conf) for nombre, conf in COLECCIONES.items()]
    validos, registros = sum(v for v, _ in resultados), sum(r for _, r in resultados)
    # Con millones de filas unos pocos inválidos no mueven el porcentaje: se reporta también el conteo
    registrar("GLOBAL", "registros_invalidos", f"{registros - validos} de {registros}")
    registrar("GLOBAL", "registros_validos_pct", pct(validos, registros))
    metricas = pd.DataFrame(METRICAS)
    metricas.insert(0, "fecha_ejecucion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    metricas.to_csv(DIR_SALIDA / "metricas_calidad.csv", index=False)
    for coleccion, grupo in metricas.groupby("coleccion", sort=False):
        print(f"== {coleccion}")
        for regla, valor in zip(grupo["regla"], grupo["valor"]):
            print(f"  {regla:<50} {valor}")
        print()


if __name__ == "__main__":
    main()
