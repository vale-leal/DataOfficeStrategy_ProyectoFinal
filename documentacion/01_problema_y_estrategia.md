# 01 · Problema, necesidad de negocio y estrategia

**Solución:** HidroData SIN · **Versión:** v0.1.0 · **Rúbrica:** 1. Problema, estrategia y diseño organizacional (10 %)

---

## 1. Contexto

**HidroCol Generación S.A. E.S.P.** es una empresa hipotética de generación de energía que opera dentro del Sistema Interconectado Nacional (SIN). Su parque es mayoritariamente hidráulico, por lo que su capacidad de generar y su exposición al riesgo de desabastecimiento dependen del nivel de los embalses y de los aportes hídricos, que varían con fenómenos climáticos como El Niño y La Niña. Colombia vivió un racionamiento eléctrico en 1992–1993 por esta misma vulnerabilidad, y cada temporada seca vuelve a poner el tema en la agenda del sector.

**XM** opera el SIN y administra el mercado mayorista; su portal **Sinergox** publica las variables del sistema que HidroCol necesita monitorear.

## 2. Problema de negocio

HidroCol gestiona el riesgo hídrico de forma **reactiva**. El monitoreo depende de descargas manuales desde XM, revisiones esporádicas y reportes sin reglas de calidad ni trazabilidad:

- El estado de los embalses se conoce con días de retraso.
- Errores en los datos pueden llegar sin detectarse a los reportes de la gerencia.
- No hay un criterio único ni documentado de cuándo una situación hídrica es un riesgo.
- Las decisiones del comité no quedan registradas ni se trazan hasta los datos que las motivaron.

> **Enunciado:** HidroCol no tiene visibilidad oportuna y confiable del estado de sus reservas hídricas, lo que retrasa la detección del riesgo de racionamiento y la toma de decisiones.

## 3. Necesidad de negocio

La Gerencia de Energía y el Comité de riesgo hídrico necesitan conocer **cada día**, con datos validados, el estado de reservas y aportes del SIN, y recibir una **alerta temprana** cuando se superan los umbrales de riesgo, para decidir a tiempo y dejar constancia.

| Usuario | Necesidad | Decisión que soporta |
|---|---|---|
| Gerencia de Energía / Comité de riesgo | Estado diario validado y alerta temprana | Acciones ante riesgo hídrico |
| Planeación Energética (Data Owner) | Definiciones y umbrales aprobados | Criterio único de riesgo |
| Data Steward | Reglas de calidad y gestión de incidentes | Aprobar o corregir datos |
| Analista de datos | Dataset curado y trazable | Indicadores y dashboard |

## 4. Estrategia de datos

**Misión del Data Office:** garantizar que las decisiones de gestión del riesgo hídrico se tomen con datos oportunos, confiables y trazables, a partir de la fuente oficial del sector (XM — Sinergox).

### 4.1 Objetivos estratégicos y metas

| # | Objetivo | KPI | Meta |
|---|---|---|---|
| O1 | Visibilidad diaria del estado de embalses y aportes | Hora de actualización del dashboard | Antes de las 7:00 a. m., todos los días |
| O2 | Detección temprana del riesgo hídrico | Tiempo entre superación del umbral y envío de alerta | < 24 horas |
| O3 | Confiabilidad del dato para decidir | % de registros que cumplen reglas de calidad | ≥ 98 % |
| O4 | Decisiones trazables | % de alertas con decisión registrada por el comité | 100 % |

### 4.2 Alcance por fases

- **Fase 1 (este proyecto):** visibilidad operativa y alertas — ingesta automatizada, validación de calidad, indicadores, dashboard y alerta por correo, bajo gobierno de datos formal.
- **Fase 2 (evolución):** predictibilidad de la generación; con el histórico curado se podrán construir proyecciones a 30 días. La fase 1 es el habilitador de la fase 2.

### 4.3 Justificación

Se prioriza la visibilidad operativa porque es la necesidad más inmediata y construye la base confiable que cualquier análisis predictivo necesita. Invertir primero en gobierno y calidad evita construir pronósticos sobre datos sin validar.

