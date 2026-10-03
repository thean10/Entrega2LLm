# Plataforma MIRA — Incremento Funcional F4 y F1

**Entrega 2 — Método BMAD (Software Design Document & Código Funcional)**  
**Proyecto:** Plataforma de Inteligencia Multimodal para Decisiones Empresariales en Salud  
**Organización:** DPRIME SpA / Aseguradora Piloto  
**Alcance Técnico:**
- **F4 — Motor de Decisión y Umbrales:** Núcleo determinista en Python 3.11+, FastAPI y Pydantic v2.
- **F1 — Bandeja de Revisión Asistida:** Single Page Application (Vite + Tailwind CSS) ergonómica con **Embudo de Tres Tercios Funcionales** para mitigar el sesgo de anclaje cognitivo (`DEC-03` / `RNF-08`), visor documental de anomalías espaciales y panel de dictamen humano soberano (`DEC-07` / `RF-19`).

---

## ⚡ Guía de Arranque Rápido en Menos de 5 Minutos (Criterio C4)

El sistema opera en modo 100% autónomo y desconectado, sin requerir credenciales en la nube ni servicios externos obligatorios.

### 1. Requisitos Previos
- **Python:** `>= 3.11` (verificado en Python 3.12)
- **Node.js:** `>= 18` (verificado en Node v24 y npm 11)
- **Git**

---

### 2. Paso a Paso de Inicialización

#### Paso 1: Inyección del Dataset Canónico de Pruebas (Regla 4.3)
Desde la raíz del repositorio, ejecute el script de inicialización para generar los 8 casos canónicos con evidencias y puntajes precalculados:
```bash
python backend/scripts/seed_dataset.py
```
*Salida esperada:* `✅ Inyección completada con éxito: 8 casos canónicos generados en 'backend/data/dataset.json'`.

---

#### Paso 2: Iniciar el Backend FastAPI y Motor F4
Instale las dependencias de backend e inicie el servidor ASGI en el puerto `8000`:
```bash
# Instalar dependencias backend (si no están instaladas)
pip install -r backend/requirements.txt

# Iniciar servidor Uvicorn
python -m uvicorn backend.app.main:app --port 8000 --reload
```
*El backend y la documentación interactiva Swagger estarán disponibles en:*  
`http://127.0.0.1:8000/docs`

---

#### Paso 3: Iniciar la Aplicación Web F1 (Frontend Vite)
En una nueva terminal, navegue a la carpeta `frontend`, instale los paquetes e inicie el entorno de desarrollo:
```bash
cd frontend
npm install
npm run dev
```
*Abra su navegador web en:*  
`http://localhost:5173`

---

## 🧪 Ejecución de Suites de Pruebas Automatizadas (Criterio C5)

### 1. Pruebas Unitarias, Integración y Verificación de los 10 RNF (Pytest)
Ejecute la suite completa de 24 pruebas automáticas de backend desde la raíz:
```bash
python -m pytest backend/tests/ -v
```
**Resumen de Cobertura Backend (100% PASSED):**
- `backend/tests/test_f4_engine.py`: 8 tests que verifican cálculo ponderado, mínimos individuales (`RF-11`), cortocircuito por fraude (`RF-12`), tolerancia a módulos nulos (`RF-13`) y prohibición estricta de rechazo automático (`RF-14` / `DEC-07`).
- `backend/tests/test_api_endpoints.py`: 6 tests de integración para contratos REST, ordenamiento de bandeja por SLA, captura de discrepancias y aislamiento multitenant.
- `backend/tests/test_rnf_validation.py`: 10 tests dedicados a comprobar matemáticamente los 10 Requisitos No Funcionales heredados de la Entrega 1 (`RNF-01` a `RNF-10`).

---

### 2. Prueba de Extremo a Extremo (E2E) de la Bandeja F1
La suite E2E recorre el ciclo de vida completo de un operador: carga de la bandeja, filtros por causal y SLA, inspección sin puntaje en el primer viewport, revisión de anomalías espaciales, revelación diferida y dictamen soberano con captura de discrepancia:
```bash
cd frontend
npm test
```
*Salida esperada:* `🎉 ¡TODAS LAS PRUEBAS DE LA SUITE E2E PASARON SATISFACTORIAMENTE (100%)!`.

