---
title: "PRD: MIRA — Incremento Funcional F4 y F1 (Entrega 2)"
status: "final"
created: "2026-10-03"
updated: "2026-10-03"
author: "John (Product Manager — BMAD Method)"
project: "MIRA — Plataforma de Inteligencia Multimodal para Decisiones Empresariales"
organization: "DPRIME SpA / Aseguradora Piloto"
target_increment: "Entrega 2 (F4: Puntaje y Decisión por Umbrales + F1: Bandeja de Revisión Asistida)"
---

# PRD: MIRA — Incremento Funcional F4 y F1

## 0. Document Purpose

El propósito de este Documento de Requisitos de Producto (PRD) es formalizar las especificaciones funcionales, las reglas de negocio vinculantes, la experiencia de usuario y los atributos de calidad para el primer incremento de software ejecutable de la plataforma **MIRA**, correspondiente a la **Entrega 2**.

Este documento se construye directamente sobre el **Project Brief** elaborado por la Analista de Negocio (Mary), incorporando la trazabilidad exigida por la pauta de evaluación académica y las directrices corporativas de DPRIME SpA y la Aseguradora Piloto:
1. **Requisitos heredados de la Entrega 1:** Mantienen rigurosamente sus identificadores originales (`RF-11`, `RF-12`, `RF-13`, `RF-19`).
2. **Requisitos nuevos:** Se tipifican con identificadores sistemáticos (`FR-F4-XX` para el motor de umbrales y `FR-F1-XX` para la bandeja asistida), declarando su fuente explícita en la bitácora de decisiones (`DEC-01` a `DEC-09`) o en el catálogo de hallazgos (`H-01` a `H-15`).
3. **Destinatarios downstream:** Este PRD es el insumo vinculante para la Diseñadora UX (**Sally** / `bmad-agent-ux-designer`), el Arquitecto de Sistemas (**Winston** / `bmad-agent-architect`), la Desarrolladora Senior (**Amelia** / `bmad-agent-dev`) y el equipo de aseguramiento de calidad (QA).

---

## 1. Vision

En la industria de seguros masivos y coberturas de salud, la automatización descontrolada de dictámenes de liquidación enfrenta una grave encrucijada legal y reputacional: las decisiones automatizadas que rechazan siniestros vulneran los derechos del consumidor si carecen de una explicación causal clara y de una **intervención humana significativa**. Al mismo tiempo, los procesos 100% manuales colapsan las operaciones, generando demoras inaceptables y sesgos cognitivos severos en los operadores.

**MIRA** resuelve este dilema mediante un modelo de automatización gobernada por umbrales y supervisión humana activa:
- **F4 (Puntaje y decisión por umbrales):** Actúa como el filtro algorítmico determinista que evalúa señales analíticas precalculadas, pondera componentes de confianza, hace cumplir reglas de corte por señal individual y aplica precedencia absoluta contra el fraude. Si el caso supera los más altos estándares de certeza ($\ge 90$ puntos y sin anomalías), se aprueba automáticamente; si existe cualquier duda, anomalía o bajo puntaje, **el sistema se abstiene de rechazar y deriva el caso a un revisor humano**.
- **F1 (Bandeja de revisión asistida):** Empodera al liquidador humano mediante un espacio de trabajo diseñado específicamente para mitigar el **sesgo de anclaje**. La interfaz presenta de forma prioritaria la evidencia documental con ubicación espacial de anomalías y el desglose de alertas, revelando el puntaje algorítmico únicamente al final del análisis. El operador toma la decisión vinculante final, y el sistema registra de manera transparente cualquier discrepancia con la sugerencia algorítmica para auditoría y mejora continua.

Este incremento funcional materializa el ciclo completo: desde la evaluación algorítmica en F4 hasta la resolución humana auditable en F1, garantizando cumplimiento regulatorio, transparencia probatoria y eficiencia operativa.

---

## 2. Target User & JTBD

### 2.1 Jobs To Be Done (JTBD)

- **Operador de Liquidación / Revisor Asistido (Usuario Primario):**
  - *Cuando* se me asigna un siniestro o reembolso derivado por el motor de reglas,
  - *Quiero* examinar las evidencias documentales con las anomalías destacadas visualmente y comprender las razones exactas de la derivación sin estar condicionado por un número al inicio,
  - *Para* dictaminar con independencia de criterio si el caso se aprueba, se rechaza o requiere antecedentes adicionales, cumpliendo el principio legal de intervención humana significativa.

- **Analista de Fraude / Investigador Forense:**
  - *Cuando* un caso presenta indicios de manipulación tipográfica, duplicidad de folio o inconsistencia de identidad,
  - *Quiero* que el motor bloquee de inmediato cualquier intento de aprobación automática y coloque el expediente en la cima de la bandeja con etiqueta de alerta crítica,
  - *Para* salvaguardar el patrimonio de la aseguradora y preservar la cadena de custodia probatoria para acciones judiciales.

