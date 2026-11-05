"""Genera el modelo ArchiMate v1.0 de HidroData SIN desde una sola especificación.

    python documentacion/BPMNyArchiMate/fuente/generar_archimate.py

Salidas (en documentacion/BPMNyArchiMate/):
  - HidroData_ArchiMate_v1.archimate  modelo editable (abrir con Archi: File > Open)
  - ArchiMate_HidroData_v1.svg        vista por capas
  - ArchiMate_HidroData_v1.png        la misma vista en PNG (requiere playwright + chromium)

Para cambiar el diagrama se edita ELEMENTOS / RELACIONES / VISTA y se vuelve a correr.
"""
import html
import re
import uuid
from pathlib import Path

SALIDA = Path(__file__).resolve().parents[1]
NOMBRE = "HidroData SIN · ArchiMate v1.0"
# Herramienta del dashboard: se ajusta cuando el equipo la confirme (aparece en la capa de tecnología)
DASHBOARD_TECH = "Herramienta del dashboard"

# ---------------------------------------------------------------- elementos
# clave: (tipo Archi, nombre, documentación)
ELEMENTOS = {
    # Negocio
    "A_PLA": ("BusinessActor", "Planeación Energética", "Área de negocio dueña del significado del dato y de los umbrales (spoke del Data Office federado)."),
    "A_DO": ("BusinessActor", "Data Office (CDO)", "Unidad staff de la Gerencia General; define políticas, estándares, calidad y arquitectura (hub)."),
    "A_COM": ("BusinessActor", "Comité de Riesgo Hídrico", "Presidido por el Gerente de Energía; decide acciones ante una alerta y registra la decisión."),
    "R_OWN": ("BusinessRole", "Data Owner", "Jefatura de Planeación Energética. Aprueba definiciones, reglas, clasificación y umbrales (RACI: A)."),
    "R_ANA": ("BusinessRole", "Analista de datos", "Consumidor del dato: construye indicadores y publica el dashboard."),
    "R_STE": ("BusinessRole", "Data Steward", "Significado y calidad diaria del dato: catálogo, diccionario, reglas e incidentes."),
    "R_CUS": ("BusinessRole", "Custodio técnico", "Implementa y opera el pipeline, el almacenamiento, el linaje y los accesos."),
    "P": ("BusinessProcess", "Monitoreo y alerta de reservas hídricas", "Proceso TO-BE del BPMN (mejoras M1 a M6)."),
    "P1": ("BusinessProcess", "Obtener y validar datos (M1–M3)", "Descarga de Sinergox, validación de reglas de calidad y revisión de incidentes por el Data Steward."),
    "P2": ("BusinessProcess", "Calcular indicadores y publicar dashboard (M4)", "Indicadores diarios y mensuales, linaje y publicación del dashboard."),
    "P3": ("BusinessProcess", "Enviar alerta por umbral (M5)", "Si el volumen útil cruza el umbral aprobado, se envía la alerta por correo."),
    "P4": ("BusinessProcess", "Decidir y registrar la decisión (M6)", "El comité analiza la alerta en el dashboard, decide y deja constancia."),
    "S_INFO": ("BusinessService", "Información hídrica diaria validada", "Estado de reservas, aportes y generación con calidad medida."),
    "S_ALE": ("BusinessService", "Alerta de riesgo hídrico", "Aviso oportuno cuando se superan los umbrales aprobados."),
    "BO_PLAN": ("BusinessObject", "Plan de Gobierno de Datos", "Políticas, RACI, catálogo, reglas de calidad, linaje, clasificación y acceso."),
    "BO_UMB": ("BusinessObject", "Umbrales de riesgo aprobados", "Vigilancia 50 % y crítico 40 % del volumen útil (propuestos por el EDA, aprueba el Data Owner)."),
    "BO_REG": ("BusinessObject", "Registro de decisiones", "Constancia de cada decisión del comité con los datos que la motivaron (O4)."),
    # Aplicación
    "AC_PIPE": ("ApplicationComponent", "Pipeline HidroData (run_pipeline.py)", "Orquesta ingesta, normalización y limpieza, y calidad."),
    "AC_ING": ("ApplicationComponent", "Ingesta (src/ingesta.py)", "Une los .xlsx anuales por colección y guarda un parquet por colección."),
    "AC_NOR": ("ApplicationComponent", "Normalización y limpieza (normalizacion.py, limpieza.py)", "Tipos, nombres, validez e imputaciones con bitácora."),
    "AC_CAL": ("ApplicationComponent", "Calidad (src/calidad.py)", "Métricas de completitud, unicidad, validez y cobertura por colección."),
    "AC_EDA": ("ApplicationComponent", "Notebook EDA (04_eda.ipynb)", "Análisis exploratorio; produce los indicadores mensuales y la tabla de alerta."),
    "AC_DASH": ("ApplicationComponent", "Dashboard HidroData", "Visualización para la toma de decisiones del comité."),
    "AC_PA": ("ApplicationComponent", "Flujo de alerta (Power Automate)", "Lee el estado más reciente de TablaReservas y envía el correo de alerta."),
    "AC_GOB": ("ApplicationComponent", "Medición de reglas de gobierno (scripts + Excel S2)", "construir_gobierno.py, calidad_tablas_grandes.py y los 7 Excel de gobierno."),
    "AS_CAL": ("ApplicationService", "Reporte de calidad del dato", "Resultado de las reglas por dataset con semáforo."),
    "AS_DAT": ("ApplicationService", "Datos normalizados y validados", "Siete colecciones de XM limpias y con tipos estándar."),
    "AS_VIS": ("ApplicationService", "Visualización de indicadores", "Consulta del estado hídrico y de la calidad en el dashboard."),
    "AS_NOT": ("ApplicationService", "Notificación de alerta", "Envío automático del correo de alerta al comité."),
    "DO_RAW": ("DataObject", "Datos crudos XM (7 colecciones .xlsx)", "DS-01 a DS-07, 2022–2026, tal como se descargan de Sinergox."),
    "DO_NORM": ("DataObject", "Datos normalizados (.parquet)", "data/processed/normalizado: una tabla por colección."),
    "DO_CALQ": ("DataObject", "Bitácoras y métricas de calidad", "data/processed/calidad: métricas, incidentes e imputaciones."),
    "DO_IND": ("DataObject", "Indicadores mensuales (eda_mensual)", "data/processed/eda/eda_mensual.parquet: insumo del dashboard."),
    "DO_ALE": ("DataObject", "Tabla de alerta (TablaReservas)", "Fecha, volumen útil, variación 30 días, umbrales y estado."),
    "DO_CAT": ("DataObject", "Catálogo, diccionario y scorecard de calidad", "Excel S2 de gobierno por dataset (DS-01 a DS-07)."),
    # Tecnología
    "N_XM": ("Node", "XM Sinergox (externo)", "Portal de información del mercado mayorista. La descarga hoy es manual."),
    "TS_EXP": ("TechnologyService", "Exportación de históricos (.xlsx)", "Descarga anual por colección desde sinergox.xm.com.co."),
    "N_PC": ("Node", "Estación de trabajo del equipo", "Equipo local donde corre el pipeline y los notebooks."),
    "SS_PY": ("SystemSoftware", "Python 3.10–3.12 · pandas · pyarrow", "Entorno definido en requirements.txt."),
    "SS_JUP": ("SystemSoftware", "JupyterLab", "Ejecución de los notebooks."),
    "SS_DASH": ("SystemSoftware", DASHBOARD_TECH, "Plataforma donde se construye y publica el dashboard."),
    "AR_PQ": ("Artifact", "data/processed/*.parquet", "Salidas del pipeline y del EDA (no se versionan)."),
    "N_GH": ("Node", "GitHub · repositorio + Git LFS", "vale-leal/DataOfficeStrategy_ProyectoFinal: control de versiones y revisión por PR."),
    "AR_SRC": ("Artifact", "run_pipeline.py · src/ · notebooks/", "Código fuente versionado del pipeline y del análisis."),
    "AR_RAR": ("Artifact", "HidrologiaYGeneracionEnergetica_7065.rar", "35 .xlsx crudos (Git LFS); evidencia de la extracción."),
    "N_M365": ("Node", "Microsoft 365 (nube)", "Licencia institucional."),
    "SS_PA": ("SystemSoftware", "Power Automate", "Ejecuta el flujo programado de alerta."),
    "SS_OUT": ("SystemSoftware", "Outlook", "Envío del correo de alerta."),
    "AR_XLSX": ("Artifact", "reservas_alerta.xlsx (OneDrive)", "Archivo que genera el EDA y lee el flujo."),
}

