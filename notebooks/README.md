# Notebooks

Ejecutar en orden desde la raíz del repositorio, después de descomprimir los datos (ver el [README](../README.md#cómo-ejecutar-el-proyecto)). Antes de cada entrega: *Restart & Run All*.

| # | Notebook | Qué hace | Rúbrica |
|---|---|---|---|
| 01 | [`01_ingesta_limpieza_calidad.ipynb`](01_ingesta_limpieza_calidad.ipynb) | Ejecuta `run_pipeline.py` (o reutiliza su salida) y muestra la evidencia de cada etapa: filas por colección, esquema normalizado, bitácoras de incidentes e imputaciones y métricas de calidad | 5 y 6 |
| 04 | [`04_eda.ipynb`](04_eda.ipynb) | Análisis exploratorio de las preguntas P1–P6: reservas, aportes, generación, capacidad, demanda, vertimientos y compras en bolsa. Produce `data/processed/eda/eda_mensual.parquet` (dashboard) y `automatizacion/reservas_alerta.xlsx` (Power Automate) | 5 |

La lógica de ingesta, normalización, limpieza y calidad vive en `src/` (scripts que se ejecutan igual cada vez); los notebooks la leen y explican. Las reglas de calidad formales por ID (Plan de Gobierno §7) se miden en `documentacion/PlanDeGobierno/`.

**Convenciones:** los notebooks no modifican `data/raw/`; las rutas se calculan desde la raíz del repositorio, así que funcionan desde `notebooks/` o desde la raíz.
