**HidroData SIN v0.1**

Problema, estrategia y diseño organizacional del Data Office

# **1\. Contexto**

HidroCol Generación S.A. E.S.P. es una empresa hipotética de generación de energía que opera dentro del Sistema Interconectado Nacional (SIN). Su parque de generación es mayoritariamente hidráulico. Por eso su capacidad de generar, y su exposición al riesgo de desabastecimiento, depende directamente del nivel de los embalses y de los aportes hídricos, que varían con fenómenos climáticos como El Niño y La Niña. Colombia ya vivió un racionamiento eléctrico en 1992–1993 por esta misma vulnerabilidad, y cada temporada seca vuelve a poner el tema en la agenda del sector.

# **2\. Problema de negocio**

Hoy HidroCol toma decisiones de gestión del riesgo hídrico de forma reactiva. El monitoreo de reservas y aportes depende de descargas manuales de información de XM, de revisiones esporádicas y de reportes que se construyen sin reglas de calidad ni trazabilidad. Como resultado:

* El estado de los embalses se conoce con días de retraso.

* Los errores en los datos pueden llegar sin detectarse a los reportes que usa la gerencia.

* No existe un criterio único ni documentado para decidir cuándo una situación hídrica representa un riesgo.

* Las decisiones del comité de riesgo no quedan registradas ni se pueden trazar hasta los datos que las motivaron.

No tiene visibilidad oportuna y confiable del estado de sus reservas hídricas, lo que retrasa la detección del riesgo de racionamiento y la toma de decisiones.

# **3\. Necesidad de negocio**

La Gerencia de Energía y el Comité de riesgo hídrico necesitan conocer cada día, con datos validados, el estado de las reservas y aportes del SIN. También necesitan recibir una alerta temprana cuando se superan los umbrales de riesgo, para tomar decisiones a tiempo y dejarlas documentadas.

# **4\. Estrategia de datos**

**Misión del Data Office:** garantizar que las decisiones de gestión del riesgo hídrico se tomen con datos oportunos, confiables y trazables, a partir de fuentes abiertas oficiales del sector eléctrico.

## **4.1 Objetivos estratégicos y metas**

| \# | Objetivo estratégico | Indicador (KPI) | Meta |
| :---- | :---- | :---- | :---- |
| O1 | Visibilidad diaria del estado de embalses y aportes | Hora de actualización del dashboard | Antes de las 7:00 a.m., todos los días |
| O2 | Detección temprana del riesgo hídrico | Tiempo entre la superación del umbral y el envío de la alerta | Menos de 24 horas |
| O3 | Confiabilidad del dato para decidir | % de registros que cumplen las reglas de calidad | ≥ 98% |
| O4 | Decisiones trazables | % de alertas con una decisión registrada por el comité | 100% |

## **4.2 Alcance por fases**

* **Fase 1 (este proyecto):** visibilidad operativa y alertas. Incluye la ingesta automatizada, la validación de calidad, los indicadores, el dashboard y la alerta por correo, bajo un modelo de gobierno de datos formal.

* **Fase 2 (evolución):** predictibilidad de la generación. Con el histórico curado y gobernado de la fase 1, se podrán construir modelos de proyección a 30 días. Sin datos confiables, cualquier pronóstico sería poco fiable, así que la fase 1 es el habilitador de la fase 2\.

## **4.3 Justificación**

Se prioriza la visibilidad operativa porque es la necesidad más inmediata y porque construye la base de datos confiable que cualquier análisis predictivo futuro necesita. Invertir primero en gobierno y calidad evita construir pronósticos sobre datos sin validar.

**4.4 Cómo se convierte el dato en una decisión**

La prioridad es responder cada mañana qué cambió en las reservas, dónde ocurrió y si exige una revisión del comité. Por eso la primera fase combina una fuente identificada, controles de calidad, indicadores comparables y un registro de las alertas. Las proyecciones y recomendaciones de despacho quedan para una etapa posterior: primero necesitamos una serie 2022–2026 consistente y una definición aprobada de riesgo.

El Data Owner aprueba las definiciones y los umbrales; el Data Steward revisa los datos que no pasan las reglas; el custodio conserva la extracción original y registra las transformaciones; el analista publica indicadores; el comité decide y deja constancia de los datos y la versión del tablero utilizados. Así se puede reconstruir por qué se emitió una alerta y qué se hizo después.

Las metas de la sección 4.1 (actualización antes de las 7:00 a. m., alerta en menos de 24 horas, calidad igual o superior a 98 % y decisiones registradas para todas las alertas) son criterios propuestos para evaluar la solución. No describen el desempeño actual de una empresa real.