- **Oficial de Cumplimiento Normativo y Auditor Interno:**
  - *Cuando* la entidad reguladora o un asegurado audita un siniestro rechazado,
  - *Quiero* reconstruir el expediente exacto: las señales recibidas, los umbrales vigentes al momento del fallo, la identidad del operador y la justificación escrita de su voto,
  - *Para* demostrar fehacientemente que ningún rechazo fue producto de un algoritmo opaco ("caja negra") y que se respetó el debido proceso.

- **Supervisor de Operaciones de Siniestros:**
  - *Cuando* administro la carga de trabajo diaria de la mesa de revisión,
  - *Quiero* visualizar los casos clasificados por urgencia de SLA y detectar discrepancias de criterio entre revisores y plataforma,
  - *Para* evitar cuellos de botella operativos y alimentar los ciclos de reentrenamiento de los modelos de riesgo.

### 2.2 Non-Users (v1)

- **Asegurado / Reclamante externo:** No interactúa directamente con esta consola interna; recibe el resultado del dictamen a través de los canales habituales de la aseguradora.
- **Data Scientist / Entrenador de Modelos:** En la Entrega 2 no interactúa con pipelines de reentrenamiento en caliente; los modelos pesados se sustituyen por datos sintéticos deterministas (Regla 4.3).
- **Administrador de Políticas Comerciales:** La edición dinámica de umbrales y doble firma (F5) queda explícitamente fuera de alcance en esta fase.

### 2.3 Key User Journeys

#### UJ-1: Liquidación asistida de siniestro con sospecha de fraude (RF-12)
- **Persona y Contexto:** Marco Peñailillo, liquidador senior con 8 años de experiencia, atiende la bandeja de casos urgentes.
- **Estado de Entrada:** Autenticado en la consola web de MIRA con rol de Operador.
- **Ruta de Interacción:**
  1. Marco accede a la bandeja de casos derivados (F1) y visualiza un caso destacado en rojo con causal: `Alerta Crítica de Fraude: Alteración de Folio`.
  2. Al abrir el expediente, la pantalla le presenta en primer plano el visor documental con una caja delimitadora (*bounding box*) roja señalando la fecha y folio del comprobante médico.
  3. Revisa la lista de señales: la señal de *Autenticidad de Documento* está en rojo (falla crítica), aun cuando el monto coincide y la identidad del asegurado es válida.
  4. Hace scroll hacia el final de la pantalla y recién allí observa el puntaje sugerido global de confianza (32 puntos).
  5. Selecciona la acción `Rechazar`, ingresa en el campo de texto obligatorio la justificación: *"Se constata doble impresión tipográfica en el folio fiscal del bono"*, y envía la resolución.
- **Clímax:** El sistema procesa el rechazo humano, emite el comprobante de dictamen con firma del operador y actualiza el estado a `RECHAZADO_POR_OPERADOR`.
- **Resolución:** El caso desaparece de la cola activa y se archiva en el histórico con auditoría completa.
- **Caso de Borde:** Si Marco hubiese presionado `Aprobar`, el sistema no bloquea la acción pero activa de inmediato la marca `discrepancia_detectada = true` exigiendo justificación técnica exhaustiva antes de persistir.

#### UJ-2: Revisión de caso con puntaje global alto pero mínimo individual insatisfecho (H-12 / RF-11)
- **Persona y Contexto:** Marco Peñailillo revisa un reembolso ambulatorio de alto valor presentado por un nuevo prestador de salud.
- **Estado de Entrada:** Bandeja F1 filtrada por casos derivados de hoy.
- **Ruta de Interacción:**
  1. Marco abre el caso `CASO-2026-9042`, derivado automáticamente por F4 bajo la causal: `Incumplimiento de Umbral Mínimo: Consistencia de Prestador`.
  2. En el visor de evidencias, observa que la boleta es nítida y el asegurado no tiene antecedentes adversos.
  3. En el panel de desglose analítico nota que tres señales tienen 98 puntos, pero la señal de *Habilitación de Prestador ante Superintendencia de Salud* tiene 40 puntos (mínimo exigido: 70 puntos).
  4. Al final de la página se revela que el puntaje global agregado era de 91 puntos, pero F4 impidió la aprobación automática en cumplimiento estricto de la regla `RF-11`.
  5. Marco determina que se requiere clarificación del prestador y pulsa `Solicitar Antecedentes Adicionales`, detallando el requerimiento de certificado de vigencia médica.
- **Clímax:** El caso cambia a estado `PENDIENTE_ANTECEDENTES`, pausando el reloj de SLA interno y notificando la solicitud al área de convenios.
- **Resolución:** Se evita la fuga de capitales por prestadores no validados sin generar un rechazo arbitrario contra el afiliado.

