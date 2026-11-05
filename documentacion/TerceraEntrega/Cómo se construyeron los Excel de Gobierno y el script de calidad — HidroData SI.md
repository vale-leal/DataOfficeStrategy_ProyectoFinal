# Cómo se construyeron los Excel de Gobierno y el script de calidad — HidroData SIN

Oct 28, 2026 · @Rafael

## Resumen

Se midió la calidad de las 7 tablas de XM del proyecto con 6 reglas cada una (una por dimensión de calidad), sobre los archivos completos descargados el 28/09/2026. Las 4 tablas pequeñas se midieron con fórmulas de Excel y las 3 grandes con un script de Python. Con esos resultados se actualizó el Plan de Gobierno a la versión 0.3.

Este documento explica cómo se hizo cada cosa, para que alguien pueda revisarla o repetirla sin haber estado en la conversación.

**Archivos entregados**

| Archivo | Qué es | Cómo se generó |
| --- | --- | --- |
| `S2_Gobierno_EquipoX_DS01_Aportes.xlsx` | Plantilla de Gobierno de la profe, llena para Aportes | Fórmulas de Excel sobre los datos completos |
| `S2_Gobierno_EquipoX_DS02_Reservas.xlsx` | Igual, para Reserva diaria | Fórmulas de Excel |
| `S2_Gobierno_EquipoX_DS03_Vertimientos.xlsx` | Igual, para Vertimientos | Fórmulas de Excel |
| `S2_Gobierno_EquipoX_DS04_Demanda.xlsx` | Igual, para Demanda | Fórmulas de Excel |
| `S2_Gobierno_EquipoX_DS05_Generacion.xlsx` | Igual, para Generación | Números calculados en Python y pegados en la hoja |
| `S2_Gobierno_EquipoX_DS06_Capacidad.xlsx` | Igual, para Capacidad | Python |
| `S2_Gobierno_EquipoX_DS07_ComprasBolsa.xlsx` | Igual, para Compras en bolsa | Python |
| `calidad_tablas_grandes.py` | Script que mide las reglas de las 3 tablas grandes | — |
| `metricas_calidad_grandes.csv` | Salida del script: una fila por regla | Lo genera el script |
| `Plan_Gobierno_Datos.md` (v0.3) | Plan de Gobierno actualizado | Edición de la v0.2.2 con los resultados |

Cada Excel tiene las 4 hojas de la plantilla: `1_Calidad` (scorecard), `2_Seguridad` (clasificación y acceso), `3_Maestros` (datos maestros) y `4_Datos` (los datos o la evidencia).

## Decisiones de diseño

**1. Se mide la capa raw, no los parquet.** Los datos son los Excel originales de XM, sin pasar por el pipeline. Los parquet de Vale son la capa normalizada: ya tienen nombres cambiados y algunos valores corregidos (por ejemplo, el negativo de QUEBRADONA está imputado). Medir el raw muestra la calidad con la que llega la fuente; el pipeline se presenta como la medida correctiva. Se comparó una muestra de 98 filas de Aportes normalizado (enero a marzo de 2022) contra el raw: los valores son idénticos y el pipeline solo agrega columnas como `dato_no_registrado`. Las correcciones del pipeline caen fuera de esa muestra.

**2. Un Excel por tabla.** La profe pidió 7 archivos, uno por tabla. Cada uno mide 6 reglas, una por dimensión: completitud, validez, exactitud, consistencia, unicidad y oportunidad. Las reglas se tomaron del Plan de Gobierno (§7) con su código (A-01, R-04, GN-03…).

**3. Excel donde cabe, Python donde no.** El corte salió de contar las filas de cada tabla:

