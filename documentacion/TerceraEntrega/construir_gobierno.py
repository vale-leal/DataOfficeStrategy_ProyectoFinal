"""Arma los 7 Excel de la plantilla S2_Plantilla_Gobierno (uno por tabla de XM) con la parte medible.

    python construir_gobierno.py PLANTILLA CONSOLIDADOS METRICAS SALIDA

PLANTILLA     S2_Plantilla_Gobierno.xlsx de la docente.
CONSOLIDADOS  carpeta con los .pkl que genera consolidar.py (35 Excel crudos -> 7 tablas, sin cambiar valores).
METRICAS      metricas_calidad_grandes.csv que genera calidad_tablas_grandes.py.
SALIDA        carpeta donde quedan los 7 archivos S2_Gobierno_EquipoX_DSxx_*.xlsx.

Qué llena el script:
  - DS-01 a DS-04 (pequeñas): los datos completos en 4_Datos y, en 1_Calidad, las reglas como fórmulas de Excel.
  - DS-05 a DS-07 (grandes): no caben o no calculan en Excel; en 1_Calidad van los conteos del CSV y 4_Datos
    guarda la evidencia (una fila por regla).
  El % y el semáforo son las fórmulas originales de la plantilla.
Qué NO llena (se escribe a mano): causa y acción de 1_Calidad (columnas J y K), 2_Seguridad y 3_Maestros.
"""
import datetime as dt
import sys

import openpyxl
import pandas as pd
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

PLANTILLA, CONS, METRICAS, SALIDA = sys.argv[1:5]
DESCARGA = dt.datetime(2026, 9, 28)
EQUIPO = "Sara Rúa García · Rafael José Gutiérrez Realpe · Valentina Leal Noreña · Paula Andrea Olier Alba"
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO",
         "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
REGIONES = ["ANTIOQUIA", "CALDAS", "CARIBE", "CENTRO", "ORIENTE", "RIOS ESTIMADOS", "VALLE"]
HORAS = [str(h) for h in range(24)]
D = "'4_Datos'!"
NEGRITA = Font(name="Arial", size=10, bold=True)
# Columna que evalúa cada regla de las tablas grandes (la plantilla exige llenarla para mostrar el semáforo)
COLUMNAS = {"GN-01": "cant_generacion_kwh (24 horas)", "GN-02a": "nom_tipo_generacion", "GN-02b": "cant_generacion_kwh (24 horas)",
            "GN-04": "Suma diaria de cant_generacion_kwh", "GN-03": "fec_generacion + nom_recurso + cod_agente + nom_version + nom_combustible",
            "CP-01": "Los 9 campos", "CP-02a": "ind_es_menor", "CP-02b": "cant_capacidad_efectiva_neta_kw",
            "CP-04": "cant_capacidad_efectiva_neta_kw vs. generación (DS-05)", "CP-03": "fec_capacidad + nom_recurso + cod_agente",
            "B-04": "cant_compras_kwh (24 horas)", "B-03": "cant_compras_kwh (24 horas)", "B-05 (propuesta)": "Estructura del archivo",
            "B-02": "fec_compra + cod_agente + nom_version"}  # G-05 y G-02 evalúan la fecha


def miles(n):
    return f"{n:,}".replace(",", ".")


def rango(L):
    """Devuelve una función que da el rango de una columna de 4_Datos (filas 4 a L)."""
    return lambda c: f"{D}${c}$4:${c}${L}"


def leer(nombre, ordenar=True):
    """Carga un consolidado; las tablas con fecha se ordenan por fecha."""
    df = pd.read_pickle(f"{CONS}/{nombre}.pkl")
    if ordenar:
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df = df.sort_values("Fecha").reset_index(drop=True)
    return df