#### UJ-3: Aprobación de caso de bajo puntaje con marca de discrepancia de criterio (DEC-07 / RF-19)
- **Persona y Contexto:** Andrea Muñoz, revisora médica, analiza un caso de urgencia médica derivado por bajo puntaje.
- **Estado de Entrada:** Bandeja F1, caso `CASO-2026-4411` con puntaje F4 de 48 puntos (derivado por DEC-07, jamás rechazado automáticamente).
- **Ruta de Interacción:**
  1. Andrea ingresa al caso y revisa la orden médica de urgencia. Nota que el documento fue fotografiado en condiciones de baja iluminación en una ambulancia, lo que degradó la señal de legibilidad OCR y hundió el puntaje algorítmico a 48.
  2. Al inspeccionar manualmente la imagen ampliada y cotejar el timbre del médico tratante con el registro hospitalario, comprueba que la prestación fue legítima y de riesgo vital inminente.
  3. Llega al panel de resolución y pulsa `Aprobar`.
  4. El sistema despliega un diálogo advirtiendo que la resolución difiere de la sugerencia algorítmica de la plataforma y solicita el motivo de discrepancia.
  5. Andrea escribe: *"Evidencia fotográfica tomada en traslado de urgencia; lectura humana valida identidad médica y diagnóstico de apendicectomía aguda"*. Confirma la emisión.
- **Clímax:** La plataforma aprueba el reembolso, genera la validación cobrable (DEC-02) y almacena el registro de discrepancia para revisión del equipo de Data Science.
- **Resolución:** El asegurado recibe el reembolso en tiempo récord sin perjuicio patrimonial indebido, y la aseguradora recopila un caso de estudio real para calibrar sus pesos analíticos.

#### UJ-4: Monitoreo y control preventivo de SLA en casos derivados (DEC-05)
- **Persona y Contexto:** Rodrigo Valenzuela, supervisor de operaciones de siniestros.
- **Estado de Entrada:** Consola F1 en vista de administración de cola.
- **Ruta de Interacción:**
  1. Rodrigo visualiza la tabla de casos derivados clasificada con indicadores de tiempo restante: Verde (> 4 horas), Amarillo (entre 1 y 4 horas), Rojo (< 1 hora o vencido).
  2. Identifica un caso en estado crítico a 20 minutos de expirar el SLA normativo de 24 horas hábiles.
  3. Reasigna el caso directamente al operador disponible de turno con notificación prioritaria en pantalla.
- **Clímax:** El operador toma el caso de inmediato y emite la resolución antes del vencimiento del SLA.
- **Resolución:** Cero siniestros vencidos por negligencia en cola de revisión asistida.

---

## 3. Glossary

Los siguientes términos tienen significado formal y vinculante en todo el PRD, en las especificaciones de interfaz, en el código y en las pruebas automatizadas:

- **Puntaje de Confianza Multimodal:** Valor escalar normalizado entre $0$ y $100$ calculado por el motor F4 mediante una combinación lineal ponderada de señales analíticas precalculadas de documentos, identidades y prestaciones.
- **Umbral de Aprobación Automática:** Valor de referencia fijado en $90$ puntos (conforme a `DEC-04`), por sobre el cual un expediente puede aprobarse de forma directa y autónoma, siempre que cumpla con todos los mínimos individuales y no tenga alertas de fraude activas.
- **Umbral de Revisión Asistida (Zona Gris):** Rango de puntuación entre $60$ y $89$ puntos (conforme a `DEC-04`), en el cual un expediente requiere obligatoriamente derivación hacia F1 para escrutinio humano.
- **Prohibición de Rechazo Automático:** Mandato legal y operativo (`DEC-07` que resuelve `H-04`) que impide terminantemente a la plataforma rechazar un siniestro sin intervención humana. Todo caso con puntaje $< 60$ es catalogado como `DERIVADO_A_REVISION` bajo la causal *"Bajo Puntaje (<60)"*.
- **Intervención Humana Significativa:** Principio de diseño y gobernanza algorítmica donde el operador humano ejerce un rol decisor activo, informado e independiente sobre el caso, contando con todas las pruebas y antecedentes sin coacción del sistema.
- **Sesgo de Anclaje Cognitivo:** Tendencia psicológica del revisor humano a ajustar su juicio al primer número o puntaje que observa. En MIRA se mitiga mediante la regla de presentación `DEC-03`, que sitúa el puntaje al final del recorrido visual.
- **Precedencia de Señal de Fraude:** Regla de corte (`RF-12`) por la cual la detección activa de una sospecha tipificada de fraude prevalece sobre cualquier puntaje numérico alto, bloqueando la aprobación automática y forzando la derivación prioritaria.
- **Mínimo por Señal Individual:** Regla de consistencia (`RF-11` que resuelve el hallazgo `H-12`) que exige que señales críticas específicas (ej. autenticidad documental, prestador habilitado) superen un umbral mínimo propio independientemente del promedio agregado.
- **Marca de Discrepancia:** Indicador booleano y metadato de auditoría (`RF-19`) registrado automáticamente cuando la decisión final del operador humano contradice la recomendación o rango sugerido por la plataforma, capturando la justificación para análisis posterior.
- **Validación Cobrable:** Caso procesado con resultado emitido y puntaje formalizado, ya sea mediante aprobación automática directa en F4 o mediante dictamen humano en F1, constituyendo una unidad transaccional útil según `DEC-02`.
- **Reconstrucción de Decisión:** Capacidad de auditoría forense (`H-14` / `DEC-10`) consistente en recuperar con exactitud los datos de entrada, las versiones de reglas/umbrales vigentes y el motivo del operador al momento de la resolución.
- **SLA de Caso Derivado:** Ventana máxima de tiempo operativo admisible para que un caso derivado en F1 sea resuelto por un revisor humano (fijada como regla de negocio en 24 horas hábiles).