| Tabla | Filas | Método | Motivo |
| --- | --: | --- | --- |
| DS-01 Aportes | 2.268 | Fórmulas de Excel | Cabe y calcula |
| DS-02 Reserva | 1.731 | Fórmulas de Excel | Cabe y calcula |
| DS-03 Vertimientos | 3.989 | Fórmulas de Excel | Cabe y calcula |
| DS-04 Demanda | 1.730 | Fórmulas de Excel | Cabe y calcula |
| DS-05 Generación | 505.643 | Python | Cabe, pero la regla de unicidad compara cada fila contra todas y Excel no termina de calcularla |
| DS-06 Capacidad | 1.383.086 | Python | No cabe: una hoja de Excel admite 1.048.576 filas |
| DS-07 Compras en bolsa | 199.213 | Python | Igual que Generación |

Para que los 7 archivos se vean iguales, en las tablas grandes Python calcula solo los «registros evaluados» y los «que cumplen» (columnas E y F de `1_Calidad`). El porcentaje y el semáforo siguen siendo las fórmulas de la plantilla.

**4. Nombres de columna.** Se usan tres, cada uno en su lugar:

| Dónde | Nombre que va | Ejemplo |
| --- | --- | --- |
| Hoja `4_Datos` | El encabezado original de XM (los datos crudos no se renombran) | `Volumen Útil Diario %` |
| Hoja `1_Calidad`, columna «Columna» | El nombre estándar del Plan (§4.1) | `pct_volumen_util_diario` |
| Diccionario del Plan (§6) | Los dos, unidos con una flecha | `Volumen Útil Diario % → pct_volumen_util_diario` |

Los parquet del pipeline usan una tercera forma (`volumen_util_diario_pct`, `ano`, `aportes_caudal_m3_s`) que no coincide con el estándar. Está anotado como pendiente P16 del Plan; no afecta los Excel.

## De dónde salen los datos

Todo sale de un solo archivo del repositorio: `datos/raw/HidrologiaYGeneracionEnergetica_7065.rar` (rama `main`, guardado con Git LFS, unos 158 MB). Es la descarga de Sinergox del 28/09/2026. Al descomprimirlo queda esta estructura, con 5 archivos anuales (2022 a 2026) por carpeta:

```
HidrologiaYGeneracionEnergetica/
├── Aportes/       Aportes_Mensual_AAAA.xlsx
├── Reservas/      Reservas_Diario_SIN_AAAA.xlsx
├── Vertimentos/   Vertimientos_Diario_AAAA.xlsx (2025 y 2026: Vertimentos_…)
├── Demanda/       Demanda_Energia_SIN_AAAA.xlsx
├── Generacion/    Generacion_(kWh)_AAAA.xlsx
├── Capacidad/     Capacidad_Efectiva_Neta_(kW)_AAAA.xlsx
└── Precio/        Compras_Bolsa_Nacional_(kWh)_AAAA.xlsx
```

**Cómo se unieron los 5 años de cada tabla.** Cada Excel de XM trae unas filas de título antes de los encabezados, y no siempre en la misma fila. El procedimiento fue:

1. Leer cada archivo sin encabezado (con `pandas` y el motor `calamine`, que es rápido para archivos grandes).
2. Buscar la fila cuya primera celda dice «Fecha» (o «Año» en Aportes) y usarla como encabezado.
3. Quitar filas y columnas totalmente vacías y agregar una columna `archivo_origen` con el nombre del archivo.
4. Unir los 5 años uno debajo del otro.

No se cambia ningún valor. Los números ya vienen guardados como número en los `.xlsx`: el formato colombiano (punto para miles, coma para decimales) es solo de visualización. Se comprobó que 0 de 18.331.597 valores numéricos vienen como texto.

**Atención con WinRAR / 7-Zip:** el `.rar` usa un método de compresión que `7z` no soporta en Linux y `unar` dejó algunos archivos vacíos. Con `unrar` (o WinRAR en Windows) se extraen bien. Si al descargar el `.rar` pesa pocos bytes, se bajó el puntero de Git LFS y no el archivo real.

## Cómo se construyeron los 7 Excel