# ---------------------------------------------------------------- relaciones
# (clave, tipo, origen, destino, extra)  extra: {"acceso": "read"|"write", "nombre": str}
RELACIONES = [
    # Negocio
    ("r01", "Assignment", "A_PLA", "R_OWN", {}), ("r02", "Assignment", "A_PLA", "R_ANA", {}),
    ("r03", "Assignment", "A_DO", "R_STE", {}), ("r04", "Assignment", "A_DO", "R_CUS", {}),
    ("r05", "Assignment", "R_STE", "P1", {}), ("r06", "Assignment", "R_CUS", "P1", {}),
    ("r07", "Assignment", "R_ANA", "P2", {}), ("r08", "Assignment", "A_COM", "P4", {}),
    ("r09", "Association", "R_OWN", "BO_UMB", {"nombre": "aprueba"}),
    ("r10", "Composition", "P", "P1", {}), ("r11", "Composition", "P", "P2", {}),
    ("r12", "Composition", "P", "P3", {}), ("r13", "Composition", "P", "P4", {}),
    ("r14", "Triggering", "P1", "P2", {}), ("r15", "Triggering", "P2", "P3", {}), ("r16", "Triggering", "P3", "P4", {}),
    ("r17", "Access", "P1", "BO_PLAN", {"acceso": "read"}), ("r18", "Access", "P3", "BO_UMB", {"acceso": "read"}),
    ("r19", "Access", "P4", "BO_REG", {"acceso": "write"}),
    ("r20", "Realization", "P", "S_INFO", {}), ("r21", "Realization", "P", "S_ALE", {}),
    ("r22", "Serving", "S_INFO", "A_COM", {}), ("r23", "Serving", "S_ALE", "A_COM", {}),
    # Aplicación
    ("r30", "Composition", "AC_PIPE", "AC_ING", {}), ("r31", "Composition", "AC_PIPE", "AC_NOR", {}),
    ("r32", "Composition", "AC_PIPE", "AC_CAL", {}),
    ("r33", "Flow", "AC_ING", "AC_NOR", {}), ("r34", "Flow", "AC_NOR", "AC_CAL", {}),
    ("r35", "Realization", "AC_PIPE", "AS_DAT", {}), ("r36", "Realization", "AC_CAL", "AS_CAL", {}),
    ("r37", "Realization", "AC_GOB", "AS_CAL", {}), ("r38", "Realization", "AC_DASH", "AS_VIS", {}),
    ("r39", "Realization", "AC_PA", "AS_NOT", {}),
    ("r40", "Serving", "AS_DAT", "P1", {}), ("r41", "Serving", "AS_CAL", "P1", {}),
    ("r42", "Serving", "AS_VIS", "P2", {}), ("r43", "Serving", "AS_VIS", "P4", {}), ("r44", "Serving", "AS_NOT", "P3", {}),
    ("r45", "Access", "AC_ING", "DO_RAW", {"acceso": "read"}), ("r46", "Access", "AC_NOR", "DO_NORM", {"acceso": "write"}),
    ("r47", "Access", "AC_CAL", "DO_CALQ", {"acceso": "write"}), ("r48", "Access", "AC_EDA", "DO_NORM", {"acceso": "read"}),
    ("r49", "Access", "AC_EDA", "DO_IND", {"acceso": "write"}), ("r50", "Access", "AC_EDA", "DO_ALE", {"acceso": "write"}),
    ("r51", "Access", "AC_DASH", "DO_IND", {"acceso": "read"}), ("r52", "Access", "AC_DASH", "DO_CALQ", {"acceso": "read"}),
    ("r53", "Access", "AC_PA", "DO_ALE", {"acceso": "read"}), ("r54", "Access", "AC_GOB", "DO_CAT", {"acceso": "write"}),
    ("r55", "Access", "AC_GOB", "DO_RAW", {"acceso": "read"}),
    ("r56", "Realization", "DO_ALE", "BO_UMB", {}),          # las columnas de umbral materializan los umbrales aprobados
    ("r57", "Realization", "DO_CAT", "BO_PLAN", {}),         # el Excel S2 materializa catálogo, diccionario y reglas
    # Tecnología
    ("r60", "Realization", "N_XM", "TS_EXP", {}),
    ("r61", "Composition", "N_PC", "SS_PY", {}), ("r62", "Composition", "N_PC", "SS_JUP", {}),
    ("r63", "Composition", "N_PC", "SS_DASH", {}), ("r64", "Assignment", "N_PC", "AR_PQ", {}),
    ("r65", "Assignment", "N_GH", "AR_SRC", {}), ("r66", "Assignment", "N_GH", "AR_RAR", {}),
    ("r67", "Composition", "N_M365", "SS_PA", {}), ("r68", "Composition", "N_M365", "SS_OUT", {}),
    ("r69", "Assignment", "N_M365", "AR_XLSX", {}),
    ("r70", "Access", "TS_EXP", "AR_RAR", {"acceso": "write"}),
    ("r71", "Serving", "SS_PY", "AC_PIPE", {}), ("r72", "Serving", "SS_JUP", "AC_EDA", {}),
    ("r73", "Serving", "SS_DASH", "AC_DASH", {}), ("r74", "Serving", "SS_PA", "AC_PA", {}),
    ("r75", "Serving", "SS_OUT", "AC_PA", {}), ("r76", "Serving", "SS_PY", "AC_GOB", {}),
    ("r77", "Realization", "AR_RAR", "DO_RAW", {}), ("r78", "Realization", "AR_PQ", "DO_NORM", {}),
    ("r79", "Realization", "AR_XLSX", "DO_ALE", {}), ("r80", "Realization", "AR_SRC", "AC_PIPE", {}),
    ("r81", "Realization", "AR_SRC", "AC_EDA", {}),
]