def poner(celda, v):
    """Escribe un valor de pandas: vacío si es NaN, fecha con formato, número de Python."""
    if pd.isna(v):
        return
    v = v.to_pydatetime() if isinstance(v, pd.Timestamp) else (v.item() if hasattr(v, "item") else v)
    celda.value = v
    if isinstance(v, dt.datetime):
        celda.number_format = "yyyy-mm-dd"


def construir(archivo, ds, nombre, n, metodo, reglas, datos):
    """Copia la plantilla, llena instrucciones, reglas (B a F y meta) y 4_Datos, y la guarda."""
    wb = openpyxl.load_workbook(PLANTILLA)
    ins = wb["0_Instrucciones"]
    ins["B4"], ins["B5"] = "Equipo X  ← poner número de equipo", EQUIPO
    ins["B6"] = f"HidroData SIN · XM Sinergox · {ds} {nombre}. Capa raw (descarga del {DESCARGA:%d/%m/%Y}): {miles(n)} registros."
    q = wb["1_Calidad"]
    for r, regla in enumerate(reglas, start=6):
        for letra, v in zip("BCDEF", regla):
            q[f"{letra}{r}"] = v
        q[f"H{r}"] = 1  # meta del Plan: 100 % en todas las reglas
        q[f"E{r}"].number_format = q[f"F{r}"].number_format = "#,##0"
        q.row_dimensions[r].height = 45
    q["B14"] = metodo
    q["B14"].font = Font(name="Arial", size=9, italic=True, color="FF555555")
    datos(wb["4_Datos"])
    wb.save(f"{SALIDA}/S2_Gobierno_EquipoX_{ds.replace('-', '')}_{archivo}.xlsx")
    print("guardado", archivo)


def pequena(df, extras, anchos, refs):
    """4_Datos de una tabla pequeña: encabezado en la fila 3, datos desde la 4, auxiliares y listas de referencia a la derecha."""
    def llenar(d):
        for j, titulo in enumerate(list(df.columns) + [t for t, _ in extras], start=1):
            d.cell(3, j, titulo).font = NEGRITA
        for j, w in enumerate(anchos, start=1):
            d.column_dimensions[get_column_letter(j)].width = w
        for i, fila in enumerate(df.itertuples(index=False), start=4):
            for j, v in enumerate(fila, start=1):
                poner(d.cell(i, j), v)
            for j, (_, f) in enumerate(extras, start=len(df.columns) + 1):
                poner(d.cell(i, j), f(i, fila))
        for col, fila, titulo, valores, fmt in refs:
            d[f"{col}{fila}"] = titulo
            d[f"{col}{fila}"].font = NEGRITA
            for k, v in enumerate(valores, start=fila + 1):
                d[f"{col}{k}"] = v
                d[f"{col}{k}"].number_format = fmt or "General"
    return llenar


FORMULAS = "Reglas calculadas con fórmulas sobre 4_Datos (capa raw)."


