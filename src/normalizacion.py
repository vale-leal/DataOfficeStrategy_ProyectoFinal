"""Etapa 3 - Normalización: estandariza nombres, texto, fechas y números de cada colección.

Además invalida valores fuera de rango e imputa unas pocas medidas acordadas (reglas en limpieza.py),
con bitácora en data/processed/calidad/. No filtra filas ni elimina duplicados. Uso: python src/normalizacion.py
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

try:
    from limpieza import HORAS, NOMBRES_SALIDA, aplicar_validez, guardar_bitacoras, imputar
except ImportError:  # importado como src.normalizacion: la carpeta src no está en sys.path
    from src.limpieza import HORAS, NOMBRES_SALIDA, aplicar_validez, guardar_bitacoras, imputar

# Rutas relativas a la raíz del repo, para que funcione sin importar desde dónde se ejecute
RAIZ = Path(__file__).resolve().parents[1]
DIR_ENTRADA = RAIZ / "data" / "processed" / "ingesta"
DIR_SALIDA = RAIZ / "data" / "processed" / "normalizado"
DIR_CALIDAD = RAIZ / "data" / "processed" / "calidad"

TOKENS_NULOS = ["", "-", "N/D", "N/A", "NA"]
MESES = {"ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6, "JULIO": 7,
         "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12}

# Medidas numéricas por colección (nombres ya normalizados)
MEDIDAS = {
    "Aportes": ["aportes_energia_kwh", "aportes_caudal_m3_s", "aportes_media_historica_energia_kwh",
                "aportes_media_historica_caudal_m3_s", "aportes_95_pss_energia_kwh", "aportes_95_pss_caudal_m3_s"],
    "Capacidad": ["capacidad_efectiva_neta_kw"],
    "Demanda": ["demanda_energia_sin_kwh", "generacion_kwh", "demanda_no_atendida_kwh",
                "exportaciones_kwh", "importaciones_kwh"],
    "Generacion": HORAS,
    "Precio": HORAS,
    "Reservas": ["volumen_util_diario_pct"],
    "Vertimentos": ["vertimientos_volumen_miles_m3", "vertimientos_energia_kwh"],
}

# Filas esperadas: la normalización no debe ganar ni perder registros respecto a la ingesta
FILAS_ESPERADAS = {"Aportes": 2268, "Capacidad": 1383086, "Demanda": 1730, "Generacion": 505643,
                   "Precio": 199213, "Reservas": 1731, "Vertimentos": 3989}


def normalizar_nombre(nombre):
    """Convierte un encabezado a snake_case sin tildes; las horas "0".."23" pasan a hora_00..hora_23."""
    if nombre.isdigit():
        return f"hora_{int(nombre):02d}"
    nombre = nombre.replace("%", "pct")
    # NFKD separa la tilde de la letra; al pasar a ASCII la tilde se descarta (Ú -> U, ñ -> n)
    nombre = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return re.sub(r"[^0-9a-z]+", "_", nombre.lower()).strip("_")


def fusionar_duplicadas(df):
    """Une columnas con el mismo nombre (p. ej. Version/Versión) tomando el primer valor no nulo por fila."""
    for nombre in df.columns[df.columns.duplicated()].unique():
        bloque = df.loc[:, df.columns == nombre]
        # bfill hacia la izquierda deja en la primera columna el primer valor no nulo de la fila
        unida = bloque.bfill(axis=1).iloc[:, 0]
        # .copy() evita que pandas trate el resultado como una vista de la tabla original
        df = df.loc[:, df.columns != nombre].copy()
        df[nombre] = unida
    return df


def limpiar_texto(df):
    """Quita espacios sobrantes en todas las columnas de texto y convierte los tokens de nulo en NaN."""
    for col in df.select_dtypes(include="object").columns:
        # \s+ -> " " corrige casos como "AGPE  ALIMENTOS" (doble espacio) sin tocar el resto
        df[col] = df[col].str.strip().str.replace(r"\s+", " ", regex=True)
        df[col] = df[col].replace(TOKENS_NULOS, pd.NA)
    return df


def convertir_fecha(df):
    """Convierte la columna fecha; los 10 primeros caracteres cubren "2026-01-01" y "2022-01-01 00:00:00"."""
    df["fecha"] = pd.to_datetime(df["fecha"].str[:10], format="%Y-%m-%d")
    return df


def fecha_desde_ano_mes(df):
    """Construye la fecha mensual de Aportes como el día 1 del mes a partir de año y mes en español."""
    mes = df["mes"].str.upper().map(MESES)
    desconocidos = df.loc[mes.isna(), "mes"].unique()
    if len(desconocidos) > 0:
        raise ValueError(f"Meses no reconocidos en Aportes: {list(desconocidos)}")
    df["fecha"] = pd.to_datetime(pd.DataFrame({"year": df["ano"].astype(int), "month": mes, "day": 1}))
    return df


def convertir_medidas(df, medidas):
    """Pasa las medidas a número y avisa si algún valor no nulo se perdió en la conversión."""
    total_perdidos = 0
    for col in medidas:
        antes = df[col].notna()
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Un valor que existía y ahora es nulo indica texto no numérico que habría que revisar
        perdidos = (antes & df[col].isna()).sum()
        if perdidos > 0:
            print(f"  ATENCIÓN {col}: {perdidos} valores no numéricos pasaron a nulo")
        total_perdidos += perdidos
    print(f"  conversión numérica: {total_perdidos} valores no nulos pasaron a nulo ({len(medidas)} medidas)")
    return df


def a_largo(df, nombre_valor):
    """Pasa las 24 columnas hora_XX a filas con columnas hora (0-23) y nombre_valor."""
    ids = [c for c in df.columns if c not in HORAS]
    largo = df.melt(id_vars=ids, value_vars=HORAS, var_name="hora", value_name=nombre_valor)
    largo["hora"] = largo["hora"].str[5:].astype(int)
    return largo


def normalizar(df, coleccion):
    """Aplica todas las reglas de normalización a una colección completa."""
    df.columns = [normalizar_nombre(c) for c in df.columns]
    # Las columnas sin_nombre_* vienen de celdas combinadas o vacías del Excel; no tienen datos
    df = df.drop(columns=[c for c in df.columns if c.startswith("sin_nombre")])
    df = fusionar_duplicadas(df)
    df = limpiar_texto(df)
    df = fecha_desde_ano_mes(df) if coleccion == "Aportes" else convertir_fecha(df)
    df = convertir_medidas(df, MEDIDAS[coleccion])
    if coleccion == "Aportes":
        # Antes de validez e imputación: solo debe marcar lo que vino vacío de la fuente, no lo que tocamos
        df["dato_no_registrado"] = df[MEDIDAS["Aportes"]].isna().any(axis=1)
        print(f"  dato_no_registrado: {int(df['dato_no_registrado'].sum())} filas en True")
    # La validez va antes de imputar: un valor invalidado puede ser candidato a imputación
    invalidos = aplicar_validez(df, coleccion, MEDIDAS[coleccion])
    nulos_antes = df[MEDIDAS[coleccion]].isna().values.sum()
    imputar(df, coleccion, invalidos)
    print(f"  validez: {sum(int(m.sum()) for m in invalidos.values())} valores pasaron a nulo | "
          f"imputación: {nulos_antes - df[MEDIDAS[coleccion]].isna().values.sum()} valores imputados")
    df["anio_archivo"] = df["anio_archivo"].astype(int)
    return df


def validar(df, coleccion, filas_entrada):
    """Imprime filas, columnas, tipos, nulos y rango de fechas, y falla si cambió el número de filas."""
    print(f"  filas entrada {filas_entrada} | filas salida {len(df)} | esperadas {FILAS_ESPERADAS[coleccion]}")
    if len(df) != FILAS_ESPERADAS[coleccion]:
        raise ValueError(f"{coleccion}: {len(df)} filas, se esperaban {FILAS_ESPERADAS[coleccion]}")
    print(f"  columnas ({df.shape[1]}): {list(df.columns)}")
    # Las 24 horas comparten tipo; se resumen en una línea para que la salida sea legible
    tipos = {c: str(t) for c, t in df.dtypes.items() if c not in HORAS}
    if HORAS[0] in df.columns:
        tipos["hora_00..hora_23"] = str(df[HORAS[0]].dtype)
    print(f"  dtypes: {tipos}")
    # Se filtra antes de redondear para no ocultar columnas con muy pocos nulos
    pct_nulos = df.isna().mean() * 100
    print(f"  columnas con nulos (%): {pct_nulos[pct_nulos > 0].round(4).to_dict() or 'ninguna'}")
    print(f"  rango de fechas: {df['fecha'].min().date()} -> {df['fecha'].max().date()}")


def main():
    """Normaliza las colecciones una a una para no tener varias tablas grandes en memoria."""
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    for ruta in sorted(DIR_ENTRADA.glob("*.parquet")):
        coleccion = ruta.stem
        print(f"== {coleccion}")
        df = pd.read_parquet(ruta)
        filas_entrada = len(df)
        df = normalizar(df, coleccion)
        validar(df, coleccion, filas_entrada)
        df.to_parquet(DIR_SALIDA / f"{NOMBRES_SALIDA.get(coleccion, coleccion.lower())}.parquet", index=False)
        if coleccion == "Generacion":
            # Prueba de a_largo solo sobre una muestra: el melt completo multiplicaría las filas por 24
            muestra = a_largo(df.head(1000), "energia_kwh")
            print(f"  prueba a_largo (1000 filas de Generacion): {len(muestra)} filas (esperadas 24000)")
        del df
        print()
    guardar_bitacoras(DIR_CALIDAD)


if __name__ == "__main__":
    main()