Los 7 parten de la plantilla original de la profe (`S2_Plantilla_Gobierno.xlsx`) sin cambiar su estructura: mismas hojas, mismas fórmulas de porcentaje y semáforo, mismas listas desplegables. Se llenaron con un script de Python (`openpyxl`) para no copiar 500.000 filas a mano y para que el resultado sea repetible.

### Hoja por hoja

| Hoja | Qué se llenó | Pequeñas (DS-01 a DS-04) | Grandes (DS-05 a DS-07) |
| --- | --- | --- | --- |
| `0_Instrucciones` | Equipo, integrantes y descripción del dataset | Igual en todas | Igual en todas |
| `1_Calidad` | 6 reglas (filas 6 a 11): columna, dimensión, regla, evaluados (E), cumplen (F), meta (H), causa (J) y acción (K) | E y F son **fórmulas** sobre `4_Datos` | E y F son **números** que da el script; una nota en la fila 14 dice de dónde salen |
| `2_Seguridad` | Clasificación de hasta 8 columnas y la matriz de acceso de 4 roles | Igual en todas | En Generación y Capacidad, `nom_recurso` es dato personal |
| `3_Maestros` | 2 a 3 datos maestros o de referencia de esa tabla | Igual en todas | Igual en todas |
| `4_Datos` | Los datos | **Tabla completa** desde la fila 4, más columnas auxiliares y listas de referencia | **No hay datos**: un perfil de la tabla y el detalle de cada regla medida |

El porcentaje (G) y el semáforo (I) son las fórmulas de la plantilla: verde si cumple la meta, amarillo si está hasta 10 puntos por debajo, rojo si está más abajo. La meta (H) es 100 % en todas las reglas, como dice el Plan.

### Columnas auxiliares en `4_Datos`

Algunas reglas no se pueden contar con una sola fórmula. Para esas se agregó una columna auxiliar, marcada como «(auxiliar)» en su encabezado, a la derecha de los datos:

| Tabla | Columna auxiliar | Fórmula por fila | Para qué regla |
| --- | --- | --- | --- |
| Aportes | K: clave año-mes-río | `=A4&"-"&B4&"-"&D4` (con separador barra) | Unicidad A-05 |
| Reserva | C: variación diaria absoluta | `=ABS(B5-B4)` | Consistencia R-05 |
| Demanda | G: generación sumada de la tabla Generación | Valor calculado en Python (no es fórmula) | Exactitud GN-04 |
| Demanda | H: diferencia relativa con Generación | `=IF(OR(C4="",G4=""),"",ABS(C4/G4-1))` | Exactitud GN-04 |
| Demanda | I: diferencia del balance | `=IF(C4="","",ABS(B4-(C4+F4-E4+D4)))` | Consistencia D-03 |
| Vertimientos | F: razón energía / volumen | `=E4/D4` | Consistencia V-03 |
| Vertimientos | G: clave embalse-mes | `=C4&"-"&YEAR(A4)&"-"&MONTH(A4)` | Consistencia V-03 |
| Vertimientos | H: desvío frente al promedio del embalse en ese mes | `=ABS(F4/AVERAGEIFS(F:F,G:G,G4)-1)` (rangos fijos en el archivo) | Consistencia V-03 |
| Vertimientos | I: clave fecha-embalse | `=A4&"-"&C4` (con separador barra) | Unicidad V-01 |

La columna G de Demanda es la única que no es fórmula: es la suma de las 24 horas de todos los recursos de Generación para ese día, calculada en Python porque Generación no cabe en la hoja.

También hay listas de referencia a la derecha de los datos: los 12 meses en Aportes, las 7 regiones en Vertimientos y la **fecha de descarga (28/09/2026)** en todas, que usan las reglas de validez y oportunidad.

### Fórmulas de `1_Calidad` (columnas E y F)

Los rangos van de la fila 4 a la última fila de datos: 2271 en Aportes, 1734 en Reserva, 1733 en Demanda y 3992 en Vertimientos. Abajo, `D!` abrevia `'4_Datos'!` y los rangos se escriben sin el `$`.

**DS-01 Aportes**

