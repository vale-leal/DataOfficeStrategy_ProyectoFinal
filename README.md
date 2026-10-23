# HidroData SIN

**Versión:** 0.1 · **Entrega:** primera entrega parcial · **Caso:** HidroCol Generación S.A. E.S.P. (empresa hipotética)

## Resumen

HidroData propone un Data Office para que la gerencia de una generadora con alta dependencia hidráulica pueda seguir las reservas del Sistema Interconectado Nacional, revisar alertas y documentar sus decisiones. La ventana de análisis acordada es **2022–2026**; para 2026 se usará la última fecha disponible al extraer la fuente. Esta primera entrega define la estrategia, los responsables, los procesos y la arquitectura propuesta. Todavía no presenta un pipeline ni un tablero en operación.

## Problema y enfoque

En el caso hipotético, el analista descarga reportes de XM, consolida hojas de cálculo y aplica criterios de riesgo sin reglas documentadas. El proceso propuesto incorpora ingesta diaria, controles de calidad, revisión de excepciones, publicación de indicadores, alerta por correo y registro de las decisiones. El Data Office híbrido define estándares centrales y deja la aprobación del significado del dato y de los umbrales en Planeación Energética.

## Contenido de esta entrega

| Requisito | Archivo |
| --- | --- |
| Problema, necesidad y estrategia | `documentacion/01_problema_y_estrategia.md` |
| Organización y diseño del Data Office | `documentacion/02_diseno_data_office.md` |
| BPMN actual (AS-IS), mejoras y BPMN propuesto (TO-BE) | `documentacion/03_procesos_bpmn.md`; `documentacion/img/bpmn_as_is.png`; `documentacion/img/bpmn_to_be.jpeg` |
| Selección de datos y ventana 2022–2026 | `documentacion/04_seleccion_datos_abiertos.md` |
| Boceto ArchiMate en tres capas | `documentacion/05_arquitectura_archimate.md`; `documentacion/img/archimate_boceto.jpeg` |
| Borrador inicial del Plan de Gobierno (adelanto de la segunda entrega) | `documentacion/Plan_Gobierno_Datos.md` |

Los diagramas se conservan como imágenes suministradas por el equipo; no se adjuntaron sus archivos editables.

## Fuente seleccionada

- [XM Sinergox](https://sinergox.xm.com.co), portal de información del mercado de energía mayorista. Es la fuente propuesta para todo el análisis.
- Variables previstas: reservas hídricas (variable principal), aportes hídricos, vertimientos, precio de bolsa nacional, demanda, capacidad y generación real. Las reservas y los aportes responden directamente a la necesidad de negocio; las demás son variables de contexto.
- Referencia para aportes: [Detalle de Aportes Hídricos](https://sinergox.xm.com.co/hdrlg/Paginas/Informes/DetalleAportesHidricos.aspx).

Antes de programar la ingesta se verificará la cobertura diaria de 2022–2026, los campos, las unidades, la granularidad por embalse y región, la fecha real de publicación y la forma de descarga. Sinergox no figura entre las fuentes sugeridas en la guía del curso; se confirmará con la docente que cumple el requisito.

## Decisiones de alcance

- La organización y su proceso actual son un caso académico hipotético. Las cifras sectoriales citadas corresponden al SIN, no al desempeño de HidroCol.
- La primera fase prioriza visibilidad, calidad y trazabilidad. Pronósticos, despacho y servicios públicos de datos requieren una ampliación del alcance.
- Los horarios, porcentajes de calidad y tiempos de alerta son metas de diseño pendientes de validación.

## Cómo ejecutar el proyecto

1. Instalar las dependencias: `pip install -r requirements.txt`.
2. Descomprimir `data/raw/HidrologiaYGeneracionEnergetica_7065.rar` dentro de `data/raw/`, de modo que queden carpetas por colección con los `.xlsx` (`data/raw/<Coleccion>/*.xlsx`).
3. Ejecutar `python run_pipeline.py`, que genera `data/processed/ingesta`, `data/processed/normalizado` y `data/processed/calidad`.
4. Abrir `notebooks/04_eda.ipynb` y ejecutar todo (Restart & Run All).

## Próximas entregas

En la segunda entrega se desarrollarán los notebooks de ingesta, limpieza y análisis exploratorio; una tarea automatizada (ingesta programada y alerta con Power Automate); y el primer Plan de Gobierno de Datos con métricas. En la entrega final se completarán el gobierno aplicado al dataset, el dashboard, la arquitectura y las instrucciones para ejecutar el proyecto.

La estructura prevista es `/notebooks`, `/documentacion`, `/automatizacion` y `/dashboard`, conforme a la guía del curso. Por ahora las carpetas de implementación solo contienen un README que describe su propósito; se llenarán con trabajo real en las siguientes entregas.

## Trabajo colaborativo

Cada integrante debe registrar sus cambios en commits descriptivos y revisar el contenido antes de integrarlo (ver `CONTRIBUTING.md`). El equipo añadirá aquí la identificación de sus tres miembros y el enlace del repositorio al momento de la entrega.
