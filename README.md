# HidroData SIN

**Versión:** 1.0 · **Entrega:** final (noviembre de 2026) · **Curso:** Data Office Strategy · **Caso:** HidroCol Generación S.A. E.S.P. (empresa hipotética)

## Resumen

HidroCol es una generadora con parque mayoritariamente hidráulico que hoy monitorea sus reservas con descargas manuales, sin reglas de calidad y sin registrar sus decisiones. HidroData SIN es la solución: un **Data Office federado** que gobierna los datos abiertos de XM (Sinergox), un **pipeline en Python** que los descarga, limpia y valida, un **análisis exploratorio** que fija umbrales de riesgo, una **alerta automática** con Power Automate y un **dashboard** para que el Comité de Riesgo Hídrico decida a tiempo y deje constancia.

Datos: 7 colecciones de XM Sinergox, 2022–2026, ≈ 2,1 millones de registros (aportes, reservas, vertimientos, demanda, generación, capacidad efectiva y compras en bolsa).

## Mapa de la rúbrica

| # | Criterio (peso) | Dónde está |
|---|---|---|
| 1 | Problema, estrategia y diseño organizacional (10 %) | [`documentacion/EstrategiaOrganizacion/`](documentacion/EstrategiaOrganizacion/) — `01_problema_y_estrategia.md`, `02_diseno_data_office.md` |
| 2 | Procesos BPMN (10 %) | [`03_procesos_bpmn.md`](documentacion/EstrategiaOrganizacion/03_procesos_bpmn.md) y diagramas AS-IS / TO-BE en [`documentacion/BPMNyArchiMate/`](documentacion/BPMNyArchiMate/) |
| 3 | Automatización RPA (10 %) | [`automatizacion/`](automatizacion/) — flujo de alerta en Power Automate que lee `reservas_alerta.xlsx` |
| 4 | Arquitectura ArchiMate (10 %) | [`05_arquitectura_archimate.md`](documentacion/EstrategiaOrganizacion/05_arquitectura_archimate.md), modelo editable `HidroData_ArchiMate_v1.archimate` |
| 5 | Ingesta, limpieza y EDA en Python (10 %) | [`run_pipeline.py`](run_pipeline.py), [`src/`](src/), [`notebooks/`](notebooks/) |
| 6 | Gobierno de datos (30 %) | [`documentacion/PlanDeGobierno/`](documentacion/PlanDeGobierno/) — Plan de Gobierno, RACI, Excel de catálogo, diccionario y calidad por dataset, scripts de medición |
| 7 | Visualización / dashboard (10 %) | [`dashboard/`](dashboard/) |
| 8 | Trabajo colaborativo y documentación (10 %) | Este README, historial de commits y Pull Requests |

## Estructura del repositorio

```
├── README.md
├── requirements.txt
├── run_pipeline.py              # orquesta ingesta → normalización y limpieza → calidad
├── src/                         # ingesta.py, normalizacion.py, limpieza.py, calidad.py
├── data/
│   ├── raw/                     # HidrologiaYGeneracionEnergetica_7065.rar (Git LFS)
│   └── processed/               # lo genera el pipeline (no se versiona)
├── notebooks/                   # 01 ingesta, limpieza y calidad · 04 EDA
├── img/eda/                     # gráficos del EDA
├── documentacion/
│   ├── EstrategiaOrganizacion/  # problema, Data Office, BPMN, datos, arquitectura
│   ├── BPMNyArchiMate/          # diagramas BPMN y ArchiMate (+ fuente/ para regenerar ArchiMate)
│   └── PlanDeGobierno/          # Plan de Gobierno, RACI, Excel S2 y scripts de calidad
├── automatizacion/              # Power Automate: tabla de alerta y evidencia del flujo
└── dashboard/                   # dashboard final
```

## Herramientas

| Uso | Herramienta |
|---|---|
| Datos | XM Sinergox (exportación de históricos en Excel) |
| Procesamiento y análisis | Python 3.10–3.12, pandas, pyarrow, matplotlib, JupyterLab |
| Gobierno | Excel de la plantilla del curso (catálogo, diccionario, calidad, seguridad, maestros) + scripts Python |
| Automatización | Microsoft Power Automate, Outlook, OneDrive |
| Modelado | BPMN (diagramas TO-BE / AS-IS), ArchiMate (Archi) |
| Versionamiento | GitHub + Git LFS |

## Cómo ejecutar el proyecto

1. **Clonar con los datos.** El `.rar` está en Git LFS: instalar [Git LFS](https://git-lfs.com) y ejecutar `git lfs pull` después de clonar (o descargar el `.rar` desde la página del repositorio).
2. **Instalar dependencias** (Python 3.10 a 3.12): `pip install -r requirements.txt`.
3. **Descomprimir** `data/raw/HidrologiaYGeneracionEnergetica_7065.rar` dentro de `data/raw/` con 7-Zip, WinRAR o `unar`. Queda `data/raw/HidrologiaYGeneracionEnergetica/<Coleccion>/*.xlsx`; la ingesta también acepta las carpetas de colección directamente en `data/raw/`.
4. **Ejecutar el pipeline** desde la raíz: `python run_pipeline.py` (≈ 5 minutos). Genera `data/processed/ingesta`, `normalizado` y `calidad`.
5. **Abrir los notebooks** en orden (`01`, `04`) y ejecutar *Restart & Run All*. El EDA genera `data/processed/eda/eda_mensual.parquet` y `automatizacion/reservas_alerta.xlsx`.
6. **Regenerar el ArchiMate** (opcional): `python documentacion/BPMNyArchiMate/fuente/generar_archimate.py`.

## Equipo y roles del Data Office

| Integrante | Rol en el gobierno del dato (RACI) | Responsabilidad en el proyecto |
|---|---|---|
| Sara Rúa García | Data Owner | Gobierno de datos aplicado, reglas de calidad, estructura y coherencia del repositorio |
| Rafael José Gutiérrez Realpe | Data Steward | EDA y notebooks, arquitectura ArchiMate, documentación |
| Valentina Leal Noreña | Custodio técnico | Pipeline de ingesta y limpieza, estrategia, dashboard |
| Paula Andrea Olier Alba | Consumidor / Analista | Automatización con Power Automate, BPMN, guion del pitch |

Cada integrante trabaja en su rama y entra a `main` por Pull Request revisado por otra persona.

## Decisiones de alcance

- HidroCol y su proceso actual son un caso académico hipotético; las cifras corresponden al SIN, no a HidroCol.
- La fuente es XM Sinergox, operador oficial del mercado; no está en la lista de fuentes sugeridas de la guía.
- El dataset de «precio» de Sinergox trae **compras en bolsa (kWh)**, no precio; se usa como señal de volumen.
- Los umbrales de alerta (vigilancia 50 %, crítico 40 % del volumen útil) son propuestas del EDA; los aprueba el Data Owner.

## Historial de versiones

| Versión | Fecha | Contenido |
|---|---|---|
| 0.1 | 28-sep-2026 | Problema, estrategia, Data Office, BPMN, selección de datos y boceto ArchiMate |
| 0.2 | 23-oct-2026 | Pipeline, EDA, salida para Power Automate y Plan de Gobierno v0.2 |
| 1.0 | nov-2026 | Gobierno aplicado, ArchiMate v1.0, notebooks finales, automatización y dashboard |