# ----------------------------------------------------------------------------- tablas pequeñas
def aportes():
    ap = leer("aportes", ordenar=False).iloc[:, :10]
    A = rango(len(ap) + 3)
    reglas = [
        ("cant_aportes_energia_kwh", "Completitud", "0 vacíos en aportes en energía (A-01)", f'=COUNTA({A("D")})', f'=COUNT({A("E")})'),
        ("fec_mes", "Validez", "Mes dentro de los 12 meses en español (A-03)",
         f'=COUNTA({A("B")})', f'=SUMPRODUCT(COUNTIF({D}$M$4:$M$15,{A("B")}))'),
        ("cant_aportes_energia_kwh", "Exactitud", "Aportes en energía ≥ 0 kWh, sobre valores presentes (A-06)",
         f'=COUNT({A("E")})', f'=COUNTIF({A("E")},">=0")'),
        ("cant_aportes_caudal_m3s + cant_aportes_energia_kwh", "Consistencia", "Si el caudal es > 0, la energía está registrada (A-07)",
         f'=COUNTIF({A("F")},">0")', f'=COUNTIFS({A("F")},">0",{A("E")},"<>")'),
        ("fec_anio + fec_mes + nom_rio", "Unicidad", "Una sola fila por año, mes y río (A-05)",
         f'=COUNTA({A("K")})', f'=SUMPRODUCT((COUNTIF({A("K")},{A("K")})=1)*1)'),
        ("fec_anio + fec_mes", "Oportunidad", "Último mes publicado con 1 mes o menos de rezago frente a la descarga (G-05 mensual)",
         "=1", f'=IF((YEAR({D}$M$18)*12+MONTH({D}$M$18))-SUMPRODUCT(MAX({A("A")}*12+MATCH({A("B")},{D}$M$4:$M$15,0)))<=1,1,0)'),
    ]
    datos = pequena(ap, [("Clave año|mes|río (auxiliar)", lambda i, f: f'=A{i}&"|"&B{i}&"|"&D{i}')],
                    [7, 12, 18, 24, 18, 14, 20, 18, 18, 16, 32, 2, 30],
                    [("M", 3, "Meses válidos (referencia)", MESES, None), ("M", 17, "Fecha de descarga", [DESCARGA], "yyyy-mm-dd")])
    construir("Aportes", "DS-01", "Aportes hídricos mensuales por río", len(ap), FORMULAS, reglas, datos)


def reservas():
    rs = leer("reservas").iloc[:, :2]
    A = rango(len(rs) + 3)
    unica = f'=SUMPRODUCT((COUNTIF({A("A")},{A("A")})=1)*1)'
    reglas = [
        ("fec_reserva", "Completitud", "Un registro por cada día entre la primera y la última fecha (R-02)",
         f'=MAX({A("A")})-MIN({A("A")})+1', unica),
        ("fec_reserva", "Validez", "Fecha entre 01/01/2022 y la fecha de descarga, sin fechas futuras (R-03)",
         f'=COUNTA({A("A")})', f'=COUNTIFS({A("A")},">="&{D}$E$7,{A("A")},"<="&{D}$E$4)'),
        ("pct_volumen_util_diario", "Exactitud", "Valor entre 0 y 100 (R-04)",
         f'=COUNT({A("B")})', f'=COUNTIFS({A("B")},">=0",{A("B")},"<=100")'),
        ("pct_volumen_util_diario", "Consistencia", "Variación diaria de 5 puntos porcentuales o menos (R-05)",
         f'=COUNT({A("C")})', f'=COUNTIF({A("C")},"<=5")'),
        ("fec_reserva", "Unicidad", "Una fila por fecha (R-06)", f'=COUNTA({A("A")})', unica),
        ("fec_reserva", "Oportunidad", "Último día publicado con 2 días o menos de rezago frente a la descarga (G-05)",
         "=1", f'=IF({D}$E$4-MAX({A("A")})<=2,1,0)'),
    ]
    datos = pequena(rs, [("Variación diaria absoluta (pp, auxiliar)", lambda i, f: f"=ABS(B{i}-B{i-1})" if i > 4 else None)],
                    [12, 20, 26, 9, 30],
                    [("E", 3, "Fecha de descarga", [DESCARGA], "yyyy-mm-dd"),
                     ("E", 6, "Fecha mínima del periodo", [dt.datetime(2022, 1, 1)], "yyyy-mm-dd")])
    construir("Reservas", "DS-02", "Reserva útil diaria del SIN (%)", len(rs), FORMULAS, reglas, datos)