---

## 4. Features

### 4.1 F4: Motor de Puntaje y Decisión por Umbrales

**Descripción:**  
El motor F4 es el núcleo algorítmico responsable de consumir los datos y señales precalculadas de un siniestro (simuladas en dataset sintético para la Entrega 2), calcular el puntaje global ponderado, evaluar reglas de negocio duras (mínimos y fraude) y clasificar el expediente en una de dos categorías operativas: `APROBADO_AUTOMATICO` o `DERIVADO_A_REVISION_ASISTIDA`. El motor garantiza la imposibilidad de rechazo automático (`DEC-07`) y despacha los casos derivados a la bandeja F1 de forma inmediata.

#### Requisitos Funcionales:

##### RF-11: Evaluación de Umbrales Mínimos por Señal Individual
- **Origen:** Entrega 1 (`RF-11`), resolviendo el hallazgo abierto `H-12`.
- **Enunciado:** El motor F4 debe verificar, para cada siniestro evaluado, que las señales individuales designadas como críticas superen sus correspondientes umbrales mínimos de corte, con independencia del puntaje agregado ponderado.
- **Criterios de Verificación / Consecuencias Testables:**
  - Si un caso presenta un puntaje global de confianza de $95/100$, pero la señal crítica de *Autenticidad Documental* tiene un valor de $55$ (mínimo configurado: $70$), el motor F4 **debe clasificar el caso como `DERIVADO_A_REVISION_ASISTIDA`**.
  - El expediente resultante debe portar el metadato explícito `causal_derivacion: "INCUMPLIMIENTO_MINIMO_SENAL"` e identificar la señal específica infractora (`autenticidad_documental`).
  - Las señales configuradas con umbral mínimo propio en v1 son:
    1. `autenticidad_documental` (mínimo: $70$)
    2. `habilitacion_prestador` (mínimo: $65$)
    3. `consistencia_identidad` (mínimo: $75$)

##### RF-12: Precedencia Estricta de Señales de Fraude
- **Origen:** Entrega 1 (`RF-12` / `CP-RF-12-01`).
- **Enunciado:** Si el vector de entrada del siniestro contiene activa al menos una bandera tipificada como señal de fraude (ej. manipulación de firmas, alteración tipográfica, duplicidad de folio), el motor F4 debe aplicar cortocircuito lógico, anulando cualquier posibilidad de aprobación automática sin importar cuán alto sea el puntaje global ponderado.
- **Criterios de Verificación / Consecuencias Testables:**
  - Dado un caso con puntaje global de $98/100$ y bandera `alerta_fraude_activa: true`, el sistema emite dictamen `DERIVADO_A_REVISION_ASISTIDA` con prioridad `URGENTE`.
  - El caso es catalogado bajo la causal `causal_derivacion: "ALERTA_CRITICA_FRAUDE"`.
  - El motor jamás emite `APROBADO_AUTOMATICO` ante una señal de fraude activa.

##### RF-13: Derivación por Información Incompleta o Falla de Módulo
- **Origen:** Entrega 1 (`RF-13` / `CP-RF-13-01`).
- **Enunciado:** Si alguno de los módulos analíticos o fuentes de señal falla, arroja timeout o entrega información parcial o nula, el motor F4 debe derivar el expediente a revisión asistida, prohibiendo terminantemente la aprobación con datos truncos o la imputación arbitraria de valores faltantes.
- **Criterios de Verificación / Consecuencias Testables:**
  - Si en el vector de entrada falta una de las cuatro señales requeridas (valor `null` o no disponible), el motor F4 suspende el cálculo de aprobación automática.
  - El caso se deriva a F1 con causal `causal_derivacion: "INFORMACION_INCOMPLETA_FALLA_MODULO"` y detalle de los componentes no procesados.

##### FR-F4-01: Cálculo Ponderado y Normalización del Puntaje Multimodal
- **Origen:** Nuevo (Fuente: Project Brief §5.1, Informe E1 Cap 2.6).
- **Enunciado:** El motor F4 debe calcular el puntaje global de confianza ($S$) como la suma ponderada normalizada de los cuatro componentes del modelo:
  $$S = \sum_{i=1}^{n} (w_i \cdot s_i)$$
  donde $s_i \in [0, 100]$ representa cada señal y $w_i$ su peso normalizado ($\sum w_i = 1.0$).
- **Pesos de Referencia para Entrega 2:**
  - Autenticidad Documental ($w_1 = 0.35$)
  - Consistencia de Datos Clínicos y Montos ($w_2 = 0.25$)
  - Habilitación y Reputación del Prestador ($w_3 = 0.20$)
  - Validación de Identidad y Cobertura ($w_4 = 0.20$)