### 4.4 Cómo el dato se convierte en decisión

Cada mañana se responde: *¿qué cambió en las reservas, dónde ocurrió y exige revisión del comité?*

| Rol | Contribución |
|---|---|
| Data Owner | Aprueba definiciones y umbrales |
| Data Steward | Revisa los datos que no pasan las reglas |
| Custodio técnico | Conserva la extracción original y registra transformaciones |
| Analista | Publica indicadores |
| Comité de riesgo | Decide y deja constancia de datos y versión del tablero usados |

Así se puede reconstruir por qué se emitió una alerta y qué se hizo después.

> Las metas de 4.1 son **criterios propuestos**, no desempeño actual de una empresa real.

### 4.5 Qué se valida antes de implementar (guía de la 2.ª entrega)

| Frente | Verificación |
|---|---|
| Cobertura | Primera y última fecha entre 2022 y 2026, días faltantes, granularidad por embalse y región |
| Definiciones | Significado de volumen útil, unidades publicadas, si la capacidad de referencia cambia en el periodo |
| Calidad | Duplicados por fecha y embalse, nulos, rangos válidos, consistencia entre registros diarios y agregados |
| Oportunidad | Cuándo publica realmente Sinergox el dato, antes de prometer la actualización de las 7:00 a. m.; alternativa si la extracción falla |
| Uso para decidir | Acordar con Planeación Energética umbrales y qué registra el comité al cerrar cada caso |

## 5. Preguntas analíticas guía

| ID | Pregunta | Variables |
|---|---|---|
| P1 | ¿Cuál es el estado diario de las reservas frente a su historia 2022–2026? | Reservas |
| P2 | ¿Qué tendencia muestran los aportes frente a la media histórica? | Aportes |
| P3 | ¿Qué umbral de reservas y aportes define un riesgo que exige revisión? | Reservas, aportes |
| P4 | ¿Cómo se relacionan vertimientos y precio de bolsa con la situación hídrica? | Vertimientos, precio, reservas |
| P5 | ¿Qué holgura hay entre capacidad, generación y demanda? | Capacidad, generación, demanda |
| P6 | ¿Qué proporción de los datos cumple las reglas de calidad? | Todas |

## 6. DOFA

| | **Positivo** | **Negativo** |
|---|---|---|
| **Interno** | **F:** fuente oficial y abierta; 4+ años de serie; proceso claro para automatizar; herramientas gratuitas o institucionales | **D:** empresa hipotética sin línea base medida; equipo de 3; umbrales de riesgo aún sin aprobar |
| **Externo** | **O:** alerta de temporadas secas; API y portal de XM; interés sectorial en riesgo climático | **A:** cambios de formato o publicación en Sinergox; revisiones de datos; series afectadas por eventos atípicos |

## 7. Riesgos de ejecución

| Riesgo | Mitigación |
|---|---|
| Falla o cambio de la fuente | Conservar la última extracción con su fecha; evaluar otra ruta oficial |
| Cambios de nombre, capacidad o unidad de embalses | Documentar con su vigencia en el catálogo |
| Cifras externas no comparables | Comparar fecha, cobertura y unidad con el conjunto de trabajo antes de usarlas |
| Promesa de las 7:00 a. m. sin sustento | Medir la publicación real y ajustar la meta |
| Reparto desigual del trabajo | Issues asignados, PR con revisión cruzada |

## 8. Contexto sectorial (referencia externa)

Según su documento de entrega, XM informó que al 31 de agosto de 2026 el embalse agregado del sistema cerró en 79,36 % del volumen útil y que los aportes completaron cuatro meses consecutivos por debajo de la media histórica (comunicado de XM del 16 de septiembre de 2026, <https://www.xm.com.co/noticias/9548-en-agosto-los-embalses-de-energia-del-pais-cerraron-en-un-7936>). Son cifras del SIN, no de HidroCol; **verificar fecha, cobertura y unidad** antes de compararlas con el conjunto de trabajo.

## 9. Fuera de alcance

Portal público, reportes regulatorios y recomendaciones de despacho: requerirían otro alcance y revisión de responsables, fuentes y arquitectura.
