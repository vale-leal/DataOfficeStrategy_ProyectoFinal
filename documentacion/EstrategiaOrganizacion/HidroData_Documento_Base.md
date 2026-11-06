# HidroCol SIN — Documento base: estrategia, procesos, datos y arquitectura

**Caso:** HidroCol Generación S.A. E.S.P. (empresa hipotética) · **Versión:** 1.0 · **Fuente de datos:** XM — Sinergox, 2022–2026

Este documento reúne y reemplaza los archivos `01` a `05`. Las secciones 1 a 5 siguen el texto de la Entrega 1; la sección 6 documenta la arquitectura implementada. Lo que ya está desarrollado en otros documentos no se repite aquí:

| Tema | Dónde está |
|---|---|
| Diagnóstico (PESTEL, FODA), alternativas, BSC, organigrama to-be, roadmap, OKR y riesgos | Documento de estrategia corporativa |
| Catálogo, diccionario, matriz RACI de gobierno, reglas de calidad, linaje, clasificación y acceso | [`Plan_Gobierno_Datos.md`](Plan_Gobierno_Datos.md) |

---

## 1. Problema y necesidad

**Contexto.** HidroCol es una generadora hipotética del Sistema Interconectado Nacional (SIN) con un parque mayoritariamente hidráulico. Su capacidad de generar y su exposición al riesgo de desabastecimiento dependen del nivel de los embalses y de los aportes hídricos, que varían con fenómenos como El Niño y La Niña. Colombia ya vivió un racionamiento en 1992–1993 por esta misma vulnerabilidad.

**Problema.** HidroCol decide de forma reactiva. El monitoreo depende de descargas manuales desde XM, revisiones esporádicas y reportes sin reglas de calidad ni trazabilidad:

- El estado de los embalses se conoce con días de retraso.
- Los errores en los datos pueden llegar sin detectarse a los reportes de la gerencia.
- No hay un criterio único ni documentado de cuándo una situación hídrica es un riesgo.
- Las decisiones del comité no quedan registradas ni se trazan hasta los datos que las motivaron.

> **Enunciado:** HidroCol no tiene visibilidad oportuna y confiable del estado de sus reservas hídricas, lo que retrasa la detección del riesgo de racionamiento y la toma de decisiones.

**Necesidad.** La Gerencia de Energía y el Comité de riesgo hídrico necesitan conocer cada día, con datos validados, el estado de reservas y aportes del SIN, y recibir una alerta temprana cuando se superan los umbrales de riesgo, para decidir a tiempo y dejar constancia.

## 2. Estrategia de datos

**Misión del Data Office:** garantizar que las decisiones sobre el riesgo hídrico se tomen con datos oportunos, confiables y trazables, a partir de fuentes abiertas oficiales del sector eléctrico.

| # | Objetivo estratégico | Indicador | Meta |
|---|---|---|---|
| O1 | Visibilidad diaria del estado de embalses y aportes | Hora de actualización del dashboard | Antes de las 7:00 a. m., todos los días |
| O2 | Detección temprana del riesgo hídrico | Tiempo entre superar el umbral y enviar la alerta | Menos de 24 horas |
| O3 | Confiabilidad del dato para decidir | % de registros que cumplen las reglas de calidad | 98 % o más |
| O4 | Decisiones trazables | % de alertas con decisión registrada por el comité | 100 % |

Las metas son criterios propuestos para evaluar la solución, no mediciones de una empresa real.

**Alcance por fases.** La fase 1 (este proyecto) cubre visibilidad operativa y alertas: ingesta, validación de calidad, indicadores, dashboard y alerta por correo, bajo un modelo de gobierno formal. La fase 2 (evolución) es la predictibilidad: con el histórico curado se podrán construir proyecciones a 30 días. Pronósticos, recomendaciones de despacho, portal público y reportes regulatorios quedan fuera de la fase 1. Se prioriza la visibilidad porque es la necesidad más inmediata y porque un pronóstico sobre datos sin validar no sería confiable.

**Del dato a la decisión.** Cada mañana debe responderse qué cambió en las reservas, dónde y si exige revisión del comité. El Data Owner aprueba definiciones, umbrales y reglas; el Data Steward revisa los datos que incumplen las reglas; el Custodio técnico conserva la extracción original y registra las transformaciones; el Analista publica los indicadores; y el comité decide y deja constancia de los datos y la versión del tablero que usó. Así se puede reconstruir por qué se emitió una alerta y qué se hizo después.

