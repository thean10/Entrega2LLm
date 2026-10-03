# Input Reconciliation: project-brief.md vs. PRD

**Documento Fuente:** `_bmad-output/planning-artifacts/project-brief.md` (Mary, Business Analyst)  
**Artefactos Evaluados:** `prd.md` y `addendum.md` en `_bmad-output/planning-artifacts/prds/prd-MIRA-2026-10-03/`  
**Fecha:** 2026-10-03  

---

## 1. Verificación de Cobertura de Requisitos y Decisiones Clave

| Elemento en Project Brief | Cobertura en PRD / Addendum | Estado | Observación |
| :--- | :--- | :--- | :--- |
| **F4 (Puntaje y decisión por umbrales)** | §4.1 `prd.md` (`RF-11`, `RF-12`, `RF-13`, `FR-F4-01..03`) | **Completo** | Se modelan fórmulas ponderadas, precedencia de fraude y mínimos por señal. |
| **F1 (Bandeja de revisión asistida)** | §4.2 `prd.md` (`RF-19`, `FR-F1-01..05`) | **Completo** | Se cubre cola priorizada con SLA, visor documental, puntaje al final y marcas de discrepancia. |
| **DEC-07 (Prohibición rechazo automático)** | §4.1 (`FR-F4-02`), §3 Glosario, §7 (`SM-1`) | **Completo** | Caso con puntaje < 60 deriva forzosamente a F1. Rechazo exclusivo de operador humano. |
| **DEC-04 (Umbrales 90/60)** | §4.1 (`FR-F4-02`), §3 Glosario, `addendum.md` §1 | **Completo** | Aprobación $\ge 90$, zona intermedia 60-89, bajo puntaje $< 60$. |
| **DEC-03 (Puntaje al final anti-sesgo)** | §4.2 (`FR-F1-03`), §2.3 (`UJ-1`, `UJ-3`), §7 (`SM-3`) | **Completo** | Jerarquía visual estricta en F1: visor arriba, puntaje al pie de página. |
| **H-12 (Mínimos por señal individual)** | §4.1 (`RF-11`), §7 (`SM-5`), `addendum.md` §3 (`CP-04`) | **Completo** | Resuelve el hallazgo abierto de E1 con señales críticas definidas (autenticidad, prestador, identidad). |
| **RF-12 (Precedencia de fraude)** | §4.1 (`RF-12`), §2.3 (`UJ-1`), `addendum.md` §3 (`CP-05`) | **Completo** | Señal activa anula aprobación y asigna prioridad urgente en F1. |
| **RF-13 (Información incompleta / falla)** | §4.1 (`RF-13`), `addendum.md` §3 (`CP-06`) | **Completo** | Módulo caído o dato nulo deriva a F1 con indicación de faltante; nunca aprobación parcial. |
| **RF-19 (Marca de discrepancia)** | §4.2 (`RF-19`), §2.3 (`UJ-3`), §7 (`SM-2`), `addendum.md` §3 (`CP-07`) | **Completo** | Flag booleano y captura obligatoria de justificación para análisis posterior. |
| **Regla 4.3 (Datos sintéticos mock)** | §5 Non-Goals, §6.1 MVP Scope, `addendum.md` §2 y §3 | **Completo** | Se define esquema JSON de 8 casos canónicos sin llamadas a LLMs externos. |

---

## 2. Gaps y Matices Detectados
1. **Representación visual de bounding boxes:** El Brief menciona "coordenadas o marcas de ubicación espacial". El PRD y Addendum formalizan el estándar en porcentajes responsivos `(top, left, width, height)` para evitar problemas de resolución en diferentes monitores (incorporado como `[ASSUMPTION]`).
2. **Definición de SLA de atención en F1:** El Brief introduce el control de tiempos de atención. El PRD fija el SLA de negocio en 24 horas hábiles con semáforo tricolor (Verde $>4$h, Amarillo $1-4$h, Rojo $<1$h/vencido) para hacerlo programable y testable.
3. **Criterios de Aceptación (CA-01 a CA-07):** Todos los criterios del Project Brief fueron mapeados 1 a 1 hacia los requerimientos funcionales (`FR-F4-XX` y `FR-F1-XX`) y métricas de éxito (`SM-1` a `SM-5`).

**Conclusión:** Conciliación 100% exitosa; no existen pérdidas cualitativas ni desviaciones de alcance.