- **Criterios de Verificación / Consecuencias Testables:**
  - Ante un vector de señales deterministas, el cálculo produce exactamente el puntaje matemático esperado en un rango estricto de $[0, 100]$.
  - El tiempo de cálculo por caso es inferior a $200$ milisegundos en entorno local.

##### FR-F4-02: Clasificación Algorítmica con Prohibición Absoluta de Rechazo Automático
- **Origen:** Nuevo (Fuente: `DEC-07` que resuelve `H-04`, `DEC-04` que resuelve `H-03`).
- **Enunciado:** El motor F4 debe aplicar la lógica de clasificación por umbrales conforme a las decisiones de la bitácora:
  1. Si $S \ge 90$, sin señales de fraude y con todos los mínimos individuales cumplidos $\rightarrow$ `APROBADO_AUTOMATICO`.
  2. Si $60 \le S < 90$ $\rightarrow$ `DERIVADO_A_REVISION_ASISTIDA` (Causal: *"Zona Gris / Puntuación Intermedia"*).
  3. Si $S < 60$ $\rightarrow$ `DERIVADO_A_REVISION_ASISTIDA` (Causal: *"Bajo Puntaje (<60) — Requiere Dictamen Humano por Riesgo Patrimonial"*). **Bajo ninguna circunstancia F4 genera estado `RECHAZADO`**.
- **Criterios de Verificación / Consecuencias Testables:**
  - Un caso con puntaje $42/100$ ingresado a F4 finaliza en estado `DERIVADO_A_REVISION_ASISTIDA`.
  - El sistema arroja error o rechaza cualquier configuración que intente habilitar una salida de rechazo automático en el motor F4.

##### FR-F4-03: Despacho Inmediato de Casos Derivados a la Cola de F1
- **Origen:** Nuevo (Fuente: Regla de Conexión de Alcance Entrega 2, CA-01 del Project Brief).
- **Enunciado:** Cada vez que el motor F4 clasifica un caso como `DERIVADO_A_REVISION_ASISTIDA`, debe persistir el expediente en el repositorio compartido de casos y emitirlo en tiempo real a la cola de atención de la bandeja asistida F1, con su identificador único, vector de señales, causal de derivación y fecha/hora de creación para inicio de conteo de SLA.
- **Criterios de Verificación / Consecuencias Testables:**
  - Al ejecutar una prueba de evaluación en F4 que resulte derivada, el caso se hace inmediatamente consultable en la API/almacén de F1 con consistencia de datos total.

#### Requisitos No Funcionales Específicos de F4:
- **NFR-F4-01 (Determinismo):** Dado el mismo conjunto de señales de entrada y la misma versión de umbrales, F4 debe generar idéntico puntaje y clasificación en el 100% de las ejecuciones.
- **NFR-F4-02 (Inmutabilidad del Registro de Entrada):** El vector de señales de entrada y la instantánea de umbrales aplicados deben quedar sellados en el objeto del caso sin posibilidad de modificación posterior.

---

### 4.2 F1: Bandeja de Revisión Asistida (Human-in-the-Loop)

**Descripción:**  
La bandeja asistida F1 es la interfaz de usuario interactiva y el entorno operativo donde los revisores humanos y liquidadores analizan los casos derivados por F4. Su diseño está estrictamente gobernado por el mandato `DEC-03` para erradicar el sesgo de anclaje: la evidencia documental, las marcas de hallazgos y el desglose de señales se ubican en el foco visual primario, mientras que el puntaje algorítmico global se despliega de forma diferida al final de la pantalla. El operador es el único actor facultado para rechazar un caso, y toda resolución discrepante queda registrada para auditoría.

#### Requisitos Funcionales:

##### RF-19: Registro de Marca de Discrepancia de Criterio Operador vs. Plataforma
- **Origen:** Entrega 1 (`RF-19` / `CP-RF-19-01`).
- **Enunciado:** Si la decisión emitida por el operador humano difiere de la sugerencia algorítmica de la plataforma (ej. el operador aprueba un caso derivado por bajo puntaje o por señal de fraude; o el operador rechaza un caso con puntaje intermedio alto), la plataforma debe estampar de forma automática la marca `discrepancia_detectada: true` y exigir un motivo textual explícito, sin bloquear ni revertir la resolución soberana del operador.
- **Criterios de Verificación / Consecuencias Testables:**
  - Cuando el operador selecciona `Aprobar` en un caso derivado por `Bajo Puntaje (<60)` o `Alerta de Fraude`:
    1. El sistema solicita obligatoriamente el campo `motivo_discrepancia`.
    2. Al confirmar, el caso se guarda como `APROBADO_POR_OPERADOR` con `discrepancia_detectada: true`.
    3. El registro queda inmediatamente indexado para consulta en la bitácora de auditoría y feedback de modelos.
  - La emisión del dictamen no se interrumpe ni sufre demoras operativas.