def vertimientos():
    vt = leer("vertimientos").sort_values(["Fecha", "Nombre Embalse"]).reset_index(drop=True).iloc[:, :5]
    L = len(vt) + 3
    A = rango(L)
    reglas = [
        ("Las 5 columnas", "Completitud", "0 vacíos en los registros publicados (V-04: no se exige una fila por día)",
         f'=COUNTA({A("A")})', f'=SUMPRODUCT(({A("B")}<>"")*({A("C")}<>"")*({A("D")}<>"")*({A("E")}<>""))'),
        ("nom_region_hidrologica", "Validez", "Región dentro de la lista de regiones de XM (V-05)",
         f'=COUNTA({A("B")})', f'=SUMPRODUCT(COUNTIF({D}$K$4:$K$10,{A("B")}))'),
        ("cant_vertimientos_volumen_miles_m3 + cant_vertimientos_energia_kwh", "Exactitud",
         "Volumen > 0 y energía > 0 (si hay fila, hubo vertimiento) (V-02)",
         f'=COUNTA({A("A")})', f'=COUNTIFS({A("D")},">0",{A("E")},">0")'),
        ("cant_vertimientos_energia_kwh ÷ volumen", "Consistencia",
         "La razón energía ÷ volumen está a ±1 % del promedio del mismo embalse y mes (V-03)",
         f'=COUNT({A("H")})', f'=COUNTIF({A("H")},"<=0.01")'),
        ("fec_vertimiento + nom_embalse", "Unicidad", "Una fila por fecha y embalse (V-01)",
         f'=COUNTA({A("I")})', f'=SUMPRODUCT((COUNTIF({A("I")},{A("I")})=1)*1)'),
        ("fec_vertimiento", "Oportunidad", "Último día publicado con 2 días o menos de rezago frente a la descarga (G-05)",
         "=1", f'=IF({D}$K$13-MAX({A("A")})<=2,1,0)'),
    ]
    extras = [("Razón energía ÷ volumen (auxiliar)", lambda i, f: f"=E{i}/D{i}"),
              ("Clave embalse|mes (auxiliar)", lambda i, f: f'=C{i}&"|"&YEAR(A{i})&"-"&MONTH(A{i})'),
              ("Desvío frente al promedio embalse-mes (auxiliar)",
               lambda i, f: f"=ABS(F{i}/AVERAGEIFS($F$4:$F${L},$G$4:$G${L},G{i})-1)"),
              ("Clave fecha|embalse (auxiliar)", lambda i, f: f'=A{i}&"|"&C{i}')]
    datos = pequena(vt, extras, [12, 16, 18, 20, 20, 18, 22, 22, 22, 2, 30],
                    [("K", 3, "Regiones válidas (referencia)", REGIONES, None), ("K", 12, "Fecha de descarga", [DESCARGA], "yyyy-mm-dd")])
    construir("Vertimientos", "DS-03", "Vertimientos diarios por embalse", len(vt), FORMULAS, reglas, datos)


def demanda():
    dm = leer("demanda").iloc[:, :6]
    g = leer("generacion", ordenar=False)  # generación sumada por día: no cabe en la hoja, se calcula aquí
    gen_dia = g[HORAS].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1).groupby(pd.to_datetime(g["Fecha"])).sum()
    A = rango(len(dm) + 3)
    reglas = [
        ("cant_demanda_energia_sin_kwh + cant_generacion_sin_kwh", "Completitud", "Demanda y generación registradas en todos los días (D-02)",
         f'=COUNTA({A("A")})', f'=COUNTIFS({A("B")},"<>",{A("C")},"<>")'),
        ("cant_demanda_energia_sin_kwh, demanda no atendida, exportaciones, importaciones", "Validez",
         "Demanda > 0; demanda no atendida, exportaciones e importaciones ≥ 0 (D-02)",
         f'=COUNTA({A("A")})', f'=SUMPRODUCT(({A("B")}>0)*({A("D")}>=0)*({A("E")}>=0)*({A("F")}>=0))'),
        ("cant_generacion_sin_kwh", "Exactitud", "La generación del día coincide con la suma de la tabla Generación (DS-05), ±0,1 % (GN-04)",
         f'=COUNT({A("H")})', f'=COUNTIF({A("H")},"<=0.001")'),
        ("Balance de energía", "Consistencia", "Demanda = Generación + Importaciones − Exportaciones + Demanda no atendida, diferencia ≤ 1 kWh (D-03)",
         f'=COUNT({A("I")})', f'=COUNTIF({A("I")},"<=1")'),
        ("fec_demanda", "Unicidad", "Una fila por fecha (D-04)",
         f'=COUNTA({A("A")})', f'=SUMPRODUCT((COUNTIF({A("A")},{A("A")})=1)*1)'),
        ("fec_demanda", "Oportunidad", "Último día publicado con 2 días o menos de rezago frente a la descarga (G-05)",
         "=1", f'=IF({D}$K$4-MAX({A("A")})<=2,1,0)'),
    ]
    extras = [("Generación sumada de DS-05 (auxiliar)", lambda i, f: gen_dia.get(f[0])),
              ("Diferencia relativa con DS-05 (auxiliar)", lambda i, f: f'=IF(OR(C{i}="",G{i}=""),"",ABS(C{i}/G{i}-1))'),
              ("Diferencia del balance kWh (auxiliar)", lambda i, f: f'=IF(C{i}="","",ABS(B{i}-(C{i}+F{i}-E{i}+D{i})))')]
    datos = pequena(dm, extras, [12, 22, 18, 18, 16, 16, 22, 20, 20, 2, 40],
                    [("K", 3, "Fecha de descarga", [DESCARGA], "yyyy-mm-dd")])
    construir("Demanda", "DS-04", "Demanda de energía del SIN", len(dm),
              FORMULAS + " La columna G (generación sumada de DS-05) se calcula en Python.", reglas, datos)


