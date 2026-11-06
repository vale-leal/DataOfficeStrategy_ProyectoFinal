  
**1\. Definición de Roles y Distribución en Lanes**  
**Área de Negocio (Solicitante/consumidor):** Garantiza que cada desarrollo responda a una necesidad analítica con valor directo para la organización. Este lane esta reflejado de color verde. El ciclo de vida del dato no debe nacer desde la técnica, sino desde la demanda de valor de negocio. Colocar al consumidor al inicio asegura que la creación de un producto de datos responda a un caso de uso con retorno de inversión (ROI) justificado, evitando la proliferación de pipelines huérfanos sin dueño funcional. 

**Data Office / Data Steward (Gobierno y Calidad):** Encargado del juicio estratégico y de la calidad contextual. Evita que datos no procesados adecuadamente lleguen a producción. Este lane está representado con el color rosado durante todo el flujo. Actúa como la entidad de control y custodia. Se ubica en este nivel para ejercer soberanía sobre el ciclo de vida del dato. Su responsabilidad no es codificar pipelines, sino garantizar que la información cumpla con los estándares de privacidad, normatividad, clasificación de confidencialidad y relevancia de negocio antes y después del procesamiento técnico. 

**Ingeniería de Datos (Soporte Técnico):** Interviene únicamente ante incidentes técnicos complejos o ajustes de código (Resolver incidente técnico, Ajustar reglas de transformación), optimizando el tiempo del equipo técnico. Este lane está representado con el color azul durante todo el flujo. Aísla el trabajo operativo y correctivo de bajo nivel. El equipo técnico no aprueba requerimientos de negocio ni define políticas de calidad; su rol se restringe a resolver incidentes de infraestructura o reconfigurar reglas de transformación cuando los algoritmos detectan desviaciones. Esto evita que los ingenieros asuman roles de decisión funcional que no les corresponden. 

**Plataforma / Sistema (Orquestación Automatizada):** Ejecuta las tareas automáticas etiquetadas con \[AUTO\] (Ingesta y extracción, Pruebas de calidad, Catalogar metadatos, Publicar producto), visibilizando el nivel de automatización del proceso. Este lane está representado con el color morado durante todo el flujo. Agrupar las tareas computacionales en esta franja visibiliza la capacidad de la organización para desacoplar la ejecución determinista del juicio humano, reduciendo la variabilidad operativa y el error manual mediante pipelines auto-orquestados 

**2\. Fundamento de Decisiones y Uso de Compuertas (Gateways)**  
**Compuerta Exclusiva (XOR \-** ¿Aprobar solicitud?**):** Filtro inicial que decide de forma mutuamente excluyente si la solicitud es viable para desarrollo o si se rechaza formalmente (Notificar rechazo). Lógicamente es imposible continuar el aprovisionamiento técnico si la solicitud no supera el filtro de viabilidad y normatividad de gobierno.

**Compuertas Paralelas (AND \-** \+**):** Una vez que sacamos los datos, podemos revisar su calidad y registrar su información técnica al mismo tiempo, ya que no dependen la una de la otra. Hacer estas dos tareas en paralelo nos ahorra mucho tiempo de espera y acelera la entrega final. Al terminar, simplemente volvemos a unir todo para asegurar que los reportes consolidados estén listos y completos.

**Compuerta Inclusiva (OR \-** O**):** Dependiendo de para qué sirva cada producto de datos, puede necesitar una, varias o todas las reglas de calidad a la vez, como revisar si la información está fresca, completa, duplicada o bien estructurada. Usar una compuerta OR permite activar solo las reglas que hacen falta en cada caso, manteniendo el proceso flexible y sin trabas.

**Compuerta Exclusiva (XOR \- Evaluadora de Score de Calidad):** Clasifica el producto en 3 rutas mutuamente excluyentes según el resultado numérico. Si el puntaje de calidad es menor al 70%, el sistema bloquea los datos y los desvía automáticamente a un entorno de pruebas aislado. Esto se hace por seguridad, para evitar que la información defectuosa avance y altere los análisis o los reportes de las capas superiores del negocio.

Cuando la calificación se encuentra en un rango intermedio, entre el 70% y el 94%, se activa un ciclo de revisión. El sistema envía una alerta con los errores detectados al equipo de ingeniería de datos para que ajusten las reglas de transformación, corrijan la información y la vuelvan a procesar hasta que cumpla con los estándares.

Finalmente, si los datos alcanzan una nota excelente de 95% o más, reciben una aprobación definitiva. En este punto, la información se publica de forma directa en el catálogo de datos general, quedando lista, limpia y disponible para que cualquier usuario de la empresa pueda consumirla en la modalidad de autoservicio.

**3\. Componentes Manuales vs. Automatizables**  
**Tareas Manuales:** áreas como el llenado de datos, la evaluación de viabilidad y la revisión de reportes no se pueden delegar por completo a un algoritmo. Estas decisiones necesitan que una persona analice el contexto del negocio, evalúe el impacto de regulaciones como GDPR o Habeas Data, y mida los riesgos del proyecto. Del mismo modo, cuando ocurre un incidente técnico o se necesitan ajustar las reglas, los ingenieros de datos deben intervenir manualmente para corregir código, ajustar consultas en SQL o Python, y reconfigurar las conexiones de la infraestructura. 