##### FR-F1-01: Visualización y Priorización de la Cola de Casos Derivados con Alerta de SLA
- **Origen:** Nuevo (Fuente: Project Brief §5.2, `DEC-05`).
- **Enunciado:** La pantalla principal de F1 debe mostrar una tabla de expedientes derivados pendientes de atención, ordenada por criticidad y tiempo de SLA restante, indicando:
  1. Identificador de Caso y Nombre del Asegurado.
  2. Causal explícita de derivación (Bajo Puntaje, Zona Gris, Alerta de Fraude, Mínimo Violado, Información Incompleta).
  3. Tiempo restante para cumplimiento de SLA con distintivo visual (Verde: $> 4$ hrs; Amarillo: $1$ a $4$ hrs; Rojo: $< 1$ hr o vencido).
  4. Filtros por causal y estado, y buscador rápido por ID de caso.
- **Criterios de Verificación / Consecuencias Testables:**
  - Casos con `Alerta Crítica de Fraude` o SLA próximo a vencer aparecen posicionados en los primeros lugares de la lista.
  - El tiempo restante de SLA se actualiza dinámicamente o por refresco sin desfase temporal.

##### FR-F1-02: Despliegue Espacial de Evidencias con Marcadores de Hallazgo
- **Origen:** Nuevo (Fuente: `DEC-03` que resuelve `H-09`, Project Brief §5.2).
- **Enunciado:** Al ingresar al detalle de un caso derivado, F1 debe exhibir en la sección superior y central el visor de la evidencia documental (boleta, bono, orden médica), superponiendo cajas delimitadoras (*bounding boxes*) o marcadores visuales sobre las coordenadas exactas de las anomalías detectadas.
- **Criterios de Verificación / Consecuencias Testables:**
  - El operador puede hacer zoom, desplazar el documento y hacer clic en una anomalía para leer la descripción del hallazgo (ej. *"Alteración tipográfica detectada en el folio N° 45892"*).
  - Si el documento no posee coordenadas espaciales, se despliega una tarjeta de alerta vinculada al archivo correspondiente.

##### FR-F1-03: Despliegue Diferido del Puntaje de Confianza al Final del Flujo (Anti-Sesgo de Anclaje)
- **Origen:** Nuevo (Fuente: `DEC-03` que resuelve `H-09`).
- **Enunciado:** La interfaz de F1 debe prohibir expresamente la exhibición del puntaje numérico de confianza global en la cabecera o en la pantalla de bienvenida del caso. El puntaje global y su gráfico de barras deben ubicarse físicamente en la sección inferior de la página, accesible únicamente tras haber recorrido las evidencias y el desglose de señales.
- **Criterios de Verificación / Consecuencias Testables:**
  - Al cargar la página de detalle del caso, el viewport inicial superior contiene únicamente: metadatos del caso, visor de evidencia y tabla de desglose de señales analíticas.
  - El puntaje numérico (0-100) y su desglose porcentual están confinados a un bloque situado inmediatamente antes del panel de botones de decisión resolutiva.

##### FR-F1-04: Panel Resolutivo Humano con Justificación Obligatoria
- **Origen:** Nuevo (Fuente: `DEC-07`, Principio de Intervención Humana Significativa).
- **Enunciado:** La interfaz de F1 debe proveer tres botones de acción excluyentes para dictaminar el caso:
  1. `Aprobar`: Resuelve favorablemente la liquidación.
  2. `Rechazar`: Deniega la cobertura del siniestro.
  3. `Solicitar Antecedentes`: Suspende la resolución a la espera de nuevos documentos.
  Para las acciones `Rechazar` y `Solicitar Antecedentes`, así como en cualquier caso donde se detecte discrepancia (`RF-19`), el ingreso de una justificación textual explicativa en un campo de texto dedicado es **estrictamente obligatorio**.
- **Criterios de Verificación / Consecuencias Testables:**
  - Si el operador presiona `Rechazar` con el campo de justificación vacío, el sistema bloquea el envío y resalta el campo con advertencia: *"Debe ingresar el fundamento probatorio para rechazar el siniestro"*.
  - Al completar la justificación y confirmar, el expediente se actualiza atómicamente con fecha, hora, identidad del usuario y estado final.

##### FR-F1-05: Reconstrucción Auditable del Expediente Decisional
- **Origen:** Nuevo (Fuente: `H-14` / `DEC-10`, `DEC-01`).
- **Enunciado:** Al consumarse cualquier resolución en F1, el sistema debe sellar una instantánea inalterable del expediente que contenga:
  - Señales originales provistas por F4.
  - Causal original de derivación.
  - Coordenadas de hallazgos exhibidas.
  - Puntaje que visualizó el operador.
  - Voto emitido, justificación textual e identidad del operador.
  - Bandera de discrepancia (`true`/`false`).
- **Criterios de Verificación / Consecuencias Testables:**
  - Es posible recuperar y visualizar en modo solo lectura el expediente histórico exacto de cualquier caso finalizado, garantizando la reconstrucción exigida por auditoría regulatoria.

#### Requisitos No Funcionales Específicos de F1:
- **NFR-F1-01 (Claridad Ergonómica):** La interfaz debe estar íntegramente redactada en español formal de negocios aseguradores, sin códigos técnicos crudos no traducidos.
- **NFR-F1-02 (Tiempo de Respuesta UI):** La apertura del visor de evidencias y la transición entre casos en F1 debe completarse en menos de $500$ milisegundos en condiciones normales.