# ---------------------------------------------------------------- vista
# Grupos de capa (x, y, w, h) y cajas en coordenadas absolutas. "dentro" = caja contenedora.
CAPAS = [
    ("Capa de negocio", (10, 10, 1540, 295), "#fffbe0", "#c9b64a"),
    ("Capa de aplicación", (10, 320, 1540, 365), "#e8fafa", "#4aa7b0"),
    ("Capa de tecnología", (10, 725, 1540, 270), "#eef7e9", "#6fa35a"),
]
CAJAS = {
    "R_OWN": (215, 38, 150, 48), "R_ANA": (215, 96, 150, 48), "R_STE": (215, 176, 150, 48), "R_CUS": (215, 236, 150, 48),
    "A_PLA": (30, 63, 160, 56), "A_DO": (30, 202, 160, 56),
    "P": (400, 105, 880, 135),
    "P1": (415, 150, 200, 62, "P"), "P2": (630, 150, 200, 62, "P"), "P3": (845, 150, 200, 62, "P"), "P4": (1060, 150, 200, 62, "P"),
    "BO_PLAN": (415, 38, 200, 48), "BO_UMB": (845, 38, 200, 48), "BO_REG": (1060, 38, 200, 48),
    "S_INFO": (1320, 105, 205, 52), "S_ALE": (1320, 172, 205, 52), "A_COM": (1320, 240, 205, 52),
    "AS_CAL": (200, 340, 190, 50), "AS_DAT": (415, 340, 200, 50), "AS_VIS": (630, 340, 190, 50), "AS_NOT": (855, 340, 190, 50),
    "AC_PIPE": (30, 418, 565, 118),
    "AC_ING": (45, 460, 165, 62, "AC_PIPE"), "AC_NOR": (222, 460, 185, 62, "AC_PIPE"), "AC_CAL": (420, 460, 160, 62, "AC_PIPE"),
    "AC_DASH": (630, 445, 190, 62), "AC_PA": (855, 445, 190, 62), "AC_EDA": (1065, 445, 200, 62), "AC_GOB": (1300, 445, 225, 62),
    "DO_RAW": (40, 590, 170, 55), "DO_NORM": (240, 590, 175, 55), "DO_CALQ": (440, 590, 175, 55),
    "DO_IND": (650, 590, 170, 55), "DO_ALE": (865, 590, 170, 55), "DO_CAT": (1300, 590, 225, 55),
    "N_XM": (30, 760, 225, 115), "TS_EXP": (45, 805, 195, 55, "N_XM"),
    "N_PC": (285, 750, 530, 185),
    "SS_PY": (300, 795, 225, 55, "N_PC"), "SS_JUP": (540, 795, 120, 55, "N_PC"), "SS_DASH": (675, 795, 125, 55, "N_PC"),
    "AR_PQ": (300, 862, 225, 50, "N_PC"),
    "N_GH": (845, 750, 330, 185), "AR_SRC": (860, 795, 300, 50, "N_GH"), "AR_RAR": (860, 862, 300, 50, "N_GH"),
    "N_M365": (1200, 750, 335, 185),
    "SS_PA": (1215, 795, 150, 55, "N_M365"), "SS_OUT": (1375, 795, 145, 55, "N_M365"),
    "AR_XLSX": (1215, 862, 305, 50, "N_M365"),
}
# Conexiones visibles: relación -> puntos de quiebre absolutos (lista vacía = recta).
# Las relaciones que no aparecen aquí quedan en el modelo pero no se dibujan (p. ej. anidamientos).
CONEXIONES = {
    "r01": [], "r02": [], "r03": [], "r04": [],
    "r05": [], "r06": [], "r07": [(300, 136), (730, 136)], "r08": [(1215, 266)],
    "r09": [(290, 24), (945, 24)],
    "r14": [], "r15": [], "r16": [],
    "r17": [], "r18": [], "r19": [],
    "r20": [], "r21": [], "r22": [(1538, 131), (1538, 266)], "r23": [],
    "r33": [], "r34": [],
    "r35": [(515, 404)], "r36": [], "r37": [(1412, 412), (295, 412)], "r38": [], "r39": [],
    "r40": [], "r41": [], "r42": [], "r43": [(760, 312), (1130, 312)], "r44": [],
    "r45": [], "r46": [], "r47": [],
    "r48": [(1165, 565), (327, 565)], "r49": [], "r50": [],
    "r51": [], "r52": [], "r53": [], "r54": [],
    "r70": [(142, 960), (1010, 960)],
    "r71": [(412, 705), (225, 705), (225, 550)], "r72": [(600, 693), (1165, 693)],
    "r73": [(737, 714), (838, 714), (838, 476)], "r74": [(1290, 705), (1055, 705), (1055, 476)],
}
NOTA = ("Vista por capas v1.0 (noviembre 2026). Refleja lo implementado: descarga manual desde Sinergox, pipeline en Python, "
        "EDA, Excel de gobierno y alerta con Power Automate. Las relaciones de linaje artefacto → dato y dato → objeto de negocio "
        "están en el modelo (.archimate) y en 05_arquitectura_archimate.md.")