**4.5 Qué se debe validar antes de implementar**

Cobertura: verificar la primera y última fecha disponibles entre 2022 y 2026, los días faltantes y la granularidad por embalse y región.

Definiciones: confirmar qué significa volumen útil, en qué unidades se publica y si la capacidad de referencia cambia durante el período.

Calidad: comprobar duplicados por fecha y embalse, valores nulos, rangos válidos y consistencia entre registros diarios y agregados.

Oportunidad: medir cuándo se publica realmente el dato antes de prometer la actualización del tablero a las 7:00 a. m.; documentar una alternativa si la extracción falla.

Uso para decidir: acordar con Planeación Energética los umbrales de alerta y qué información debe registrar el comité al cerrar cada caso.

Estas comprobaciones guían la segunda entrega. En esta primera entrega se deja trazado qué se medirá y quién aprobará las decisiones de diseño.

# **5\. Diseño organizacional del Data Office**

**Modelo propuesto: híbrido (federado).** Un Data Office central, liderado por el CDO, define las políticas, los estándares, las reglas de calidad y la arquitectura. La responsabilidad sobre el significado y el uso del dato queda en el negocio, a través de un Data Owner en Planeación Energética.

## **5.1 Por qué este modelo**

* Un modelo totalmente centralizado alejaría las decisiones sobre el dato de quienes mejor lo entienden, el área de Planeación Energética.

* Un modelo totalmente descentralizado no garantizaría estándares únicos de calidad y clasificación, algo crítico cuando los datos alimentan decisiones de riesgo.

* El modelo híbrido equilibra el control central con el conocimiento del negocio, y se ajusta a una empresa mediana con un dominio de datos principal (recurso hídrico y energético).

## **5.2 Roles**

| Rol | Responsabilidad principal |
| :---- | :---- |
| CDO / Data Office | Define la estrategia, las políticas y los estándares de datos, y rinde cuentas ante la gerencia |
| Data Owner (Planeación Energética) | Es el dueño del significado del dato: aprueba su clasificación, las reglas de calidad y los umbrales de riesgo |
| Data Steward | Aplica y monitorea las reglas de calidad, mantiene el catálogo y el diccionario, y resuelve incidentes |
| Custodio técnico | Opera la infraestructura, el pipeline y los accesos |
| Analista de datos | Construye los indicadores, el EDA y el dashboard |
| Consumidor (Gerencia / Comité de riesgo) | Usa el dashboard y las alertas para decidir, y registra sus decisiones |

## **5.3 Forma de trabajo**

El equipo técnico (analista y custodio) trabaja con un enfoque ágil, con iteraciones alineadas a las entregas del proyecto. El gobierno lo coordina el Data Office con revisiones periódicas junto al Data Owner.

# **6\. Matriz RACI preliminar**

R \= Responsable (ejecuta) · A \= Accountable (rinde cuentas, aprueba) · C \= Consultado · I \= Informado

| Actividad | CDO | Data Owner | Data Steward | Custodio técnico | Analista | Comité de riesgo |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Definir políticas y estándares | **A** | C | R | C | I | I |
| Clasificar datos (público / interno / confidencial) | C | **A** | R | C | I | – |
| Definir y validar reglas de calidad | I | **A** | R | C | C | – |
| Operar la ingesta y el pipeline | I | I | C | **A/R** | C | – |
| Resolver incidentes de calidad (M3) | I | C | **A/R** | C | I | – |
| Definir umbrales de alerta de riesgo | C | **A** | C | I | R | C |
| Decidir acciones ante alerta (M6) | I | C | – | – | I | **A/R** |

# **7\. Selección de datos abiertos**

La ventana de análisis es 2022–2026 (2026 hasta la última fecha disponible). Reservas Hidráulicas en Energía es la fuente principal identificada; las demás son candidatas para enriquecer el análisis. La cobertura, frecuencia y campos se validarán antes de construir el pipeline.

| Dataset | Fuente | Uso en la solución |
| :---- | :---- | :---- |
| Reservas Hidráulicas en Energía (volumen útil diario y total en energía) | Datos Abiertos Colombia · 9h36-6mfa | Fuente principal confirmada para monitoreo de reservas |
| Aportes hídricos (caudal vs. media histórica) | XM / SIMEM | Anticipar tendencia (El Niño / La Niña) · fuente candidata; validar disponibilidad y esquema en la entrega 2 |
| Generación real por tipo de recurso | XM / SIMEM | Contexto de generación y base para la fase 2 · fuente candidata; validar disponibilidad y esquema en la entrega 2 |
| Demanda de energía del SIN | XM / SIMEM | Balance entre oferta y demanda · fuente candidata; validar disponibilidad y esquema en la entrega 2 |
| Capacidad efectiva / composición del parque | XM / SIMEM | Contexto de la dependencia hídrica · fuente candidata; validar disponibilidad y esquema en la entrega 2 |