---

## 5. Non-Goals (Explicit)

Para asegurar la máxima calidad técnica, profundidad analítica y éxito en la evaluación de la Entrega 2, se definen taxativamente los siguientes **no-objetivos**:

1. **Modelos de Inteligencia Artificial / LLMs en Tiempo Real:** No se conectarán APIs de OpenAI, Google Gemini ni modelos locales de visión por computador en vivo durante la ejecución de este incremento. Se utiliza un dataset de casos de prueba sintéticos con señales y coordenadas precalculadas (`dataset.json`), en conformidad estricta con la **Regla 4.3** de las bases.
2. **Diseñador Visual de Flujos (F2):** No se construirá una interfaz gráfica para arrastrar y soltar bloques de decisión ni control de versiones de flujos lógicos.
3. **Ingesta Multi-canal y OCR en Vivo (F3):** No se implementará procesamiento OCR de PDFs escaneados ni preprocesamiento de imágenes en caliente; las entradas se asumen procesadas previamente.
4. **Gestión y Autorización de Umbrales con Doble Firma (F5 / RF-28):** Los umbrales (90/60) se configuran de forma estática en el código o configuración de la aplicación; no se desarrollará la pantalla de solicitud y firma mancomunada de cambios de parámetros.
5. **Rastro Forense Avanzado y Tableros BI (F6, F7, F8, F9):** No se construirán gráficos analíticos de reportería gerencial, cálculo de costos de facturación comercial ni catálogos de versiones de modelos predictivos.
6. **Autenticación Federada contra Active Directory / LDAP (DEC-08):** No se integrará protocolo LDAP ni Single Sign-On corporativo; la aplicación proveerá usuarios simulados por rol (ej. `operador_marco`, `supervisor_rodrigo`) para la demostración en vivo.

---

## 6. MVP Scope (Entrega 2)

### 6.1 In Scope (Lo que se entrega operativo)
- Motor de cálculo y gobierno de umbrales F4 con evaluación ponderada, mínimos por señal (`RF-11`), precedencia de fraude (`RF-12`), rechazo automático bloqueado (`DEC-07`) y derivación directa (`FR-F4-03`).
- Bandeja de revisión asistida F1 con lista filtrable y priorizada por SLA (`FR-F1-01`), visor documental con coordenadas espaciales de hallazgos (`FR-F1-02`), despliegue de puntaje diferido al final (`FR-F1-03`), panel resolutivo de tres vías con justificación obligatoria (`FR-F1-04`) y registro de marcas de discrepancia (`RF-19`).
- Dataset sintético enriquecido con al menos 8 casos de prueba representativos que cubren todos los escenarios:
  - Caso 1: Aprobación automática limpia ($\ge 90$, sin alertas).
  - Caso 2: Derivación por zona intermedia (60-89).
  - Caso 3: Derivación por bajo puntaje ($< 60$, prueba de DEC-07).
  - Caso 4: Derivación por mínimo de señal individual violado (prueba de H-12 / RF-11).
  - Caso 5: Derivación forzada por alerta de fraude activa con puntaje alto (prueba de RF-12).
  - Caso 6: Derivación por información incompleta / módulo ausente (prueba de RF-13).
  - Caso 7: Resolución asistida con marca de discrepancia de criterio (prueba de RF-19).
  - Caso 8: Caso derivado crítico con SLA en zona roja de vencimiento.
- Suite de pruebas automatizadas y prueba de extremo a extremo (E2E) recorrible de punta a punta desde el navegador.

### 6.2 Out of Scope for MVP
- Integraciones con servicios de nube externos o pasarelas de pago.
- Exportación de expedientes en formato PDF con firma digital criptográfica PKCS#7 (diferido a v2).
- Módulo de auto-asignación algorítmica de carga balanceada entre operadores (diferido a v2).

---

## 7. Success Metrics & Counter-Metrics

### Métricas Primarias:
- **SM-1 (Cumplimiento de Prohibición de Rechazo Automático):**  
  - *Definición:* Porcentaje de siniestros con puntaje inferior a 60 que resulten rechazados directamente por el motor F4 sin pasar por un operador humano.
  - *Meta:* Exactamente **0.0%** (Cero rechazos automáticos).
  - *Valida:* `FR-F4-02`, `DEC-07`, `H-04`.
- **SM-2 (Efectividad en Captura de Discrepancias):**  
  - *Definición:* Porcentaje de casos donde la decisión del operador contradice la sugerencia de la plataforma y el sistema estampa la marca `discrepancia_detectada` y almacena el motivo.
  - *Meta:* **100%** de captura en las transacciones discrepantes.
  - *Valida:* `RF-19`, `CP-RF-19-01`.
- **SM-3 (Adherencia al Diseño Anti-Sesgo de Anclaje):**  
  - *Definición:* Verificación en pruebas de usabilidad y de interfaz de que el puntaje global de confianza no es visible en el primer pliegue (*viewport*) de la pantalla del caso asistido.
  - *Meta:* **100%** de cumplimiento en la UI de F1.
  - *Valida:* `FR-F1-03`, `DEC-03`, `H-09`.