# ---------------------------------------------------------------- utilidades geométricas
def caja(k):
    b = CAJAS[k]
    return b[0], b[1], b[2], b[3]


def centro(k):
    x, y, w, h = caja(k)
    return x + w / 2, y + h / 2


def recorte(k, desde, hacia):
    """Punto donde la recta desde el centro de k hacia 'hacia' cruza el borde de la caja (anclaje chopbox)."""
    x, y, w, h = caja(k)
    cx, cy = desde
    dx, dy = hacia[0] - cx, hacia[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    ts = []
    if dx:
        ts += [((x - cx) / dx), ((x + w - cx) / dx)]
    if dy:
        ts += [((y - cy) / dy), ((y + h - cy) / dy)]
    t = min(t for t in ts if t > 0)
    return cx + dx * t, cy + dy * t


def ruta(rid):
    _, _, a, b, _ = REL[rid]
    pts = CONEXIONES[rid]
    ca, cb = centro(a), centro(b)
    p0 = recorte(a, ca, pts[0] if pts else cb)
    p1 = recorte(b, cb, pts[-1] if pts else ca)
    return [p0, *pts, p1]


REL = {r[0]: r for r in RELACIONES}

# ---------------------------------------------------------------- SVG
CAPA_COLOR = {"Business": "#ffffb5", "Application": "#b5ffff", "Technology": "#c9e7b7", "Node": "#c9e7b7",
              "SystemSoftware": "#c9e7b7", "Artifact": "#c9e7b7", "Data": "#b5ffff"}


def color(tipo):
    if tipo.startswith("Business"):
        return "#ffffb5"
    if tipo.startswith("Application") or tipo == "DataObject":
        return "#b5ffff"
    return "#c9e7b7"


def envolver(texto, ancho_px, px=6.1):
    maxc = max(8, int(ancho_px / px))
    lineas, actual = [], ""
    for palabra in texto.split():
        if len(actual) + len(palabra) + 1 > maxc and actual:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    lineas.append(actual)
    return lineas


def icono(tipo, x, y):
    """Ícono ArchiMate en la esquina superior derecha (x, y = esquina del área del ícono)."""
    s = 'fill="none" stroke="#222" stroke-width="1"'
    if tipo == "BusinessActor":
        return (f'<circle cx="{x+7}" cy="{y+3}" r="2.6" {s}/><path d="M{x+7} {y+5.6}v6 M{x+2} {y+8}h10 '
                f'M{x+7} {y+11.6}l-4 4.5 M{x+7} {y+11.6}l4 4.5" {s}/>')
    if tipo == "BusinessRole":
        return (f'<path d="M{x+3} {y+3}h9 M{x+3} {y+11}h9" {s}/><ellipse cx="{x+3}" cy="{y+7}" rx="2.4" ry="4" {s}/>'
                f'<ellipse cx="{x+12}" cy="{y+7}" rx="2.4" ry="4" {s}/>')
    if tipo == "BusinessProcess":
        return f'<path d="M{x} {y+5}h9v-3l6 5-6 5v-3h-9z" {s}/>'
    if tipo in ("BusinessService", "ApplicationService", "TechnologyService"):
        return f'<rect x="{x}" y="{y+2}" width="15" height="9" rx="4.5" {s}/>'
    if tipo == "ApplicationComponent":
        return (f'<rect x="{x+3}" y="{y}" width="12" height="14" {s}/><rect x="{x}" y="{y+3}" width="6" height="3" '
                f'fill="{color(tipo)}" stroke="#222"/><rect x="{x}" y="{y+8}" width="6" height="3" fill="{color(tipo)}" stroke="#222"/>')
    if tipo == "SystemSoftware":
        return f'<circle cx="{x+8}" cy="{y+7}" r="5.5" {s}/><path d="M{x+6} {y+2.2}a5.5 5.5 0 0 1 7.3 6.6" {s}/>'
    if tipo == "Artifact":
        return f'<path d="M{x+2} {y}h7l4 4v10h-11z M{x+9} {y}v4h4" {s}/>'
    if tipo == "Node":
        return f'<path d="M{x} {y+4}h11v10h-11z M{x} {y+4}l3-3h11l-3 3 M{x+14} {y+1}v10l-3 3" {s}/>'
    return ""


def svg_caja(k, contenedor=False):
    tipo, nombre, _ = ELEMENTOS[k]
    x, y, w, h = caja(k)
    fill = color(tipo)
    partes = []
    if tipo == "Node":
        d = 10
        partes.append(f'<polygon points="{x},{y+d} {x+d},{y} {x+w},{y} {x+w-d},{y+d}" fill="#b3d39f" stroke="#555"/>'
                      f'<polygon points="{x+w-d},{y+d} {x+w},{y} {x+w},{y+h-d} {x+w-d},{y+h}" fill="#a6c98f" stroke="#555"/>'
                      f'<rect x="{x}" y="{y+d}" width="{w-d}" height="{h-d}" fill="{fill}" stroke="#555"/>')
        x, y, w, h = x, y + d, w - d, h - d
    elif tipo in ("BusinessService", "ApplicationService", "TechnologyService"):
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(h/2, 22)}" fill="{fill}" stroke="#555"/>')
    elif tipo == "BusinessProcess" and not contenedor:
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="#555"/>')
    elif tipo in ("BusinessObject", "DataObject"):
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#555"/>'
                      f'<line x1="{x}" y1="{y+11}" x2="{x+w}" y2="{y+11}" stroke="#555"/>')
    else:
        rx = 9 if tipo == "BusinessProcess" else 0
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#555"/>')
    if tipo not in ("BusinessObject", "DataObject"):
        partes.append(icono(tipo, x + w - 20, y + 5))
    if contenedor:
        partes.append(f'<text x="{x+10}" y="{y+18}" class="t b">{html.escape(nombre)}</text>')
    else:
        lineas = envolver(nombre, w - (16 if tipo in ("BusinessObject", "DataObject") else 30))
        y0 = y + h / 2 - (len(lineas) - 1) * 7 + (5 if tipo in ("BusinessObject", "DataObject") else 4)
        for i, ln in enumerate(lineas):
            partes.append(f'<text x="{x + w/2}" y="{y0 + i*14:.1f}" class="t" text-anchor="middle">{html.escape(ln)}</text>')
    return "".join(partes)