## 3. Diseño organizacional del Data Office

**Modelo: híbrido (federado).** Un Data Office central, liderado por el CDO, define políticas, estándares, reglas de calidad y arquitectura. El significado y el uso del dato quedan en el negocio, mediante un Data Owner en Planeación Energética. Un modelo centralizado alejaría las decisiones sobre el dato de quienes mejor lo conocen; uno descentralizado no garantizaría estándares de calidad y clasificación, crítico cuando el dato sirve para decidir riesgos. El híbrido equilibra control central y conocimiento del negocio, y se ajusta a una empresa mediana con un dominio de datos principal. El organigrama to-be y los dos comités (Gobierno de Datos y Riesgo Hídrico) están en el documento de estrategia, sección 3.3.

| Rol | Responsabilidad principal |
|---|---|
| CDO / Data Office | Define estrategia, políticas y estándares; rinde cuentas ante la gerencia |
| Data Owner (Planeación Energética) | Dueño del significado del dato: aprueba su clasificación, las reglas de calidad y los umbrales de riesgo |
| Data Steward | Aplica y monitorea las reglas de calidad, mantiene catálogo y diccionario, resuelve incidentes |
| Custodio técnico | Opera la infraestructura, el pipeline y los accesos |
| Analista de datos | Construye indicadores, EDA y dashboard |
| Consumidor (Gerencia / Comité de riesgo) | Usa el dashboard y las alertas para decidir y registra sus decisiones |

**Forma de trabajo.** El equipo técnico (analista y custodio) trabaja de forma ágil, con iteraciones alineadas a las entregas; el Data Office coordina el gobierno con revisiones periódicas junto al Data Owner.

**Matriz RACI de la Entrega 1 (V.0)** (actividades operativas). **R** ejecuta · **A** rinde cuentas y aprueba · **C** consultado · **I** informado. La matriz de tareas de gobierno del dataset, con los cuatro roles del equipo, está en el Plan de Gobierno (sección 3.2).

| Actividad | CDO | Data Owner | Data Steward | Custodio técnico | Analista | Comité de riesgo |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Definir políticas y estándares | A | C | R | C | I | I |
| Clasificar datos (público / interno / confidencial) | C | A | R | C | I | – |
| Definir y validar reglas de calidad | I | A | R | C | C | – |
| Operar la ingesta y el pipeline | I | I | C | A/R | C | – |
| Resolver incidentes de calidad (M3) | I | C | A/R | C | I | – |
| Definir umbrales de alerta de riesgo | C | A | C | I | R | C |
| Decidir acciones ante alerta (M6) | I | C | – | – | I | A/R |

## 4. Procesos (BPMN)

### 4.1 Situación actual (AS-IS)

Hoy el monitoreo depende del analista de datos. Una vez por semana, o cuando la gerencia lo pide, descarga los reportes de XM, los consolida en una hoja de cálculo y los revisa sin reglas de calidad. Si según su criterio el nivel de los embalses es preocupante, envía un correo con el reporte adjunto; si no, lo archiva. La Gerencia y el Comité de riesgo lo revisan días después y deciden en reunión, sin dejar registro de la decisión ni de los datos que la respaldan.

| # | Punto débil |
|---|---|
| P1 | Descarga manual y periódica: el dato llega con retraso y depende de solicitudes y procesos desordenados |
| P2 | Consolidación sin trazabilidad: no hay claridad del origen del dato ni de las transformaciones a las que se somete |
| P3 | Revisión sin reglas de calidad: los errores pasan al reporte o se corrigen a mano sin registro |
| P4 | Criterio de riesgo subjetivo: no hay umbrales o condiciones definidas |
| P5 | Revisión tardía: cuando se revisa el reporte la situación ya pudo cambiar y se decide con datos obsoletos |
| P6 | Decisión no documentada: no queda registro de la decisión ni de los datos que se tuvieron en cuenta |

### 4.2 Proceso propuesto (TO-BE)

El proceso corre cada día a las 6:00 a. m.: extrae reservas y aportes a la capa raw, valida las reglas de calidad y, si no se cumplen, pasa el caso al Data Steward. Si se cumplen, calcula indicadores, registra el linaje y publica el dashboard. Si se supera el umbral de riesgo, envía una alerta por correo y el comité la analiza, decide y registra su decisión.