### Métricas Secundarias:
- **SM-4 (Rendimiento de Evaluación de Umbrales F4):**  
  - *Definición:* Tiempo de procesamiento del motor F4 por caso de prueba.
  - *Meta:* $< 200$ ms.
  - *Valida:* `FR-F4-01`, `RNF-08` reformulado.
- **SM-5 (Cobertura de Regla de Mínimos Individuales):**  
  - *Definición:* Tasa de derivación forzada en casos con puntaje agregado $\ge 90$ pero con una señal crítica bajo su umbral mínimo.
  - *Meta:* **100%** de derivación a F1.
  - *Valida:* `RF-11`, `H-12`.

### Contra-Métricas (Lo que NO se debe optimizar):
- **SM-C1 (No inflar la tasa de Straight-Through Processing a expensas de la rigurosidad):**  
  - *Razón:* Optimizar ciegamente la tasa de aprobación directa en F4 elevaría el volumen de liquidación rápida, pero dispararía la filtración de fraudes o siniestros mal constituidos. Prevalece el criterio conservador de la marcha blanca (`DEC-04`).
- **SM-C2 (No sacrificar la calidad de la justificación humana por acelerar el SLA):**  
  - *Razón:* Reducir o volver opcional el campo de justificación del operador aceleraría la tasa de resolución por hora en F1, pero destruiría la auditabilidad y el valor probatorio de la intervención humana significativa ante la Superintendencia.

---

## 8. Open Questions

1. **OQ-01 (Calibración de Pesos Post-Piloto):** ¿Cuál será la frecuencia formal con la que el comité de riesgos revisará los pesos $w_i$ de F4 a partir de las marcas de discrepancia acumuladas? *(Se define como proceso posterior a la Entrega 2; para este incremento los pesos son estáticos).*
2. **OQ-02 (Notificación de Vencimiento de SLA hacia Sistemas Externos):** En una etapa productiva completa, ¿el aviso de vencimiento de SLA de F1 debe disparar webhooks hacia el CRM corporativo? *(Se mantiene local en la interfaz durante el MVP).*

---

## 9. Assumptions Index

- `[ASSUMPTION: Mock Dataset Representativo]`: Se asume que un archivo estructurado local con 8 casos canónicos en JSON cubre la totalidad de las ramas de decisión requeridas para la validación y evaluación de F4 y F1 sin necesidad de backend distribuido.
- `[ASSUMPTION: Formato de Coordenadas de Hallazgo]`: Se asume que las coordenadas de ubicación espacial de anomalías documentales se representan mediante porcentajes normalizados `(top, left, width, height)` sobre la imagen de la evidencia para asegurar compatibilidad responsiva en el visor web.
- `[ASSUMPTION: Roles Locales Simplificados]`: Se asume que la sesión de usuario en F1 se controla mediante un selector de rol simulado (Operador / Supervisor) persistido en almacenamiento local o estado de aplicación, dando cumplimiento a la exclusión de LDAP (`DEC-08`).

---

## 10. Adapt-In Clusters (Enterprise & Regulated Domain)

### 10.1 Requisitos No Funcionales Transversales (Cross-Cutting NFRs)
- **Seguridad y Confidencialidad:** Aunque se opera con datos de prueba, la estructura de datos respeta el estándar de almacenamiento seguro de expedientes médicos y personales, sin exponer datos sensibles sin enmascarar en vistas generales.
- **Confiabilidad e Integridad Transaccional:** La resolución de un caso en F1 y la emisión desde F4 son operaciones atómicas; no pueden quedar casos en estados intermedios indefinidos.
- **Portabilidad y Autonomía de Ejecución:** La aplicación debe levantarse en cualquier equipo estándar mediante comandos simples documentados en el README en menos de 5 minutos (Criterio de Evaluación `C4`).

### 10.2 Restricciones y Salvaguardas Regulatorias
- **Cumplimiento de Protección Patrimonial (`DEC-07`):** Prohibición sistémica de rechazo algorítmico sin revisión humana.
- **Principio de No Inducción de Decisión (`DEC-03`):** Neutralidad de la interfaz de usuario en los primeros momentos del análisis humano.

### 10.3 Gobernanza de Datos y Trazabilidad Forense
- **Custodia de Evidencias (`DEC-01`):** Los metadatos de los casos generados en este incremento se estructuran con campos de retención quinquenal y sellos de tiempo inmutables.
- **Reconstrucción Decisional (`H-14`):** El sistema permite reabrir cualquier caso del histórico y observar exactamente los parámetros, puntajes y motivos con los que se emitió el dictamen.

### 10.4 Requisitos Operacionales y SLA
- El reloj de SLA se inicia en el instante preciso en que el motor F4 clasifica un caso como derivado y se detiene únicamente cuando el operador humano pulsa `Aprobar`, `Rechazar` o `Solicitar Antecedentes`.