```text
Completitud  A-01  E =COUNTA(D!D4:D2271)            F =COUNT(D!E4:E2271)
Validez      A-03  E =COUNTA(D!B4:B2271)            F =SUMPRODUCT(COUNTIF(D!M4:M15, D!B4:B2271))
Exactitud    A-06  E =COUNT(D!E4:E2271)             F =COUNTIF(D!E4:E2271, ">=0")
Consistencia A-07  E =COUNTIF(D!F4:F2271, ">0")     F =COUNTIFS(D!F4:F2271, ">0", D!E4:E2271, "<>")
Unicidad     A-05  E =COUNTA(D!K4:K2271)            F =SUMPRODUCT((COUNTIF(D!K4:K2271, D!K4:K2271)=1)*1)
Oportunidad  G-05  E =1   F =IF(meses entre la descarga (M18) y el último año-mes de los datos <= 1, 1, 0)
```

**DS-02 Reserva**

```text
Completitud  R-02  E =MAX(fechas)-MIN(fechas)+1     F = número de fechas distintas
Validez      R-03  E =COUNTA(fechas)                F =COUNTIFS(fechas, ">="&E7, fechas, "<="&E4)
Exactitud    R-04  E =COUNT(B)                      F =COUNTIFS(B, ">=0", B, "<=100")
Consistencia R-05  E =COUNT(C)                      F =COUNTIF(C, "<=5")
Unicidad     R-06  E =COUNTA(fechas)                F =SUMPRODUCT((COUNTIF(fechas, fechas)=1)*1)
Oportunidad  G-05  E =1                             F =IF(E4-MAX(fechas)<=2, 1, 0)
```

**DS-03 Vertimientos**

```text
Completitud  V-04  E =COUNTA(A)    F =SUMPRODUCT((B<>"")*(C<>"")*(D<>"")*(E<>""))
Validez      V-05  E =COUNTA(B)    F =SUMPRODUCT(COUNTIF(K4:K10, B))      (lista de regiones)
Exactitud    V-02  E =COUNTA(A)    F =COUNTIFS(D, ">0", E, ">0")
Consistencia V-03  E =COUNT(H)     F =COUNTIF(H, "<=0.01")               (±1 %)
Unicidad     V-01  E =COUNTA(I)    F =SUMPRODUCT((COUNTIF(I, I)=1)*1)
Oportunidad  G-05  E =1            F =IF(K13-MAX(A)<=2, 1, 0)
```

**DS-04 Demanda**

```text
Completitud  D-02  E =COUNTA(A)    F =COUNTIFS(B, "<>", C, "<>")
Validez      D-02  E =COUNTA(A)    F =SUMPRODUCT((B>0)*(D>=0)*(E>=0)*(F>=0))
Exactitud    GN-04 E =COUNT(H)     F =COUNTIF(H, "<=0.001")              (±0,1 %)
Consistencia D-03  E =COUNT(I)     F =COUNTIF(I, "<=1")                  (1 kWh)
Unicidad     D-04  E =COUNTA(A)    F =SUMPRODUCT((COUNTIF(A, A)=1)*1)
Oportunidad  G-05  E =1            F =IF(K4-MAX(A)<=2, 1, 0)
```

Las fórmulas exactas, con sus rangos absolutos, están en cada archivo: basta hacer clic en las celdas E6 a F11. Las reglas de oportunidad usan E = 1 y F = 1 o 0, así que el porcentaje sale 100 % o 0 %.

### Tablas grandes: qué hay en `4_Datos`

En Generación, Capacidad y Compras la hoja `4_Datos` no tiene datos. Tiene la evidencia de la medición: archivos de origen, número de registros, periodo y particularidades de la tabla (por ejemplo, que Generación 2022 y 2023 no traen tres columnas), y una tabla con las 6 reglas medidas: código, dimensión, descripción, evaluados, cumplen, % y detalle. Esos números son los mismos que están en `metricas_calidad_grandes.csv`.

## El script `calidad_tablas_grandes.py`