# ----------------------------------------------------------------------------- tablas grandes
def grande(tabla, archivo, ds, nombre):
    """Reglas desde el CSV de calidad_tablas_grandes.py; 4_Datos guarda una fila de evidencia por regla."""
    m = pd.read_csv(METRICAS, encoding="utf-8-sig")
    m = m[m["tabla"] == tabla]
    reglas = [(COLUMNAS.get(r.regla, "fecha"), r.dimension, f"{r.descripcion} ({r.regla})", int(r.evaluados), int(r.cumplen))
              for r in m.itertuples()]
    evidencia = [("Regla", "Dimensión", "Descripción", "Evaluados", "Cumplen", "%", "Detalle")] + [
        (r.regla, r.dimension, r.descripcion, int(r.evaluados), int(r.cumplen), r.pct / 100,
         r.detalle if isinstance(r.detalle, str) else "") for r in m.itertuples()]
    n = int(m["evaluados"].iloc[0])  # la primera regla (completitud) evalúa todas las filas

    def datos(d):
        d["A1"] = f"Esta tabla no se pega aquí ({miles(n)} filas): las reglas se midieron en Python sobre el archivo completo. Abajo queda la evidencia."
        d["A2"] = "Script: calidad_tablas_grandes.py → metricas_calidad_grandes.csv (una fila por regla). Capa medida: raw."
        for i, fila in enumerate(evidencia, start=3):
            for j, v in enumerate(fila, start=1):
                c = d.cell(i, j, v)
                c.font = Font(name="Arial", size=10, bold=(i == 3))
                if i > 3 and isinstance(v, int):
                    c.number_format = "#,##0"
                elif isinstance(v, float):
                    c.number_format = "0.00%"
        for col, w in zip("ABCDEFG", [18, 14, 60, 12, 12, 9, 90]):
            d.column_dimensions[col].width = w

    construir(archivo, ds, nombre, n, "Conteos medidos en Python (calidad_tablas_grandes.py) sobre la capa raw; el detalle por regla está en 4_Datos. "
              "% y semáforo: fórmulas de la plantilla.", reglas, datos)


aportes(); reservas(); vertimientos(); demanda()
grande("generacion", "Generacion", "DS-05", "Generación real por recurso y hora")
grande("capacidad", "Capacidad", "DS-06", "Capacidad efectiva neta por recurso")
grande("compras_bolsa", "ComprasBolsa", "DS-07", "Compras en bolsa nacional por agente y hora")