---

## 📋 Catálogo Canónico de Casos de Prueba (Regla 4.3)

| ID Caso | Asegurado / Prestador | Causal de Derivación | Puntaje F4 | Estado Inicial | Aspecto Clave Verificado en F1 |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **`CASO-2026-001`** (`CP-01`) | Carlos Mendoza / C. RedSalud | *Ninguna* (Aprobación Limpia) | **95.7** | `APROBADO_AUTOMATICO` | Caso de control con puntaje $\ge 90$ sin pasar por mesa asistida. |
| **`CASO-2026-002`** (`CP-04`) | Claudio Lara / C. Santa María | Zona Gris / Intermedio | **77.4** | `DERIVADO` | Caso intermedio (60-89) con SLA normal (19h restantes). |
| **`CASO-2026-003`** (`CP-03`) | Juan Pablo Soto / C. Alameda | Bajo Puntaje ($<60$) — `DEC-07` | **48.3** | `DERIVADO` | Prohibición de rechazo automático: solo el liquidador humano puede denegar. |
| **`CASO-2026-004`** (`CP-02`) | Matías Bravo / Lab. San José | Mínimo Violado: Prestador (`RF-11`) | **83.1** | `DERIVADO` | Promedio ponderado alto (83.1) bloqueado por señal de prestador ($52 < 65$). |
| **`CASO-2026-005`** (`CP-05`) | Rosa Oyarzún / Farmacia Central | Alerta Crítica Fraude (`RF-12`) | **68.1** | `DERIVADO` | Precedencia absoluta de corte por fraude; boleta con anomalía tipográfica en folio. |
| **`CASO-2026-006`** (`CP-06`) | Beatriz Pino / Hosp. del Mar | Módulo Caído / Incompleto (`RF-13`)| **N/D** | `DERIVADO` | Señal de consistencia nula por caída de OCR; derivado sin inventar números. |
| **`CASO-2026-007`** (`CP-07`) | Verónica Alarcón / C. Visión Real| Bajo Puntaje / Discrepancia (`RF-19`)| **54.7** | `DERIVADO` | El operador aprueba excepcionalmente y el sistema sella `discrepancia_detectada=true`. |
| **`CASO-2026-008`** (`CP-08`) | Elena Morales / C. Valparaíso | SLA Inminente / Rojo (`DEC-05`) | **73.2** | `DERIVADO` | Vence en 25 minutos; badge rojo con parpadeo urgente para priorizar atención. |

---

## 🏛️ Jerarquía Visual Anti-Anclaje: El Embudo de Tres Tercios (DEC-03 / RNF-08)

La pantalla de detalle del siniestro (`/bandeja/:id`) mitiga el sesgo cognitivo de anclaje mediante la siguiente arquitectura visual vertical:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. TERCIO SUPERIOR (Viewport Inicial 100vh - min-h-[820px]): Inspección Factual │
│   • Cabecera Adherente: ID del Caso, Causal de Derivación, Temporizador SLA     │
│   • INVARIANTE RNF-08: ¡PROHIBIDA LA VISUALIZACIÓN DEL PUNTAJE NUMÉRICO!        │
│   • Columna Izquierda: Ficha del Asegurado, Prestador y Prestación              │
│   • Columna Derecha: Visor Documental con Pan & Zoom y Bounding Boxes Rojos     │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ Desplazamiento consciente (Scroll)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 2. TERCIO MEDIO: Desglose de Señales Analíticas Explicables                     │
│   • 4 Tarjetas Comparativas: Autenticidad (35%), Consistencia (25%),           │
│     Habilitación Prestador (20%) y Validación de Identidad (20%)                │
│   • Indicador de umbrales mínimos por componente (RF-11 / H-12)                 │
│   • Banners destacados de alerta de fraude prevalente (RF-12) y módulos caídos  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ Desplazamiento al bloque resolutivo
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 3. TERCIO INFERIOR: Revelación Diferida de Puntaje y Dictamen Soberano          │
│   • Revelación del Puntaje Global Ponderado (0-100) y desglose de fórmula S     │
│   • Advertencia ética: El puntaje es meramente referencial (DEC-03 / DEC-07)   │
│   • Panel Resolutivo: [ Aprobar ] [ Rechazar ] [ Solicitar Antecedentes ]       │
│   • Banner Reactivo de Discrepancia Detectada (RF-19) si se aprueba con alerta  │
│   • Campo de justificación obligatoria (mínimo 15 caracteres)                   │
│   • Emisión de dictamen sellado con hash inmutable SHA-256 (RNF-04 / DEC-10)    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Matriz de Cumplimiento de los 10 Requisitos No Funcionales (RNF-01..10)

