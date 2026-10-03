---
title: "PRD Addendum: Especificaciones Técnicas y Matrices de Decisión (Entrega 2)"
status: "final"
created: "2026-10-03"
updated: "2026-10-03"
author: "John (Product Manager — BMAD Method)"
project: "MIRA — Plataforma de Inteligencia Multimodal para Decisiones Empresariales"
---

# Addendum: MIRA — Incremento F4 y F1 (Entrega 2)

Este documento complementa el **PRD Principal** (`prd.md`), preservando el detalle técnico, las matrices de alternativas descartadas y las estructuras de datos que alimentarán directamente el trabajo de la Diseñadora UX (**Sally**), el Arquitecto de Sistemas (**Winston**) y la Desarrolladora Senior (**Amelia**).

---

## 1. Matriz de Decisiones Vinculantes y Alternativas Consideradas (DEC-01 a DEC-09)

A partir de la bitácora consensuada con el Representante del Cliente en la Entrega 1, se resumen las opciones analizadas y el fundamento de la alternativa seleccionada:

| ID | Asunto | Alternativas Evaluadas | Opción Adoptada y Razón de Negocio |
| :--- | :--- | :--- | :--- |
| **DEC-01** | Retención de evidencia digital | (a) 90 días (estándar inicial DPRIME).<br>(b) 5 años mínimo (estándar asegurador).<br>(c) Indefinida con anonimización. | **Se adopta (b):** Exigencia legal y regulatoria para responder ante litigios y auditorías de la Superintendencia. Cifrado continuo en reposo. |
| **DEC-02** | Definición operativa de validación cobrable | (a) Solo resoluciones automáticas en F4.<br>(b) Solo casos manuales en F1.<br>(c) Todo caso procesado y concluido (automático o derivado con dictamen). | **Se adopta (c):** Permite alinear a Finanzas y Producto; todo expediente que entrega un resultado útil y formalizado constituye consumo de plataforma. |
| **DEC-03** | Orden de visualización del puntaje en F1 | (a) Puntaje en cabecera junto al caso.<br>(b) Puntaje al final tras revisión probatoria.<br>(c) Puntaje oculto con botón de revelación. | **Se adopta (b):** Erradica el sesgo de anclaje cognitivo del liquidador, garantizando intervención humana real y defendible ante Compliance. |
| **DEC-04** | Valores por defecto de umbrales en F4 | (a) 85 aprobación / 60 derivación (demo original).<br>(b) 90 aprobación / 60 derivación.<br>(c) 95 aprobación / 70 derivación. | **Se adopta (b):** Conservador para marcha blanca; un falso positivo (fraude aprobado) es mucho más costoso que el exceso temporal de derivaciones. |
| **DEC-05** | Tiempos de procesamiento y SLA | (a) Garantía fija de 5 segundos sincrónicos.<br>(b) Diferenciación por tipo de archivo y SLA asincrónico para revisión asistida. | **Se adopta (b):** Procesamiento pesado no puede prometer 5 seg para PDFs complejos. Para F1 se fija SLA operativo de atención de 24 horas hábiles. |
| **DEC-06** | Comportamiento ante saturación de llamadas | (a) Rechazo con error HTTP 429.<br>(b) Encolamiento elástico con degradación suave. | **Se adopta (b):** Prioridad a la continuidad operacional del cliente; en Entrega 2 la carga se simula localmente. |
| **DEC-07** | Rechazo automático que afecta patrimonio | (a) Rechazo automático si puntaje $< 60$.<br>(b) Prohibición absoluta de rechazo automático; $< 60 \rightarrow$ derivación obligatoria. | **Se adopta (b):** Mandato legal irrenunciable. Solo un ser humano con justificación escrita puede rechazar un reembolso. |
| **DEC-08** | Autenticación y gestión de accesos | (a) Credenciales locales administradas en MIRA.<br>(b) Integración federada LDAP/Active Directory. | **Para v1/Entrega 2 se opera con (a) simplificado** (usuarios simulados por rol), dejando (b) planificado para integración corporativa v2. |
| **DEC-09** | Ventana de mantenimiento | (a) Horario nocturno único Chile.<br>(b) Arquitectura multi-zona horaria sin interrupción de servicio. | **Se adopta (b):** Diseño conceptual de alta disponibilidad; no afecta el scope local de la Entrega 2. |

---

## 2. Especificación del Modelo de Datos (Mock Dataset JSON)

Para dar estricto cumplimiento a la **Regla 4.3** (datos sintéticos con señales precalculadas), el archivo `dataset.json` que alimentará F4 y F1 define el siguiente esquema representativo:

```json
{
  "caso_id": "CASO-2026-001",
  "asegurado": {
    "rut": "15.420.819-3",
    "nombre": "Carlos Mendoza Tapia",
    "poliza_id": "POL-SALUD-8841",
    "plan": "Cobertura Preferente Max"
  },
  "prestador": {
    "rut": "76.321.900-K",
    "nombre": "Clínica RedSalud Valparaíso",
    "registro_superintendencia": "REG-MED-2019-88"
  },
  "prestacion": {
    "tipo": "Reembolso Consulta Médica de Especialidad",
    "monto_reclamado": 45000,
    "fecha_emision": "2026-09-28"
  },
  "evidencias": [
    {
      "id": "EVID-01",
      "tipo": "boleta_honorarios_electronica",
      "archivo_url": "/assets/evidencias/boleta_caso_001.jpg",
      "hallazgos_espaciales": [
        {
          "id": "HALLAZGO-01",
          "tipo": "alerta_tipografia",
          "descripcion": "Inconsistencia en fuente tipográfica del folio fiscal",
          "severidad": "critica",
          "coordenadas": {
            "top": 12.5,
            "left": 68.0,
            "width": 24.0,
            "height": 6.5
          }
        }
      ]
    }
  ],
  "senales_analiticas": {
    "autenticidad_documental": { "valor": 55, "minimo_exigido": 70, "critica": true },
    "consistencia_datos": { "valor": 95, "minimo_exigido": null, "critica": false },
    "habilitacion_prestador": { "valor": 98, "minimo_exigido": 65, "critica": true },
    "consistencia_identidad": { "valor": 90, "minimo_exigido": 75, "critica": true },
    "alerta_fraude_activa": false,
    "detalle_alerta_fraude": null
  },
  "estado_caso": "PENDIENTE_EVALUACION_F4",
  "resultado_f4": null,
  "resolucion_humana_f1": null
}
```

---

## 3. Catálogo de los 8 Casos Canónicos de Prueba

Los siguientes casos sintéticos deben ser implementados para garantizar la cobertura exhaustiva de la suite de pruebas automatizadas y la demostración en vivo:

1. **CP-01 (Aprobación Automática Limpia):**
   - Señales: Autenticidad 96, Consistencia 94, Prestador 98, Identidad 95. Puntaje F4: 95.9.
   - Sin fraude, todos los mínimos cumplidos.
   - Resultado F4: `APROBADO_AUTOMATICO`. No pasa a F1.
2. **CP-02 (Zona Gris / Puntuación Intermedia):**
   - Señales: Autenticidad 75, Consistencia 72, Prestador 80, Identidad 78. Puntaje F4: 75.9.
   - Sin fraude, mínimos cumplidos.
   - Resultado F4: `DERIVADO_A_REVISION_ASISTIDA` (Causal: *"Puntuación Intermedia / Zona Gris"*).
3. **CP-03 (Bajo Puntaje sin Fraude — Prueba Crítica DEC-07):**
   - Señales: Autenticidad 45, Consistencia 50, Prestador 40, Identidad 60. Puntaje F4: 48.2.
   - Sin fraude.
   - Resultado F4: `DERIVADO_A_REVISION_ASISTIDA` (Causal: *"Bajo Puntaje (<60) — Prohibición de Rechazo Automático"*).
4. **CP-04 (Puntaje Global Alto con Violación de Mínimo — Prueba H-12 / RF-11):**
   - Señales: Autenticidad 98, Consistencia 96, Identidad 95, Prestador **40** (mínimo: 65). Puntaje F4: 87.3 (o calibrado con pesos para superar 90).
   - Resultado F4: `DERIVADO_A_REVISION_ASISTIDA` (Causal: *"Incumplimiento de Umbral Mínimo: Habilitación de Prestador"*).
5. **CP-05 (Precedencia de Fraude con Puntaje Perfecto — Prueba RF-12):**
   - Señales: Autenticidad 99, Consistencia 98, Prestador 100, Identidad 99. Puntaje F4: 98.9.
   - Alerta de Fraude: `true` (Duplicidad de folio detectada en otra compañía).
   - Resultado F4: `DERIVADO_A_REVISION_ASISTIDA` (Causal: *"Alerta Crítica de Fraude: Prevalencia sobre Puntaje"*). Prioridad urgente.
6. **CP-06 (Falla de Módulo Analítico — Prueba RF-13):**
   - Señales: Autenticidad `null` (timeout de OCR), Consistencia 90, Prestador 95, Identidad 90.
   - Resultado F4: `DERIVADO_A_REVISION_ASISTIDA` (Causal: *"Información Incompleta por Falla de Módulo"*).
7. **CP-07 (Resolución Asistida con Marca de Discrepancia — Prueba RF-19):**
   - Caso derivado por bajo puntaje (CP-03) atendido por el operador en F1.
   - Acción del operador: `Aprobar` con justificación médica.
   - Resultado F1: `APROBADO_POR_OPERADOR`, `discrepancia_detectada: true`.
8. **CP-08 (Alerta de Vencimiento Inminente de SLA):**
   - Caso derivado con fecha de ingreso hace 23.5 horas hábiles.
   - Visualización F1: Badge rojo parpadeante, tiempo restante 30 minutos, ordenado al inicio de la bandeja.

---

## 4. Guía de Directrices Ergonómicas para UX (Sally)

1. **Jerarquía Visual Inflexible:**
   - La pantalla de detalle de F1 **debe cargar mostrando en su tercio superior el visor de documentos** y la ficha del reclamo.
   - En el tercio medio se despliega la tabla comparativa de señales analíticas evaluadas.
   - El bloque de **Puntaje de Confianza** (círculo de score o barra de progreso) **debe estar ubicado en el tercio inferior**, forzando al usuario a realizar scroll o desplazamiento deliberado.
2. **Paleta Semántica Accesible:**
   - Aprobado / Sin Alertas: Verde esmeralda (#10B981).
   - Advertencia / Zona Gris / SLA Medio: Ámbar (#F59E0B).
   - Alerta Crítica / Fraude / SLA Vencido: Rojo carmesí (#EF4444).
   - Fondo y Contraste: Modo claro profesional de alta legibilidad, cumpliendo WCAG 2.1 AA.
3. **Interacción con Hallazgos Espaciales:**
   - Las cajas delimitadoras deben tener animación de pulso sutil y resaltar al pasar el cursor (hover), desplegando un tooltip con la explicación del hallazgo.