ESTILO = {  # tipo: (trazo, marcador inicio, marcador fin)
    "Serving": ("", "", "srv"), "Realization": ("6 4", "", "rea"), "Assignment": ("", "asg0", "asg"),
    "Triggering": ("", "", "trg"), "Flow": ("6 3", "", "trg"), "Association": ("", "", ""),
    "Composition": ("", "cmp", ""),
}


def svg_conexion(rid):
    _, tipo, a, b, extra = REL[rid]
    pts = ruta(rid)
    d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    if tipo == "Access":
        ini, fin = ("acc0", "") if extra.get("acceso") == "read" else ("", "acc")
        trazo = "2 3"
    else:
        trazo, ini, fin = ESTILO[tipo]
    attrs = f'stroke-dasharray="{trazo}"' if trazo else ""
    attrs += f' marker-start="url(#{ini})"' if ini else ""
    attrs += f' marker-end="url(#{fin})"' if fin else ""
    out = f'<path d="{d}" fill="none" stroke="#333" stroke-width="1.1" {attrs}/>'
    if extra.get("nombre"):
        (x1, y1), (x2, y2) = pts[1], pts[2]
        out += f'<text x="{(x1+x2)/2:.0f}" y="{y1-4:.0f}" class="t s" text-anchor="middle">{extra["nombre"]}</text>'
    return out