| Mejora | AS-IS (problema) | TO-BE (solución) | Objetivo |
|---|---|---|---|
| **M1 · Ingesta programada** | Descarga manual semanal (P1) | Extracción automática diaria a las 6:00 a. m. desde API XM / Sinergox a la capa raw | O1 |
| **M2 · Validación de calidad** | Revisión sin reglas (P3) | Reglas de calidad automáticas y registro de métricas en cada ejecución | O3 |
| **M3 · Gestión de incidentes** | Errores sin detectar o corregidos sin registro (P3) | El Data Steward revisa cada incidente y lo corrige o aprueba con nota | O3 |
| **M4 · Indicadores y linaje** | Consolidación sin trazabilidad; revisión tardía (P2, P5) | Cálculo automático de indicadores, seguimiento del flujo de datos y publicación diaria del dashboard | O1, O4 |
| **M5 · Alerta automática** | Criterio subjetivo y correo manual (P4) | Umbral aprobado por el Data Owner y alerta automática por correo (Power Automate) | O2 |
| **M6 · Decisión registrada** | Decisión en reunión sin documentar (P6) | El comité analiza escenarios en el dashboard y registra su decisión de forma trazable | O4 |

**Automatización.** Ingesta y validación con scripts de Python (`run_pipeline.py`) y alerta con Power Automate sobre una tabla de Excel. Los horarios (6:00 y 7:00 a. m.) y los umbrales son metas de diseño sujetas a la hora real de publicación de Sinergox y a la aprobación del Data Owner. En la implementación, la fuente es el histórico descargado de Sinergox y versionado en el repositorio; la extracción directa por API queda como evolución (sección 6.4).

## 5. Selección de datos

