# 04 · Selección de datos abiertos

**Solución:** HidroData SIN · **Versión:** v0.1.0 · **Rúbrica:** 5. Datos (insumo) · 6. Gobierno

---

## 1. Fuente seleccionada: XM — Sinergox

| Atributo | Valor |
|---|---|
| Fuente | **XM S.A. E.S.P. — Sinergox**, portal de información y estadísticas del mercado de energía mayorista |
| URL | <https://sinergox.xm.com.co> |
| Referencia de aportes | <https://sinergox.xm.com.co/hdrlg/Paginas/Informes/DetalleAportesHidricos.aspx> |
| Tipo | Información pública oficial del operador del SIN |
| Periodo | 2022–2026 (2026 hasta la última fecha disponible al extraer) |
| Acceso | Descarga desde el portal; API de XM (`pydataxm`) **por validar** |
| Formato | CSV / XLSX (por confirmar) |
| Uso | Citar siempre a XM/Sinergox |

> ℹ️ El enunciado del curso lista cinco fuentes sugeridas y Sinergox no figura en ella. Es un portal público oficial; conviene **confirmar con la docente** que cumple el requisito de “datos abiertos”.

## 2. Variables seleccionadas

| # | Variable | Rol en HidroData SIN | Prioridad |
|---|---|---|---|
| 1 | **Reservas hídricas** (volumen útil diario y total en energía) | **Fuente principal**: monitoreo de embalses, indicador de riesgo | Núcleo |
| 2 | **Aportes hídricos** (vs. media histórica) | Anticipar tendencia (El Niño / La Niña) | Núcleo |
| 3 | **Vertimientos** | Señal de exceso hídrico; contexto de reservas | Contexto |
| 4 | **Precio de bolsa nacional** | Señal de mercado ante escasez o abundancia | Contexto |
| 5 | **Demanda** del SIN | Balance oferta–demanda | Contexto |
| 6 | **Capacidad efectiva** / composición del parque | Dependencia hídrica del sistema | Contexto |
| 7 | **Generación real** por tipo de recurso | Contexto de generación; base para la fase 2 | Contexto |

> Cobertura, frecuencia, granularidad (por embalse/región), unidades y campos exactos se **validan antes de construir el pipeline** (2.ª entrega). Las variables de contexto no están integradas todavía: son candidatas complementarias.

## 3. Criterios de selección

| Criterio | ¿Cumple? | Justificación |
|---|:---:|---|
| Relevancia | ✅ | Las variables describen el estado hídrico y el balance del sistema |
| Credibilidad | ✅ | Operador oficial del SIN |
| Acceso público | ✅ | Publicado en Sinergox |
| Cobertura temporal | ✅ | 2022–2026, incluye periodos secos y húmedos |
| Ausencia de datos personales | ✅ | Magnitudes agregadas del sistema |
| Volumen manejable | ✅ | Series diarias de pocos miles de filas por variable |

## 4. Modelo de datos objetivo

**Llave de integración:** `fecha` (y `embalse` / `region` cuando la fuente lo permita). **Granularidad objetivo:** diaria.

| Capa | Contenido |
|---|---|
| `raw` | Archivos tal como se extraen, con fecha de extracción |
| `validado` | Registros que pasan reglas de calidad, con métricas |
| `curado` | Dataset integrado con indicadores, listo para el dashboard |

Reglas de agregación previstas: reservas = valor de cierre del día; aportes, vertimientos, demanda y generación = suma diaria; precio de bolsa = promedio diario (definir ponderación al ver la granularidad real); capacidad = valor vigente.

## 5. Riesgos de los datos

| Riesgo | Tratamiento |
|---|---|
| Publicación tardía frente a la meta de las 7:00 a. m. | Medir el rezago real; documentar alternativa si la extracción falla |
| Cambios de nombre, capacidad o unidad de embalses | Registrar con vigencia en el catálogo |
| Duplicados por fecha y embalse, nulos, rangos inválidos | Reglas de calidad (Plan de Gobierno §6) |
| Revisiones posteriores de valores publicados | Guardar fecha de extracción y conservar la extracción original |
| Año 2026 incompleto | Marcar como parcial |
| Falla de la fuente | Conservar la última extracción con su fecha |

## 6. Trazabilidad de cada extracción

| Campo | Ejemplo |
|---|---|
| `archivo` | `reservas_2022_2026.csv` |
| `variable` | Reservas hídricas |
| `fuente_url` | URL del informe en Sinergox |
| `fecha_extraccion` | AAAA-MM-DD hh:mm |
| `responsable` | Custodio técnico |
| `hash_sha256` | Huella de integridad |

## 7. Justificación

Una sola fuente oficial simplifica gobierno, clasificación y linaje. Las reservas y los aportes responden directamente a la necesidad de negocio; las demás variables enriquecen la lectura del sistema y habilitan la fase 2 sin cambiar de fuente.