**Tareas Automatizadas (**\[AUTO\]**):** Procesos como la ingesta de datos, las pruebas de calidad, la catalogación y la publicación final son tareas estructuradas y repetitivas que se rigen por reglas lógicas ya definidas. Al dejar que un software orquestador las ejecute de forma automática, aseguramos que siempre den el mismo resultado ante los mismos datos, generamos un registro claro para auditorías y eliminamos por completo los errores o descuidos humanos. Son procesos deterministas y repetitivos ejecutados por la plataforma analítica (ej: Apache Airflow, AWS Step Functions), lo que elimina errores humanos y acelera la ejecución.

**4\. Gestión de Errores, SLAs y Tabla de Estados Finales**  
Por una parte, está la captura automática de fallos técnicos. Si el proceso de ingesta y extracción de datos encuentra un error de conectividad o una falla en la infraestructura, un sensor de tiempo detecta el problema de inmediato. Esto desvía la situación hacia el equipo de ingeniería de datos para que resuelvan el incidente técnico sin detener todo el sistema.

Por otra parte, se incluye un temporizador de límite de 48 horas para cumplir con los acuerdos de servicio (SLA). Una vez que el reporte de calidad está listo, el sistema otorga un plazo máximo de dos días para que el responsable de los datos (*Data Steward*) haga su revisión. Si este tiempo expira, el flujo avanza automáticamente a la siguiente etapa de evaluación de calidad, evitando que el proceso se quede estancado indefinidamente.

**5\. Mitigación de Riesgos de Datos**  
**Evitar datos corruptos o dañados:** Colocamos una barrera de control automática justo antes de publicar la información. Si los datos vienen vacíos o con errores de formato, el sistema los frena de inmediato. Así aseguramos que la información incorrecta nunca llegue a los reportes de los directivos. 

**Saber siempre de dónde viene la información:** Al mismo tiempo que recibimos los datos, el sistema registra automáticamente su origen, los cambios que sufre y hacia dónde va. Esto nos da un mapa completo de su camino, lo que facilita cualquier auditoría o revisión legal sin tener que adivinar de dónde salió el dato.

**Prevenir el desorden y la duplicidad:** Antes de aprobar cualquier espacio de datos, le pedimos al responsable del gobierno (*Data Steward*) que dé su visto bueno. Esto evita que la plataforma se llene de archivos duplicados, abandonados o sin un dueño claro que se haga cargo de ellos.

**6\. Oportunidades de Mejora (Mayor Madurez Organizacional)**  
**Control automático de reglas:**  Mi propuesta es reemplazar la evaluación manual de solicitudes y la revisión estática del Data Steward por un motor de políticas declarativas integradas directamente en el pipeline de CI/CD (ej: usando Open Policy Agent \- OPA). Esto permitiría verificar automáticamente si una solicitud cumple con las normativas de seguridad y privacidad sin intervención humana, transformando la gobernanza en un habilitador automatizado y descentralizado.

**Monitoreo inteligente para evitar cambios de lógica:**La idea es evolucionar los controles de calidad tradicionales (que solo miden porcentajes fijos) hacia un sistema de monitoreo activo basado en inteligencia artificial. Este sensor analizará cómo viajan los datos y aprenderá su comportamiento. Si un sistema de origen cambia la forma en que calcula un dato (alterando su significado de negocio), el sistema detectará esta variación y avisará a los usuarios antes de 

**Orquestación inteligente basada en costos:** Vincular la ejecución del pipeline y las pruebas de calidad a un controlador dinámico de costos en la nube. El sistema identificará qué tan importante es cada reporte: si es una tarea crítica del negocio, le asignará los mejores servidores para que corra rápido; si es un análisis secundario, usará servidores económicos o muestras más pequeñas de datos. De esta forma, el control de calidad se adapta al presupuesto y evita gastos innecesarios de infraestructura. 

**Tabla de Estados Finales del Proceso**

| Estado Final | Tipo de Evento Fin | Causas y Significado Operativo |
| :---: | :---: | :---: |
| **Solicitud rechazada por gobierno** | Fin de Cancelación/Rechazo | La solicitud no cumple con criterios de factibilidad, valor de negocio o políticas de privacidad. |
| **Cancelado por fallo técnico** | Fin por error / excepción | El pipeline de ingesta o extracción sufrió un colapso no recuperable en la infraestructura y la tarea de resolución técnica no logró restablecer el servicio. |
| **En cuarentena por mala calidad** | Fin por Contención de riesgo | El dataset obtuvo un score de calidad crítico (\< 70%), quedando aislado en sandbox para evitar contaminación del catálogo oficial.  |
| **Producto publicado exitosamente** | Fin Exitoso | El producto superó las pruebas de calidad (≥ 95%), fue catalogado con sus metadatos y quedó disponible en la plataforma de autoservicio. |