DEFS = """<defs>
<marker id="srv" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M1 1L9.5 5L1 9" fill="none" stroke="#333" stroke-width="1.2"/></marker>
<marker id="rea" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M1 1L11 6L1 11z" fill="#fff" stroke="#333"/></marker>
<marker id="asg" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#333"/></marker>
<marker id="asg0" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6"><circle cx="5" cy="5" r="4" fill="#333"/></marker>
<marker id="trg" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#333"/></marker>
<marker id="acc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#333" stroke-width="1.2"/></marker>
<marker id="acc0" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#333" stroke-width="1.2"/></marker>
<marker id="cmp" viewBox="0 0 14 10" refX="1" refY="5" markerWidth="11" markerHeight="8" orient="auto-start-reverse"><path d="M1 5L7 1L13 5L7 9z" fill="#333"/></marker>
</defs>"""


def construir_svg():
    W, H = 1560, 1060
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         "<style>.t{font-family:Inter,'DejaVu Sans',Arial,sans-serif;font-size:11.5px;fill:#111}"
         ".b{font-weight:700;font-size:12.5px}.s{font-size:10.5px;font-style:italic}.g{font-size:13px;font-weight:700}</style>",
         DEFS, f'<rect width="{W}" height="{H}" fill="#fff"/>']
    for nombre, (x, y, w, h), fondo, borde in CAPAS:
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fondo}" stroke="{borde}" stroke-width="1.3"/>'
                 f'<text x="{x+8}" y="{y+16}" class="t g" fill="{borde}">{nombre}</text>')
    contenedores = {b[4] for b in CAJAS.values() if len(b) > 4}
    for k in CAJAS:  # primero contenedores
        if k in contenedores:
            p.append(svg_caja(k, contenedor=True))
    for k in CAJAS:
        if k not in contenedores:
            p.append(svg_caja(k))
    for rid in CONEXIONES:
        p.append(svg_conexion(rid))
    y = 1005
    for i, ln in enumerate(envolver(NOTA, 1500, px=5.9)):
        p.append(f'<text x="14" y="{y + i*14}" class="t s">{html.escape(ln)}</text>')
    p.append("</svg>")
    return "\n".join(p)