La fuente es [XM — Sinergox](https://sinergox.xm.com.co), portal público del operador del SIN. La ventana de análisis es 2022–2026 (2026 hasta la última fecha disponible). Reservas es la fuente principal; las demás variables enriquecen el análisis y habilitan la fase 2 sin cambiar de fuente. Sinergox no figura entre las fuentes sugeridas por el curso, así que se confirma con la docente que cumple el requisito de datos abiertos.

| Dataset | Sección de Sinergox | Uso en la solución |
|---|---|---|
| Reservas hidráulicas en energía | `sinergox.xm.com.co/hydrology/historical` | Fuente principal: cuánto hay en los embalses |
| Aportes hídricos (caudal frente a la media histórica) | `sinergox.xm.com.co/hydrology/historical` | Anticipar tendencias climáticas: cuánto llega a los embalses |
| Vertimientos | `sinergox.xm.com.co/hydrology/historical` | Agua que pasa por embalses o plantas sin generar energía |
| Generación real por tipo de recurso | `sinergox.xm.com.co/supply/historical` | Producción real según fuente hídrica y otras |
| Capacidad efectiva / composición del parque | `sinergox.xm.com.co/supply/historical` | Contexto de la dependencia hídrica |
| Demanda de energía del SIN | `sinergox.xm.com.co/demand/historical` | Energía que requieren los usuarios |
| Precio de la energía en bolsa nacional | `sinergox.xm.com.co/transactions/historical` | Enlazar variables en un contexto económico |

**Criterios de selección.** Relevancia para el estado hídrico, credibilidad del operador oficial, acceso público, cobertura de periodos secos y húmedos, ausencia de datos personales en las tablas principales y un volumen manejable en una estación de trabajo.

**Modelo de integración.** El dato pasa por tres capas: `raw` (tal como se descarga), `validado` (cumple las reglas) y `curado` (integrado, con indicadores). La llave es la fecha y la granularidad objetivo es diaria: la reserva toma el valor de cierre del día; aportes, vertimientos, demanda y generación se suman; la capacidad toma el valor vigente.

**Sobre las tablas descargadas.** La tabla de reserva trae solo el porcentaje de volumen útil, y el archivo rotulado como precio de bolsa contiene compras de energía en kWh. Los hallazgos completos, las unidades y los pendientes están en el Plan de Gobierno (sección 2).

## 6. Arquitectura de la solución (ArchiMate v1.0)
La v1.0 modela lo que está implementado en el repositorio, no el boceto de la primera entrega. Conecta el proceso TO-BE (negocio), los programas y datos del repositorio (aplicación) y dónde corren (tecnología).

### 6.1 Capa de negocio

| Tipo | Elementos |
|---|---|
| Actores | Planeación Energética (spoke del Data Office federado, dueña del significado del dato y de los umbrales) · Data Office / CDO (hub staff de la Gerencia General) · Comité de Riesgo Hídrico |
| Roles | Data Owner · Data Steward · Custodio técnico · Analista de datos |
| Proceso | Monitoreo y alerta de reservas hídricas, compuesto por cuatro subprocesos: obtener y validar datos (M1–M3), calcular indicadores y publicar dashboard (M4), enviar alerta por umbral (M5) y decidir y registrar la decisión (M6) |
| Servicios | Información hídrica diaria validada · Alerta de riesgo hídrico |
| Objetos | Plan de Gobierno de Datos · Umbrales de riesgo aprobados · Registro de decisiones |

### 6.2 Capa de aplicación

| Componente | Archivo en el repositorio | Lee → escribe |
|---|---|---|
| Ingesta | `src/ingesta.py` | Datos crudos XM → parquet de ingesta |
| Normalización y limpieza | `src/normalizacion.py`, `src/limpieza.py` | → datos normalizados |
| Calidad | `src/calidad.py` | → bitácoras y métricas de calidad |
| Pipeline HidroData | `run_pipeline.py` (orquesta los tres anteriores) | — |
| Notebook EDA | `notebooks/04_eda.ipynb` | Datos normalizados → indicadores mensuales y tabla de alerta |
| Dashboard | `dashboard/` | Indicadores mensuales y bitácoras de calidad → visualización |
| Flujo de alerta | `automatizacion/` (Power Automate) | Tabla de alerta → correo |
| Medición de reglas de gobierno | `documentacion/PlanDeGobierno/*.py` y Excel S2 | Datos crudos XM → catálogo, diccionario y scorecard |

Los servicios que expone esta capa son datos normalizados y validados, reporte de calidad, visualización de indicadores y notificación de alerta.

### 6.3 Capa de tecnología

| Nodo | Contiene |
|---|---|
| XM Sinergox (externo) | Servicio de exportación de históricos (`.xlsx`) |
| Estación de trabajo del equipo | Python 3.10–3.12 con pandas y pyarrow, JupyterLab, herramienta del dashboard y `data/processed/*.parquet` |
| GitHub (repositorio y Git LFS) | Código (`run_pipeline.py`, `src/`, `notebooks/`) y `HidrologiaYGeneracionEnergetica_7065.rar` |
| Microsoft 365 (nube) | Power Automate, Outlook y `reservas_alerta.xlsx` en OneDrive |

**Linaje de punta a punta:** Sinergox → `.rar` → ingesta → normalización y limpieza → calidad → EDA → indicadores y tabla de alerta → dashboard y Power Automate → comité → registro de decisiones. El plan lo detalla en su sección 8.

### 6.4 Decisiones y cambios

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| Capas crudo → normalizado → indicadores, cada una en su archivo | Transformar sobre el mismo archivo | Se reprocesa desde la fuente y se mide la calidad en cada paso |
| Pipeline en scripts (`src/`) y análisis en notebooks | Todo en notebooks | Los scripts se ejecutan igual cada vez; el notebook queda para analizar y explicar |
| Descarga manual desde Sinergox, versionada en Git LFS | API de XM (`pydataxm`) | La descarga anual en Excel es la vía oficial verificada y el `.rar` deja evidencia de lo descargado; la API es una evolución (riesgo R1 de la estrategia) |
| Alerta con Power Automate sobre una tabla de Excel | Envío manual de correo | Reduce el tiempo de alerta (O2) y el criterio subjetivo (P4) con herramientas ya licenciadas |
| Umbrales como columnas de la tabla de alerta | Umbrales dentro del flujo | El Data Owner los cambia en un solo lugar y quedan trazables |
| Sin nube de datos | AWS, Azure o GCP | El curso no la exige y el volumen (unos 2,1 millones de registros) cabe en una estación de trabajo |

**Cambios frente al boceto de la Entrega 1.** La fuente pasa de «API XM · SIMEM · datos.gov.co» a la exportación de históricos de Sinergox, que es lo que se usó. Los componentes genéricos pasan a ser uno por archivo de `src/` y del notebook. Las métricas de calidad ahora las escribe el componente de calidad y el dashboard las lee (antes colgaban del dashboard). El flujo de alerta lee la tabla `TablaReservas` de `reservas_alerta.xlsx`. Los artefactos de gobierno y el proceso compuesto por M1–M6 en cuatro subprocesos se incorporan al modelo.

**Para editar el modelo:** la vista y el `.archimate` se generan con `documentacion/BPMNyArchiMate/fuente/generar_archimate.py` (el PNG necesita `playwright`), o se abre el `.archimate` en Archi y se exporta de nuevo la imagen.