Mide las 6 reglas de Generación, Capacidad y Compras sobre los archivos crudos completos y escribe un CSV con una fila por regla. Tarda alrededor de 1 minuto. Solo lee: no modifica ningún archivo de datos.

### Cómo correrlo

Requisitos: Python 3.10 o superior y dos paquetes:

```bash
pip install pandas python-calamine
```

Se le pasan la carpeta descomprimida, el nombre del CSV de salida y, opcionalmente, la fecha de descarga:

```bash
python calidad_tablas_grandes.py "RUTA/HidrologiaYGeneracionEnergetica" metricas_calidad_grandes.csv 2026-09-28
```

Sin argumentos (por ejemplo, con el botón ▶ de VS Code) usa la ruta escrita en `RAIZ_POR_DEFECTO`, justo antes de `main()`, que es la del computador de Rafael. En otro computador hay que cambiarla o pasar la ruta como argumento.

El script avisa si la carpeta no tiene las subcarpetas esperadas, y si el CSV está abierto en Excel lo guarda con otro nombre en vez de fallar.

### Qué hace, paso a paso

1. **Lee** las carpetas `Demanda`, `Generacion`, `Capacidad` y `Precio` con la función `leer()`, que es la misma consolidación descrita arriba (busca la fila «Fecha» y une los 5 años).
2. **Generación** (`generacion()`): convierte las 24 columnas horarias a número y mide las reglas. Para GN-04 suma las 24 horas de todos los recursos por día y compara con la columna «Generación kWh» de Demanda.
3. **Capacidad** (`capacidad()`): mide las reglas. Para CP-04 toma la hora de mayor generación de cada recurso en cada día y la cruza por fecha y nombre de recurso con su capacidad de ese día.
4. **Compras** (`compras()`): une las columnas «Versión» (2022–2025) y «Version» (2026), y mide las reglas.
5. **Guarda** `metricas_calidad_grandes.csv` y un `metricas_calidad_grandes.perfil.json` con el perfil de cada tabla, e imprime la tabla de resultados.

### Las reglas que mide

| Tabla | Regla | Dimensión | Qué cuenta como «cumple» |
| --- | --- | --- | --- |
| Generación | GN-01 | Completitud | Fila con las 24 horas con valor |
| Generación | GN-02a | Validez | Tipo de generación en {HIDRAULICA, TERMICA, SOLAR, EOLICA, COGENERADOR} |
| Generación | GN-02b | Exactitud | Celda horaria ≥ 0 (sobre las celdas con valor) |
| Generación | GN-04 | Consistencia | Día cuya suma difiere 0,1 % o menos de la generación de Demanda |
| Generación | GN-03 | Unicidad | Fila única por fecha + recurso + agente + versión + **combustible** |
| Generación | G-05 | Oportunidad | Último día con 2 días o menos de rezago frente a la descarga |
| Capacidad | CP-01 | Completitud | Fila sin vacíos en los 9 campos |
| Capacidad | CP-02a | Validez | «Es Menor» en {SI, NO} |
| Capacidad | CP-02b | Exactitud | Capacidad > 0 kW |
| Capacidad | CP-04 | Consistencia | Recurso-día cuya hora máxima de generación es ≤ capacidad × 1,05 |
| Capacidad | CP-03 | Unicidad | Fila única por fecha + recurso + agente |
| Capacidad | G-05 | Oportunidad | Igual que en Generación |
| Compras | B-04 | Completitud | Fila con las 24 horas con valor |
| Compras | G-02 | Validez | Fecha válida, desde 2022-01-01 y no posterior a la descarga |
| Compras | B-03 | Exactitud | Celda horaria ≥ 0 (sobre las celdas con valor) |
| Compras | B-05 | Consistencia | Fila cuyo archivo guarda la fecha como fecha y trae la columna «Versión» |
| Compras | B-02 | Unicidad | Fila única por fecha + agente + versión |
| Compras | G-05 | Oportunidad | Igual que en Generación |