# ---------------------------------------------------------------- Archi (.archimate)
def nid(semilla):
    return "id-" + uuid.uuid5(uuid.NAMESPACE_URL, "hidrodata/" + semilla).hex


CARPETA = {"Business": "business", "Application": "application", "DataObject": "application",
           "Technology": "technology", "Node": "technology", "SystemSoftware": "technology", "Artifact": "technology"}


def carpeta_de(tipo):
    for pref, c in CARPETA.items():
        if tipo.startswith(pref):
            return c
    return "other"


def esc(s):
    return html.escape(s, quote=True)


def construir_archimate():
    vista_id = nid("vista")
    objetos = {k: nid("dobj/" + k) for k in CAJAS}
    capas_id = {n: nid("grupo/" + n) for n, *_ in CAPAS}
    conex = {rid: nid("conn/" + rid) for rid in CONEXIONES}
    entrantes = {k: [] for k in CAJAS}
    for rid in CONEXIONES:
        entrantes[REL[rid][3]].append(conex[rid])

    folders = {f: [] for f in ["strategy", "business", "application", "technology", "motivation",
                               "implementation_migration", "other", "relations"]}
    for k, (tipo, nombre, doc) in ELEMENTOS.items():
        folders[carpeta_de(tipo)].append(
            f'    <element xsi:type="archimate:{tipo}" name="{esc(nombre)}" id="{nid(k)}">'
            f'<documentation>{esc(doc)}</documentation></element>')
    for rid, tipo, a, b, extra in RELACIONES:
        acc = ""
        if tipo == "Access":
            acc = ' accessType="1"' if extra.get("acceso") == "read" else ""  # 0 (write) es el valor por defecto
        nombre = f' name="{esc(extra["nombre"])}"' if extra.get("nombre") else ""
        folders["relations"].append(f'    <element xsi:type="archimate:{tipo}Relationship" id="{nid(rid)}"{nombre}'
                                    f' source="{nid(a)}" target="{nid(b)}"{acc}/>')

    def padre_de(k):
        b = CAJAS[k]
        if len(b) > 4:
            return b[4]
        x, y = b[0], b[1]
        for n, (gx, gy, gw, gh), *_ in CAPAS:
            if gx <= x <= gx + gw and gy <= y <= gy + gh:
                return n
        raise ValueError(k)

    def abs_origen(padre):
        if padre in CAJAS:
            return CAJAS[padre][0], CAJAS[padre][1]
        for n, (gx, gy, *_), *_ in CAPAS:
            if n == padre:
                return gx, gy

    def objeto(k, ind):
        x, y, w, h = caja(k)
        ox, oy = abs_origen(padre_de(k))
        tc = f' targetConnections="{" ".join(entrantes[k])}"' if entrantes[k] else ""
        lin = [f'{ind}<child xsi:type="archimate:DiagramObject" id="{objetos[k]}"{tc} archimateElement="{nid(k)}">',
               f'{ind}  <bounds x="{x-ox:.0f}" y="{y-oy:.0f}" width="{w}" height="{h}"/>']
        for rid in CONEXIONES:
            if REL[rid][2] != k:
                continue
            _, _, a, b, _ = REL[rid]
            (sx, sy), (tx, ty) = centro(a), centro(b)
            bps = "".join(f'<bendpoint startX="{bx-sx:.0f}" startY="{by-sy:.0f}" endX="{bx-tx:.0f}" endY="{by-ty:.0f}"/>'
                          for bx, by in CONEXIONES[rid])
            lin.append(f'{ind}  <sourceConnection xsi:type="archimate:Connection" id="{conex[rid]}" '
                       f'source="{objetos[a]}" target="{objetos[b]}" archimateRelationship="{nid(rid)}">{bps}</sourceConnection>')
        for hijo in CAJAS:
            if len(CAJAS[hijo]) > 4 and CAJAS[hijo][4] == k:
                lin += objeto(hijo, ind + "  ")
        lin.append(f"{ind}</child>")
        return lin

    vista = [f'    <element xsi:type="archimate:ArchimateDiagramModel" name="Vista por capas v1.0" id="{vista_id}">',
             f"      <documentation>{esc(NOTA)}</documentation>"]
    for n, (gx, gy, gw, gh), fondo, _ in CAPAS:
        vista.append(f'      <child xsi:type="archimate:Group" id="{capas_id[n]}" name="{esc(n)}" fillColor="{fondo}">')
        vista.append(f'        <bounds x="{gx}" y="{gy}" width="{gw}" height="{gh}"/>')
        for k in CAJAS:
            if padre_de(k) == n:
                vista += objeto(k, "        ")
        vista.append("      </child>")
    vista.append(f'      <child xsi:type="archimate:Note" id="{nid("nota")}"><bounds x="10" y="1000" width="1540" height="50"/>'
                 f"<content>{esc(NOTA)}</content></child>")
    vista.append("    </element>")

    nombres = {"strategy": "Strategy", "business": "Business", "application": "Application", "technology": "Technology &amp; Physical",
               "motivation": "Motivation", "implementation_migration": "Implementation &amp; Migration", "other": "Other",
               "relations": "Relations"}
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           f'xmlns:archimate="http://www.archimatetool.com/archimate" name="{esc(NOMBRE)}" id="{nid("modelo")}" version="5.0.0">']
    for f, filas in folders.items():
        xml.append(f'  <folder name="{nombres[f]}" id="{nid("folder/" + f)}" type="{f}">')
        xml += filas
        xml.append("  </folder>")
    xml.append(f'  <folder name="Views" id="{nid("folder/views")}" type="diagrams">')
    xml += vista
    xml.append("  </folder>")
    xml.append(f"  <purpose>{esc('Arquitectura de la solución HidroData SIN para HidroCol Generación S.A. E.S.P. (caso académico).')}</purpose>")
    xml.append("</archimate:model>")
    return "\n".join(xml)


def a_png(svg_path, png_path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright no está instalado: se omite el PNG")
        return
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pag = nav.new_page(viewport={"width": 1560, "height": 1060}, device_scale_factor=2)
        pag.set_content(f'<html><body style="margin:0">{svg_path.read_text(encoding="utf-8")}</body></html>')
        pag.locator("svg").first.screenshot(path=str(png_path), animations="disabled", timeout=120000)
        nav.close()


if __name__ == "__main__":
    for k in CAJAS:
        assert k in ELEMENTOS, k
    for rid in CONEXIONES:
        assert REL[rid][2] in CAJAS and REL[rid][3] in CAJAS, rid
    svg = SALIDA / "ArchiMate_HidroData_v1.svg"
    svg.write_text(construir_svg(), encoding="utf-8")
    (SALIDA / "HidroData_ArchiMate_v1.archimate").write_text(construir_archimate(), encoding="utf-8")
    a_png(svg, SALIDA / "ArchiMate_HidroData_v1.png")
    print(f"{len(ELEMENTOS)} elementos, {len(RELACIONES)} relaciones, {len(CONEXIONES)} conexiones dibujadas")