# **8\. Procesos (BPMN): situación actual y mejoras**

## **8.1 Proceso AS-IS (situación actual)**

Hoy el monitoreo de reservas hídricas es un proceso manual que depende del analista de datos. Una vez por semana, o cuando la gerencia lo solicita, el analista descarga los reportes de XM en Excel, los consolida en una hoja de cálculo y los revisa a ojo, sin reglas de calidad. Si según su criterio el nivel de los embalses es preocupante, envía un correo con el reporte adjunto; si no, el reporte se archiva. La Gerencia y el Comité de riesgo revisan el reporte días después y deciden en reunión, sin dejar registro de la decisión ni de los datos que la motivaron.

![BPMN AS-IS](documentacion/Diagramas/BPMN_AS-IS_HidroData.png)

*Figura 1\. BPMN AS-IS. Los marcadores P1–P6 señalan los puntos de dolor.*

## **8.2 Puntos de dolor identificados**

| \# | Punto de dolor |
| :---- | :---- |
| P1 | Descarga manual y periódica: el dato llega con retraso y depende de que alguien se acuerde de hacerlo |
| P2 | Consolidación en hoja de cálculo sin trazabilidad: no se sabe de dónde viene cada cifra ni qué se transformó |
| P3 | Revisión sin reglas de calidad: los errores pasan al reporte o se corrigen a mano sin registro |
| P4 | Criterio de riesgo subjetivo: no hay umbrales definidos ni un responsable que los apruebe |
| P5 | Revisión tardía: la gerencia ve el reporte días después, cuando la situación ya pudo haber cambiado |
| P6 | Decisión no documentada: no queda registro de qué se decidió ni con qué datos |

## **8.3 Mejoras del proceso TO-BE**

El proceso TO-BE (véase la Figura 2 y la imagen adjunta) automatiza el monitoreo y lo pone bajo gobierno de datos. Cada mejora (M1–M6) responde a uno o más puntos de dolor y se conecta con un objetivo estratégico de la sección 4\.

| Mejora | AS-IS (problema) | TO-BE (solución) | Objetivo |
| :---- | :---- | :---- | :---- |
| M1 · Ingesta programada | Descarga manual semanal (P1) | Extracción automática diaria a las 6:00 a.m. desde la API XM (Sinergox) a la capa raw | O1 |
| M2 · Validación de calidad | Revisión a ojo, sin reglas (P3) | Reglas de calidad automáticas y registro de métricas en cada ejecución | O3 |
| M3 · Gestión de incidentes | Errores sin detectar o corregidos sin registro (P3) | El Data Steward revisa cada incidente y lo corrige o aprueba con nota | O3 |
| M4 · Indicadores y linaje | Consolidación en Excel sin trazabilidad; revisión tardía (P2, P5) | Cálculo automático de indicadores, registro de linaje y publicación diaria del dashboard | O1, O4 |
| M5 · Alerta automática | Criterio subjetivo y correo manual (P4) | Umbral de riesgo aprobado por el Data Owner y alerta automática por correo (Power Automate) | O2 |
| M6 · Decisión registrada | Decisión en reunión sin documentar (P6) | El comité analiza escenarios en el dashboard y registra su decisión de forma trazable | O4 |

# **9\. Arquitectura de la solución (ArchiMate)**

La arquitectura se modela en tres capas (véase la Figura 3 y la imagen adjunta). La capa de negocio muestra los roles del Data Office, el proceso de monitoreo y el servicio de alerta de riesgo hídrico que recibe la Gerencia. La capa de aplicación contiene los componentes del pipeline (ingesta, validación, transformación, dashboard y flujo de alertas) y los objetos de datos que producen. La capa de tecnología reúne las fuentes externas (API XM, SIMEM, datos.gov.co), Python, el repositorio GitHub, la herramienta de visualización y Microsoft 365 / Power Automate.

**Justificación:** se eligió una arquitectura por capas de datos (raw → validado → curado) porque separa el dato original del dato transformado. Esto permite reprocesar desde la fuente, medir la calidad en cada paso y reconstruir el linaje completo desde la fuente hasta el dashboard, que es un requisito del modelo de gobierno. Además, todas las herramientas son gratuitas o de uso institucional (Python, GitHub, Microsoft 365), lo que hace la solución realista y reproducible sin depender de una nube.