| ID | Atributo de Calidad | Mecanismo Arquitectónico | Caso de Prueba Verificador | Estatus |
| :---: | :--- | :--- | :---: | :---: |
| **RNF-01** | Rendimiento API (100 rpm) | Middleware *Leaky Bucket* elástico; peticiones excedentes retornan HTTP 202 con `Retry-After`. Cero códigos 429. | `test_rnf_01_leaky_bucket_zero_descartes_429` | **PASSED** |
| **RNF-02** | Confiabilidad ante Fallos | Repositorios duales con conmutación transparente de Firestore a `LocalJsonRepository`. | `test_rnf_02_confiabilidad_fallback_local` | **PASSED** |
| **RNF-03** | Onboarding Ultrarrápido | Aprovisionamiento con datos sintéticos mediante `seed_dataset.py` en $<5$ segundos (Criterio C4). | `test_rnf_03_eficiencia_onboarding_sub_5_segundos` | **PASSED** |
| **RNF-04** | Auditabilidad y Reconstrucción | Registro append-only encadenado con hash SHA-256 (`DEC-10`). 0 discrepancias forenses. | `test_rnf_04_auditabilidad_reconstruccion_sha256` | **PASSED** |
| **RNF-05** | Confidencialidad Multitenant | Middleware de seguridad exigiendo `X-Tenant-ID`. Bloqueo con HTTP 403 Forbidden ante accesos cruzados (`DEC-08`). | `test_rnf_05_aislamiento_multitenant_estricto` | **PASSED** |
| **RNF-06** | Consistencia en Conteo | Contador atómico en transacción unificada (`DEC-02`). $\text{Diferencia} = 0$ entre cliente y facturación. | `test_rnf_06_consistencia_conteo_cobrable_cliente_vs_finanzas` | **PASSED** |
| **RNF-07** | Gobernanza de Umbrales | Regla de dominio de segregación de funciones: solicitante $\neq$ aprobador para cambios de corte. | `test_rnf_07_gobernanza_segregacion_funciones` | **PASSED** |
| **RNF-08** | Mitigación Sesgo de Anclaje | Estructura jerárquica estricta: `#panel-puntaje-confianza` posterior al visor y señales en el DOM. | `test_rnf_08_mitigacion_sesgo_anclaje_orden_componentes` | **PASSED** |
| **RNF-09** | Custodia Quinquenal | Guardián normativo que deniega el borrado de evidencias con menos de 5 años (`DEC-01`). | `test_rnf_09_retencion_quinquenal_obligatoria` | **PASSED** |
| **RNF-10** | Aislamiento de Integración | Despachador de notificaciones y firmas HMAC segregadas por `tenant_id` sin contaminación cruzada. | `test_rnf_10_aislamiento_callbacks_hmac_por_tenant` | **PASSED** |

---

## 👥 Roles del Equipo BMAD Responsables
- **Desarrolladora Senior:** Amelia 💻 (`bmad-agent-dev`)
- **Ingeniero de Aseguramiento de Calidad:** QA Engineer 🧪 (`bmad-qa-generate-e2e-tests`)
- **Diseñadora UX:** Sally 🎨 (`bmad-agent-ux-designer`)
- **Arquitecto de Sistemas:** Winston 🏛️ (`bmad-agent-architect`)
- **Scrum Master:** SM 📋