Las tolerancias están como constantes al inicio del archivo (`TOLERANCIA_GN04 = 0.001`, `TOLERANCIA_CP04 = 1.05`, `MAX_REZAGO_DIAS = 2`), así que se pueden cambiar en un solo lugar.

### Cómo saber si salió bien

La columna «cumplen» del CSV debe coincidir con la columna F de los Excel. Tres valores de control:

| Regla | Evaluados | Cumplen |
| --- | --: | --: |
| Compras B-04 | 199.213 | 174.123 |
| Generación GN-01 | 505.643 | 505.584 |
| Capacidad CP-04 | 429.689 | 410.391 |

Si no coinciden, lo más probable es que se haya usado otra descarga o que algún archivo se haya extraído vacío (ver la advertencia sobre el `.rar`).

## Cómo se verificó

Las tablas pequeñas se comprobaron por dos caminos distintos; las grandes, revisando a mano los resultados que salían raros:

1. **Las fórmulas calculan sin errores.** Los 7 archivos se recalcularon con LibreOffice: 0 errores (`#N/A`, `#VALUE!`, `#REF!`…) en todas sus fórmulas.
2. **Las fórmulas dan lo mismo que un cálculo independiente.** Cada regla de las 4 tablas pequeñas se volvió a calcular en `pandas`, sin usar el Excel, y los números coinciden (por ejemplo, Vertimientos V-03: 3.983 de 3.989 en ambos).
3. **Los números de Python se revisaron a mano** cuando salían raros. Así se descubrió que las 3.815 «filas duplicadas» de Generación son plantas con dos combustibles, y que el factor energía/volumen de los embalses cambia con los años.
4. **El script se corrió dos veces**, la segunda con la versión que tiene las rutas por defecto, y dio los mismos resultados.
5. **Se revisó cómo se ven las hojas**, exportándolas a PDF, para comprobar que los textos de causa y acción no se cortan.

**Un error encontrado y corregido:** en la hoja `3_Maestros` de Aportes se había escrito que SAN FRANCISCO pasa de CENTRO a CALDAS. Al revisar los datos se vio que es al revés (de CALDAS a CENTRO, en 2025). Ya está corregido en el Excel y en el Plan.

## Resultados por tabla

El promedio de los 7 índices es **91,8 %** frente a una meta de 98 %. Si se quitan las reglas de oportunidad, que dependen de cuándo publica XM y no de la calidad del dato, sube a **98,8 %**.

% de cumplimiento de cada regla (columna G de `1_Calidad`). El índice es el promedio de las 6.

| Tabla | Completitud | Validez | Exactitud | Consistencia | Unicidad | Oportunidad | Índice |
| --- | --: | --: | --: | --: | --: | --: | --: |
| DS-07 Compras en bolsa | 87,41 % | 100 % | 100 % | 81,57 % | 100 % | 0 % (5 días) | 78,2 % |
| DS-01 Aportes | 94,97 % | 100 % | 99,95 % | 97,44 % | 100 % | 0 % (3 meses) | 82,1 % |
| DS-05 Generación | 99,99 % | 100 % | 100 % | 100 % | 100 % | 0 % (3 días) | 83,3 % |
| DS-06 Capacidad | 100 % | 100 % | 100 % | 95,51 % | 100 % | 100 % | 99,25 % |
| DS-03 Vertimientos | 100 % | 100 % | 100 % | 99,85 % | 100 % | 100 % | 99,97 % |
| DS-04 Demanda | 99,94 % | 100 % | 100 % | 100 % | 100 % | 100 % | 99,99 % |
| DS-02 Reserva | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % |

Qué explica cada valor por debajo del 100 %:

- **Compras, completitud y consistencia:** el archivo 2026 cambió de formato. Las horas sin compra vienen vacías en vez de 0 (25.090 filas), la fecha viene como texto y la columna se llama «Version» sin tilde.
- **Aportes, completitud:** 114 meses sin energía, casi todos de 6 ríos (BLANCO y 5 de la región CALDAS).
- **Aportes, exactitud:** un solo valor negativo, QUEBRADONA en junio de 2026 (−676.298,56 kWh). El pipeline lo imputa.
- **Aportes, consistencia:** 56 meses con caudal medido pero sin energía.
- **Capacidad, consistencia:** 19.298 recurso-días en que una planta generó más que su capacidad más 5 %.
- **Vertimientos, consistencia:** 6 registros cuya razón energía/volumen se aleja más de 1 % del promedio del mes.
- **Demanda, completitud:** el último día (26/09/2026) llegó incompleto: 63.850 kWh de demanda y la generación vacía.
- **Oportunidad:** el último dato de Aportes es de junio, el de Generación del 25/09 y el de Compras del 23/09, frente a una descarga del 28/09 y una meta de 2 días.

## Reglas corregidas y cambios al Plan v0.3

Al medir sobre los datos completos, 8 reglas del Plan resultaron mal planteadas: fallaban por cambios legítimos de la fuente o no medían lo que decían. Se corrigieron dejando a la vista la redacción anterior y su resultado.

| Regla | Antes | Después | Por qué se cambió |
| --- | --- | --- | --- |
| A-02 | Cada río tiene un registro por cada mes del periodo completo (91,3 %) | … por cada mes del periodo en que XM lo reporta (99,5 %) | Los ríos entran y salen del reporte: de 42 a 45 por año |
| A-04 | Cada río pertenece a una sola región (90,9 %) | La región está en la lista y los cambios de región se documentan | XM reclasificó 4 ríos (3 a CALDAS en 2023, 1 a CENTRO en 2025) |
| A-07 | Si el caudal es 0, la energía es 0 (0 de 58) | Si el caudal es mayor que 0, la energía está registrada (97,4 %) | XM deja vacía la energía no registrada, no pone 0. La regla vieja no medía nada |
| A-09 | La media histórica es igual todos los años (12,9 %) | Cambia 10 % o menos entre años; los cambios mayores se documentan (98,1 %) | XM recalcula la media cada año; la de CAUCA SALVAJINA se triplica en 2023 |
| V-03 | La razón energía/volumen es constante por embalse (69 %) | Está a ±1 % del promedio del mismo embalse y mes (99,85 %) | XM actualiza el factor de conversión; RIOGRANDE2 bajó cerca de 11 % |
| V-05 | Cada embalse pertenece a una sola región | El embalse está en la lista y los cambios de región se documentan | AMANI pasó de ANTIOQUIA a CALDAS |
| GN-02 | Valores ≥ 0 kW | Valores ≥ 0 kWh | El archivo de XM se titula «Generación (kWh)» |
| GN-03 | Una fila por fecha, recurso, agente y versión | … y combustible | Sin el combustible, 3.815 filas de plantas duales parecían duplicadas |

**Reglas nuevas (7):** B-04 (las 24 horas de Compras tienen valor), B-05 (mismo formato de archivo en todos los años) y TR-01 a TR-05 para `TablaReservas`, la tabla que lee Power Automate. Las 5 de `TablaReservas` se cumplen al 100 %.

**Otros cambios del Plan v0.3:**

- Fichas de catálogo de 17 campos y diccionario completo (valores permitidos, vacíos, ejemplo y sensibilidad por columna) para Vertimientos, Demanda, Generación, Capacidad y Compras.
- `TablaReservas` (`automatizacion/reservas_alerta.xlsx`, rama `eda`) catalogada como activo DS-11, con ficha, diccionario y reglas. Sus umbrales de 50 % y 40 % siguen siendo **propuestos**: los aprueba el Data Owner.
- Hallazgos corregidos: el formato colombiano es solo de visualización (H1); Generación viene en kWh y no en kW (H7); no hay ningún negativo en Compras (H9).
- Hallazgos nuevos H13 a H17: el cambio de formato de Compras 2026, las columnas que faltan en Generación 2022–2023, las reclasificaciones de XM, el último día incompleto de Demanda y la tabla de Power Automate.
- 46 de 49 reglas medidas. Faltan G-04 (manifiesto de descarga), G-06 (tablero antes de las 7:00 a. m.) y V-04 (confirmación de XM).
- Pendientes nuevos P16 a P19.

