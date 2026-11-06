"""Reglas de validez e imputación que usa normalizacion.py, con su bitácora en data/processed/calidad/.

No se ejecuta por sí solo: normalizacion.py importa estas funciones y las llama en su flujo.
"""

import pandas as pd

HORAS = [f"hora_{h:02d}" for h in range(24)]
# Entidad de cada colección para las bitácoras; demanda y reservas son una sola serie (sin entidad)
ENTIDADES = {"Aportes": "nombre_rio", "Capacidad": "recurso", "Generacion": "recurso",
             "Precio": "codigo_agente", "Vertimentos": "nombre_embalse"}
# Vertimentos corrige la errata de la carpeta; Precio son compras en bolsa (kWh), no precios
NOMBRES_SALIDA = {"Vertimentos": "vertimientos", "Precio": "compras_bolsa"}
CV_MAXIMO = 0.5  # si el cociente energía/caudal del río varía más que esto, no sirve para imputar
INCIDENTES, IMPUTACIONES = [], []  # filas de las bitácoras; se escriben en CSV al final de main()


def bitacora(coleccion, df, marca, medida, **campos):
    """Arma las filas de bitácora (incidente o imputación) de las celdas marcadas de una medida."""
    entidad = ENTIDADES.get(coleccion)
    return pd.DataFrame({"coleccion": NOMBRES_SALIDA.get(coleccion, coleccion.lower()), "fecha": df.loc[marca, "fecha"],
                         "entidad": df.loc[marca, entidad] if entidad else "", "medida": medida, **campos})


def aplicar_validez(df, coleccion, medidas):
    """Pasa a nulo las medidas negativas y los porcentajes fuera de 0-100, y los anota como incidentes."""
    invalidos = {}
    for col in medidas:
        tope = 100 if col == "volumen_util_diario_pct" else float("inf")
        invalidos[col] = (df[col] < 0) | (df[col] > tope)
        regla = "entre 0 y 100" if tope == 100 else ">= 0"
        # Se anota antes de borrar para conservar el valor original
        INCIDENTES.append(bitacora(coleccion, df, invalidos[col], col, valor_original=df.loc[invalidos[col], col],
                                   regla=regla))
        df.loc[invalidos[col], col] = float("nan")
    return invalidos


def imputar_celdas(coleccion, df, marca, medida, nuevos, metodo):
    """Pone los valores nuevos en las celdas marcadas (alineando por índice) y anota cada una en la bitácora."""
    df.loc[marca, medida] = nuevos
    IMPUTACIONES.append(bitacora(coleccion, df, marca, medida, valor_imputado=df.loc[marca, medida],
                                 metodo=metodo, n_celdas=1))


def imputar_demanda(df):
    """Importaciones y exportaciones nulas pasan a 0 (sin flujo); generación nula toma el día anterior."""
    for col in ["importaciones_kwh", "exportaciones_kwh"]:
        imputar_celdas("Demanda", df, df[col].isna(), col, 0, "cero_sin_flujo")
    # ffill sobre la serie ordenada por fecha; al asignar se alinea por índice y las filas no cambian de orden
    dia_anterior = df.sort_values("fecha")["generacion_kwh"].ffill()
    imputar_celdas("Demanda", df, df["generacion_kwh"].isna(), "generacion_kwh", dia_anterior, "dia_anterior")


def imputar_generacion(df):
    """Interpola cada hora nula con sus vecinas de la misma fila, solo en filas con una única hora nula."""
    nulas = df[HORAS].isna()
    por_fila = nulas.sum(axis=1)
    print(f"  generacion: máximo de horas nulas en una fila = {por_fila.max()}; "
          f"filas con más de 1 hora nula (no se imputan): {(por_fila > 1).sum()}")
    filas = por_fila == 1
    # limit_direction="both" hace que hora_00 u hora_23 copien a su única hora vecina
    interpoladas = df.loc[filas, HORAS].interpolate(axis=1, limit_direction="both")
    for h in HORAS:
        imputar_celdas("Generacion", df, nulas[h] & filas, h, interpoladas[h], "interpolacion_horaria")


def imputar_compras(df):
    """Horas nulas de compras pasan a 0: en 2026 "sin compra" viene vacío y en 2022-2025 viene como 0."""
    por_anio = df[HORAS].isna().sum(axis=1).groupby(df["anio_archivo"]).sum()
    df[HORAS] = df[HORAS].fillna(0)
    # Una fila de bitácora por año (no por celda): son cientos de miles de celdas con la misma causa
    for n in por_anio[por_anio > 0]:
        IMPUTACIONES.append(pd.DataFrame([{"coleccion": "compras_bolsa", "fecha": "", "entidad": "",
                                           "medida": "hora_00..hora_23", "valor_imputado": 0,
                                           "metodo": "cero_sin_compra", "n_celdas": int(n)}]))
    print(f"  compras_bolsa: {int(por_anio.sum())} celdas nulas pasaron a 0 (por año: {por_anio.to_dict()})")


def imputar_aportes(df, invalidos):
    """Rehace la energía invalidada como caudal x mediana de energía/caudal de los demás meses del río."""
    energia, caudal = "aportes_energia_kwh", "aportes_caudal_m3_s"
    for idx in df.index[invalidos[energia]]:
        rio = df.at[idx, "nombre_rio"]
        otros = df[(df["nombre_rio"] == rio) & (df.index != idx) & (df[energia] > 0) & (df[caudal] > 0)]
        cociente = otros[energia] / otros[caudal]
        cv = cociente.std() / cociente.mean()  # coeficiente de variación: dispersión relativa del cociente
        print(f"  {rio} {df.at[idx, 'fecha'].date()}: energía/caudal en {len(cociente)} meses -> mín {cociente.min():.2f}"
              f" | mediana {cociente.median():.2f} | máx {cociente.max():.2f} | CV {cv:.4f}")
        if cv > CV_MAXIMO:
            print(f"  AVISO: CV > {CV_MAXIMO}: no se imputa, {rio} queda en nulo")
        else:
            imputar_celdas("Aportes", df, df.index == idx, energia, df[caudal] * cociente.median(), "proporcion_caudal")


def imputar(df, coleccion, invalidos):
    """Aplica la imputación acordada para la colección; las demás colecciones no se imputan."""
    if coleccion == "Demanda":
        imputar_demanda(df)
    elif coleccion == "Generacion":
        imputar_generacion(df)
    elif coleccion == "Aportes":
        imputar_aportes(df, invalidos)
    elif coleccion == "Precio":
        imputar_compras(df)


def guardar_bitacoras(dir_calidad):
    """Escribe los CSV de incidentes e imputaciones en dir_calidad, sobrescribiendo los anteriores."""
    # Bitácoras: se sobrescriben en cada corrida; los bloques vacíos se omiten al unir
    dir_calidad.mkdir(parents=True, exist_ok=True)
    base = ["coleccion", "fecha", "entidad", "medida"]
    for filas, extra, archivo in [(INCIDENTES, ["valor_original", "regla"], "incidentes_validez.csv"),
                                  (IMPUTACIONES, ["valor_imputado", "metodo", "n_celdas"], "imputaciones.csv")]:
        tabla = pd.concat([f for f in filas if len(f)] or [pd.DataFrame(columns=base + extra)], ignore_index=True)
        tabla[base + extra].to_csv(dir_calidad / archivo, index=False)