**10\. Evidencia y alcance de la primera entrega**

Esta entrega define y modela la propuesta. La automatización, las reglas de calidad ejecutadas, el pipeline y el dashboard funcional corresponden a entregas posteriores. Las horas y los umbrales son metas de diseño sujetas a validación con la fuente y a aprobación del Data Owner; no se presentan como resultados medidos.

**10.1 Fuente abierta principal**

Reservas Hidráulicas en Energía, identificador 9h36-6mfa, publicado en Datos Abiertos Colombia. El conjunto describe el volumen útil diario y total de los embalses expresado en energía para generación en el SIN. URL: https://www.datos.gov.co/dataset/Reservas-Hidr-ulicas-en-Energ-a/9h36-6mfa. Antes de implementar el pipeline se deben revisar el esquema, la granularidad, la frecuencia real de actualización y las condiciones de descarga. Los demás conjuntos de la sección 7 son candidatos complementarios, no fuentes ya integradas.

**10.2 Correspondencia de artefactos**

| Requisito de la entrega 1 | Evidencia |
| :---- | :---- |
| Problema, necesidad, estrategia y Data Office | Secciones 1 a 6 |
| Selección de datos abiertos | Secciones 7 y 10.1; fuente principal identificada |
| BPMN del proceso y mejoras | Figura 1 suministrada; secciones 8.1 a 8.3; Figura 2 |
| Boceto ArchiMate | Sección 9 y Figura 3 |

**10.3 Contexto sectorial y extensión histórica**

Como contexto externo, XM informó que al 31 de agosto de 2026 el embalse agregado del sistema cerró en 79,36 % de su volumen útil y que los aportes hídricos completaron cuatro meses consecutivos por debajo de la media histórica. Estas cifras corresponden al SIN, no a resultados de HidroCol, que es una organización hipotética. Fuente: XM, comunicado del 16 de septiembre de 2026, https://www.xm.com.co/noticias/9548-en-agosto-los-embalses-de-energia-del-pais-cerraron-en-un-7936.  
El período de análisis acordado es 2022–2026, con 2026 hasta la última fecha disponible en la fuente al momento de extraer los datos. Compararemos reservas por embalse y región, además de aportes cuando la fuente lo permita. Antes del análisis se comprobarán los días cubiertos, la continuidad de la serie y cualquier cambio de unidad o identificación de embalses.  
El futuro catálogo deberá definir embalse, región, operador, capacidad y unidad, según los atributos disponibles en fuentes oficiales. El Data Steward documentará esas definiciones y el Data Owner las aprobará en la segunda entrega.  
El proyecto se centra en el monitoreo y las alertas internas de HidroCol con datos de 2022–2026. Una eventual ampliación a un portal público, reportes regulatorios o recomendaciones de despacho necesitaría otro alcance y una revisión de responsables, fuentes y arquitectura.

**10.4 Organización y riesgos de ejecución**

Se propone un comité mensual con el CDO y el Data Owner para aprobar políticas y criterios de riesgo. En ciclos de dos semanas, el custodio técnico se encarga de la ingesta, el Data Steward revisa incidencias y definiciones, y el analista prepara indicadores. Es la forma de trabajo prevista para HidroCol, no una estructura existente.  
La continuidad de la fuente es el primer riesgo: si la descarga falla, se conservará la última extracción con su fecha y se evaluará otra ruta oficial. Los cambios de nombre, capacidad o unidad de los embalses se documentarán con su vigencia. Antes de usar cifras externas se compararán fecha, cobertura y unidad con el conjunto de trabajo. Como HidroCol es hipotética, sus tiempos de decisión y resultados operativos se presentarán como metas, no como mediciones.  
Referencia adicional de XM para aportes hídricos y su comparación con la media histórica: https://sinergox.xm.com.co/hdrlg/Paginas/Informes/DetalleAportesHidricos.aspx.

**Figura 2\. BPMN TO-BE**

![BPMN TO-BE](documentacion/Diagramas/BPMN_TO_BE_HidroData.png)  
Propuesta M1–M6, con gestión de excepciones de calidad y decisión registrada.

**Figura 3\. Boceto ArchiMate**

![ARCHIMATE](documentacion/Diagramas/ArchiMate_Boceto_HidroData.png)  
Capas de negocio, aplicación y tecnología con trazabilidad desde la fuente hasta la decisión.