## Supuestos y qué revisar

### Supuestos que se tomaron

| Supuesto | Dónde pesa | Si cambia |
| --- | --- | --- |
| La fecha de descarga es el 28/09/2026 (la que dice el Plan) | Todas las reglas de oportunidad | Cambiarla en `4_Datos` de cada Excel pequeño y en el tercer argumento del script |
| Rezago máximo de 2 días (G-05, «tentativo» en el Plan) | Generación y Compras salen en rojo | El Data Owner puede fijar una meta propia por tabla (pendiente P19) |
| Tolerancias propuestas: ±1 % (V-03), ±0,1 % (GN-04), 5 % (CP-04), 10 % (A-09) | Consistencia y exactitud | Ninguna está aprobada por el Data Owner (pendiente P5) |
| Meta de 100 % en todas las reglas | El color del semáforo | Es lo que dice el Plan; con 98 % varios amarillos pasarían a verde |
| `nom_recurso` es dato personal (Sí, Uso interno) y `cod_agente` no (identifica a una empresa) | Hojas `2_Seguridad` de Generación y Capacidad | Hay recursos con nombre de persona natural (por ejemplo, «AGPE ALVARO HOYOS»). Pendiente P4: confirmarlo con la docente |
| «DESV.» en los nombres de ríos significa desviación | Diccionario de Aportes | Es una interpretación, no está confirmada por XM |

### Lo que no se pudo verificar

- Que un vacío en Compras 2026 signifique «sin compra» (0). Hay que confirmarlo con XM (P17).
- Por qué 6 ríos tienen caudal pero no energía, y por qué la media histórica de CAUCA SALVAJINA se triplica en 2023 (P1, P17).
- Si el flujo de Power Automate usa otras tablas aparte de `TablaReservas` (destinatarios, alertas enviadas o decisiones). En el repositorio solo existe `TablaReservas`, así que el Plan solo documenta esa.
- El cruce Generación–Capacidad se hizo por nombre de recurso: 74.040 recurso-días no encontraron pareja. Con el código de recurso el resultado de CP-04 podría cambiar (P18).

### Lista de revisión

- [ ] Abrir un Excel pequeño (por ejemplo, Aportes), hacer clic en E6:F11 y comprobar que las fórmulas apuntan a los rangos correctos de `4_Datos`.
- [ ] Correr `calidad_tablas_grandes.py` y comparar el CSV con la columna F de los Excel de Generación, Capacidad y Compras.
- [ ] Leer las reglas corregidas y decidir si la nueva redacción es defendible ante la profe.
- [ ] Revisar las hojas `2_Seguridad`: si se mantiene la decisión sobre `nom_recurso`.
- [ ] Comparar el Plan v0.3 con la v0.2.2 (el «diff» en GitHub muestra todo lo que cambió).
- [ ] Poner el número de equipo en la celda B4 de cada Excel y en el nombre de los archivos (hoy dicen «EquipoX»).

### Si se revisa con Claude

Adjuntar este documento, los 7 Excel, `calidad_tablas_grandes.py`, `metricas_calidad_grandes.csv` y `Plan_Gobierno_Datos.md`. Para correr el script hacen falta los datos crudos (el `.rar` del repositorio). Un pedido que funciona:

> Revisa estos archivos de gobierno de datos. Comprueba que las fórmulas de la hoja 1\_Calidad de cada Excel cuenten lo que dice la regla, que los resultados de las tablas grandes coincidan con el CSV del script y que el Plan v0.3 sea coherente con los Excel. Ordéname los problemas por gravedad.

El script que generó los Excel (`construir_gobierno.py`) y el que consolida los datos crudos (`consolidar.py`) también están disponibles, por si alguien quiere regenerar los archivos desde cero.
