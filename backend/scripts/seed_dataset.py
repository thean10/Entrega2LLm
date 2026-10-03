"""
Script de Inicialización del Dataset Sintético Canónico (8 Casos de Prueba).
Referencia Cruzada:
- HU E2: HU-QA-01 (Dataset Sintético Canónico y Script de Inicialización Rápida)
- HU E1: HU-58 (Arranque ágil y onboarding de operación / RNF-03)
- Regla 4.3 de las Bases E2 y Criterio C4 (< 5 segundos de ejecución)
- Casos Canónicos: CP-01 a CP-08 (Cubre F4, F1, SLA, Fraude, Mínimos, Módulos Caídos y Discrepancias)
"""

import json
import base64
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path


def generar_svg_boleta(
    folio: str,
    paciente_nombre: str,
    paciente_rut: str,
    prestador_nombre: str,
    prestacion_desc: str,
    monto_clp: int,
    alerta_roja: bool = False,
    texto_alerta: str = "",
) -> str:
    """Genera un comprobante médico realista en SVG y lo retorna codificado como Data URI."""
    monto_formateado = f"${monto_clp:,}".replace(",", ".")
    banner_alerta_svg = ""
    if alerta_roja:
        banner_alerta_svg = f"""
        <!-- Resaltado de anomalía forense detectada -->
        <rect x="340" y="55" width="220" height="40" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,2"/>
        <text x="350" y="80" font-family="monospace" font-size="12" font-weight="bold" fill="#dc2626">⚠️ {texto_alerta}</text>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 800" width="100%" height="100%">
  <!-- Fondo documento -->
  <defs>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.15"/>
    </filter>
  </defs>
  <rect x="10" y="10" width="580" height="780" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" filter="url(#shadow)"/>
  
  <!-- Encabezado Clínico -->
  <rect x="10" y="10" width="580" height="110" rx="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
  <circle cx="55" cy="65" r="28" fill="#0284c7"/>
  <text x="44" y="74" font-family="sans-serif" font-size="26" font-weight="bold" fill="#ffffff">✚</text>
  
  <text x="100" y="52" font-family="sans-serif" font-size="19" font-weight="bold" fill="#0f172a">{prestador_nombre}</text>
  <text x="100" y="72" font-family="sans-serif" font-size="12" fill="#64748b">Prestador Médico Acreditado — Superintendencia de Salud</text>
  <text x="100" y="90" font-family="sans-serif" font-size="11" fill="#475569">Casa Central: Av. Providencia 1920, Santiago • Fono: +56 2 2890 4000</text>
  
  <!-- Recuadro Folio Electrónico -->
  <rect x="380" y="25" width="190" height="70" rx="6" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>
  <text x="400" y="48" font-family="sans-serif" font-size="11" font-weight="bold" fill="#0284c7">R.U.T.: 76.321.900-K</text>
  <text x="400" y="66" font-family="sans-serif" font-size="13" font-weight="bold" fill="#dc2626">BOLETA N° {folio}</text>
  <text x="400" y="84" font-family="sans-serif" font-size="10" fill="#64748b">S.I.I. — SANTIAGO ORIENTE</text>
  
  {banner_alerta_svg}

  <!-- Datos del Paciente / Asegurado -->
  <rect x="30" y="140" width="540" height="110" rx="6" fill="#f1f5f9" stroke="#e2e8f0"/>
  <text x="45" y="165" font-family="sans-serif" font-size="13" font-weight="bold" fill="#334155">ANTECEDENTES DEL PACIENTE / AFILIADO</text>
  <line x1="45" y1="173" x2="555" y2="173" stroke="#cbd5e1" stroke-width="1"/>
  
  <text x="45" y="196" font-family="sans-serif" font-size="12" font-weight="600" fill="#475569">Nombre:</text>
  <text x="110" y="196" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a">{paciente_nombre}</text>
  
  <text x="45" y="218" font-family="sans-serif" font-size="12" font-weight="600" fill="#475569">R.U.T.:</text>
  <text x="110" y="218" font-family="sans-serif" font-size="12" fill="#0f172a">{paciente_rut}</text>
  
  <text x="320" y="196" font-family="sans-serif" font-size="12" font-weight="600" fill="#475569">Fecha Atención:</text>
  <text x="430" y="196" font-family="sans-serif" font-size="12" fill="#0f172a">28/09/2026</text>
  
  <text x="320" y="218" font-family="sans-serif" font-size="12" font-weight="600" fill="#475569">Forma de Pago:</text>
  <text x="430" y="218" font-family="sans-serif" font-size="12" fill="#0f172a">Reembolso Web</text>

  <!-- Detalle Prestación Médica -->
  <rect x="30" y="270" width="540" height="230" rx="6" fill="#ffffff" stroke="#cbd5e1"/>
  <rect x="30" y="270" width="540" height="35" rx="6" fill="#e2e8f0"/>
  <text x="45" y="293" font-family="sans-serif" font-size="12" font-weight="bold" fill="#334155">CÓDIGO / DESCRIPCIÓN DEL ACTO MÉDICO</text>
  <text x="460" y="293" font-family="sans-serif" font-size="12" font-weight="bold" fill="#334155">VALOR TOTAL</text>
  
  <text x="45" y="335" font-family="sans-serif" font-size="12" font-weight="600" fill="#0f172a">01-01-001</text>
  <text x="130" y="335" font-family="sans-serif" font-size="12" fill="#1e293b">{prestacion_desc}</text>
  <text x="470" y="335" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0f172a">{monto_formateado}</text>
  
  <line x1="45" y1="360" x2="555" y2="360" stroke="#f1f5f9" stroke-width="1"/>
  <text x="45" y="390" font-family="sans-serif" font-size="11" fill="#64748b">Médico Tratante: Dr. Alejandro Valenzuela M. (Reg. Col. Médicos 44921)</text>
  <text x="45" y="410" font-family="sans-serif" font-size="11" fill="#64748b">Diagnóstico: J00 Rinofaringitis Aguda / Control de Evolución Clínica</text>
  <text x="45" y="430" font-family="sans-serif" font-size="11" fill="#64748b">Servicio: Unidad de Consultas Ambulatorias</text>

  <!-- Total General -->
  <rect x="340" y="440" width="230" height="50" rx="4" fill="#0284c7"/>
  <text x="355" y="470" font-family="sans-serif" font-size="14" font-weight="bold" fill="#ffffff">TOTAL A REEMBOLSAR:</text>
  <text x="495" y="470" font-family="sans-serif" font-size="14" font-weight="bold" fill="#ffffff">{monto_formateado}</text>

  <!-- Timbre y Código de Barras -->
  <rect x="50" y="530" width="220" height="85" rx="4" fill="#ffffff" stroke="#94a3b8" stroke-dasharray="2,2"/>
  <circle cx="160" cy="572" r="32" fill="none" stroke="#2563eb" stroke-width="2" opacity="0.6"/>
  <text x="122" y="568" font-family="sans-serif" font-size="9" font-weight="bold" fill="#2563eb" opacity="0.8">CLÍNICA HABILITADA</text>
  <text x="135" y="582" font-family="sans-serif" font-size="8" fill="#2563eb" opacity="0.8">RECEPCIÓN CONFORME</text>
  
  <!-- Timbre Electrónico SII Simulado -->
  <rect x="300" y="530" width="270" height="85" fill="#f8fafc" stroke="#64748b"/>
  <line x1="310" y1="545" x2="560" y2="545" stroke="#000" stroke-width="3"/>
  <line x1="310" y1="552" x2="560" y2="552" stroke="#000" stroke-width="1"/>
  <line x1="310" y1="560" x2="560" y2="560" stroke="#000" stroke-width="4"/>
  <line x1="310" y1="570" x2="560" y2="570" stroke="#000" stroke-width="2"/>
  <line x1="310" y1="578" x2="560" y2="578" stroke="#000" stroke-width="5"/>
  <text x="315" y="602" font-family="monospace" font-size="9" fill="#334155">Timbre Electrónico D.S. N° 55 de 2004 SII</text>
  
  <!-- Pie de Página Legal -->
  <text x="30" y="740" font-family="sans-serif" font-size="9" fill="#94a3b8">Este documento constituye una copia digital emitida para fines de liquidación de reembolsos en plataforma MIRA.</text>
  <text x="30" y="755" font-family="sans-serif" font-size="9" fill="#94a3b8">La adulteración o uso malicioso de este comprobante sanciona conforme al Art. 197 del Código Penal de Chile.</text>
</svg>"""
    data_uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return data_uri


def generar_dataset_canonico() -> list:
    """Construye los 8 casos canónicos de prueba acordados."""
    ahora = datetime.now(timezone.utc)

    # 1. CASO-2026-001 (CP-01): Aprobación limpia (>=90 pts)
    caso_001 = {
        "caso_id": "CASO-2026-001",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "15.420.819-3",
            "nombre": "Carlos Mendoza Tapia",
            "poliza_id": "POL-SALUD-8841",
            "plan": "Cobertura Preferente Max",
        },
        "prestador": {
            "rut": "76.321.900-K",
            "nombre": "Clínica RedSalud Providencia",
            "registro_superintendencia": "REG-MED-2019-88",
        },
        "prestacion": {
            "tipo": "Reembolso Consulta Médica de Especialidad (Cardiología)",
            "monto_reclamado": 45000,
            "fecha_emision": "2026-09-28",
        },
        "evidencias": [
            {
                "id": "EVID-001",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Boleta_Electrónica_45890.pdf",
                "archivo_url": generar_svg_boleta("45890", "Carlos Mendoza Tapia", "15.420.819-3", "Clínica RedSalud Providencia", "Consulta Médica Especialidad", 45000),
                "hallazgos_espaciales": [],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 96.0, "minimo_exigido": 70.0, "critica": True},
            "consistencia_datos": {"valor": 94.0, "minimo_exigido": None, "critica": False},
            "habilitacion_prestador": {"valor": 98.0, "minimo_exigido": 65.0, "critica": True},
            "consistencia_identidad": {"valor": 95.0, "minimo_exigido": 75.0, "critica": True},
            "alerta_fraude_activa": False,
            "detalle_alerta_fraude": None,
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=3)).isoformat(),
            "limite_timestamp": (ahora + timedelta(hours=21)).isoformat(),
            "duracion_horas": 24,
            "horas_restantes": 21.0,
            "tiempo_restante_minutos": 1260,
            "estado_sla": "verde",
        },
        "estado_caso": "APROBADO_AUTOMATICO",
        "resultado_f4": {
            "puntaje_calculado": 95.7,
            "desglose_componentes": {
                "autenticidad_documental": 33.6,
                "consistencia_datos": 23.5,
                "habilitacion_prestador": 19.6,
                "consistencia_identidad": 19.0,
            },
            "decision_algoritmica": "APROBADO_AUTOMATICO",
            "causal_derivacion": None,
            "detalle_causal": "Expediente con alta confianza (95.7 >= 90.0). Aprobación directa autorizada.",
            "timestamp_evaluacion": (ahora - timedelta(hours=3)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "8f3b25916c02934ad27fe9a12b6e1590498305c48b259586118d09ca084931a1",
        "fecha_creacion": (ahora - timedelta(hours=3)).isoformat(),
    }

    # 2. CASO-2026-002 (CP-04): Zona Gris / Intermedia (60-89 pts)
    caso_002 = {
        "caso_id": "CASO-2026-002",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "12.894.312-5",
            "nombre": "Claudio Lara Santander",
            "poliza_id": "POL-SALUD-3312",
            "plan": "Plan Integral Familiar",
        },
        "prestador": {
            "rut": "76.452.110-3",
            "nombre": "Centro Médico Santa María",
            "registro_superintendencia": "REG-MED-2021-12",
        },
        "prestacion": {
            "tipo": "Sesión de Kinesioterapia Integral (x10 sesiones)",
            "monto_reclamado": 120000,
            "fecha_emision": "2026-09-27",
        },
        "evidencias": [
            {
                "id": "EVID-002",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Boleta_Kine_SantaMaria.pdf",
                "archivo_url": generar_svg_boleta("88412", "Claudio Lara Santander", "12.894.312-5", "Centro Médico Santa María", "Sesiones Kinesioterapia Integral", 120000),
                "hallazgos_espaciales": [],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 78.0, "minimo_exigido": 70.0, "critica": True},
            "consistencia_datos": {"valor": 82.0, "minimo_exigido": None, "critica": False},
            "habilitacion_prestador": {"valor": 72.0, "minimo_exigido": 65.0, "critica": True},
            "consistencia_identidad": {"valor": 76.0, "minimo_exigido": 75.0, "critica": True},
            "alerta_fraude_activa": False,
            "detalle_alerta_fraude": None,
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=4, minutes=50)).isoformat(),
            "limite_timestamp": (ahora + timedelta(hours=19, minutes=10)).isoformat(),
            "duracion_horas": 24,
            "horas_restantes": 19.2,
            "tiempo_restante_minutos": 1150,
            "estado_sla": "verde",
        },
        "estado_caso": "DERIVADO_A_REVISION_ASISTIDA",
        "resultado_f4": {
            "puntaje_calculado": 77.4,
            "desglose_componentes": {
                "autenticidad_documental": 27.3,
                "consistencia_datos": 20.5,
                "habilitacion_prestador": 14.4,
                "consistencia_identidad": 15.2,
            },
            "decision_algoritmica": "DERIVADO_A_REVISION_ASISTIDA",
            "causal_derivacion": "ZONA_GRIS",
            "detalle_causal": "Puntaje de confianza en zona gris (77.4 entre 60.0 y 90.0). Requiere inspección asistida humana.",
            "timestamp_evaluacion": (ahora - timedelta(hours=4, minutes=50)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "4b6a12c8e19034af72e90c889a2b5e190348705c48b259586118d09ca084931b2",
        "fecha_creacion": (ahora - timedelta(hours=4, minutes=50)).isoformat(),
    }

    # 3. CASO-2026-003 (CP-03): Derivación por Bajo Puntaje (<60) — Mandato DEC-07
    caso_003 = {
        "caso_id": "CASO-2026-003",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "18.301.992-1",
            "nombre": "Juan Pablo Soto Cárdenas",
            "poliza_id": "POL-SALUD-5520",
            "plan": "Plan Joven Esencial",
        },
        "prestador": {
            "rut": "77.892.400-8",
            "nombre": "Centro Radiológico y Diagnóstico Alameda",
            "registro_superintendencia": "REG-MED-2018-44",
        },
        "prestacion": {
            "tipo": "Resonancia Magnética de Columna Lumbar con Contraste",
            "monto_reclamado": 185000,
            "fecha_emision": "2026-09-26",
        },
        "evidencias": [
            {
                "id": "EVID-003",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Comprobante_Radiologia_Alameda.jpg",
                "archivo_url": generar_svg_boleta("10492", "Juan Pablo Soto Cárdenas", "18.301.992-1", "Centro Radiológico Alameda", "Resonancia Magnética Columna", 185000),
                "hallazgos_espaciales": [
                    {
                        "id": "HALLAZGO-003-A",
                        "tipo": "calidad_imagen_degradada",
                        "descripcion": "Baja resolución y artefactos de compresión en el cuerpo de la boleta",
                        "severidad": "moderada",
                        "coordenadas": {"top": 35.0, "left": 10.0, "width": 80.0, "height": 30.0},
                    }
                ],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 48.0, "minimo_exigido": 70.0, "critica": False},
            "consistencia_datos": {"valor": 50.0, "minimo_exigido": None, "critica": False},
            "habilitacion_prestador": {"valor": 45.0, "minimo_exigido": 65.0, "critica": False},
            "consistencia_identidad": {"valor": 50.0, "minimo_exigido": 75.0, "critica": False},
            "alerta_fraude_activa": False,
            "detalle_alerta_fraude": None,
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=9, minutes=45)).isoformat(),
            "limite_timestamp": (ahora + timedelta(hours=14, minutes=15)).isoformat(),
            "duracion_horas": 24,
            "horas_restantes": 14.2,
            "tiempo_restante_minutos": 855,
            "estado_sla": "amarillo",
        },
        "estado_caso": "DERIVADO_A_REVISION_ASISTIDA",
        "resultado_f4": {
            "puntaje_calculado": 48.3,
            "desglose_componentes": {
                "autenticidad_documental": 16.8,
                "consistencia_datos": 12.5,
                "habilitacion_prestador": 9.0,
                "consistencia_identidad": 10.0,
            },
            "decision_algoritmica": "DERIVADO_A_REVISION_ASISTIDA",
            "causal_derivacion": "BAJO_PUNTAJE",
            "detalle_causal": "Puntaje crítico (48.3 < 60.0). Conforme al mandato DEC-07 y RF-14, el sistema tiene prohibición de emitir rechazos automáticos. Requiere dictamen humano soberano.",
            "timestamp_evaluacion": (ahora - timedelta(hours=9, minutes=45)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "9a12c8e19034af72e90c889a2b5e190348705c48b259586118d09ca084931c3",
        "fecha_creacion": (ahora - timedelta(hours=9, minutes=45)).isoformat(),
    }

    # 4. CASO-2026-004 (CP-02): Mínimo Individual Insatisfecho (RF-11 / H-12)
    caso_004 = {
        "caso_id": "CASO-2026-004",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "16.782.109-8",
            "nombre": "Matías Bravo Osses",
            "poliza_id": "POL-SALUD-7711",
            "plan": "Plan Senior Preferente",
        },
        "prestador": {
            "rut": "76.991.002-1",
            "nombre": "Laboratorio Clínico San José",
            "registro_superintendencia": "REG-MED-2015-09",
        },
        "prestacion": {
            "tipo": "Perfil Lipídico, Hemograma y PCR Cuantitativa",
            "monto_reclamado": 38000,
            "fecha_emision": "2026-09-28",
        },
        "evidencias": [
            {
                "id": "EVID-004",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Comprobante_Examenes_SanJose.pdf",
                "archivo_url": generar_svg_boleta("55102", "Matías Bravo Osses", "16.782.109-8", "Laboratorio Clínico San José", "Perfil Lipídico y Hemograma", 38000),
                "hallazgos_espaciales": [
                    {
                        "id": "HALLAZGO-004-A",
                        "tipo": "alerta_habilitacion_prestador",
                        "descripcion": "Registro sanitario del prestador con vencimiento reportado en Superintendencia",
                        "severidad": "critica",
                        "coordenadas": {"top": 5.0, "left": 15.0, "width": 45.0, "height": 12.0},
                    }
                ],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 92.0, "minimo_exigido": 70.0, "critica": True},
            "consistencia_datos": {"valor": 90.0, "minimo_exigido": None, "critica": False},
            "habilitacion_prestador": {"valor": 52.0, "minimo_exigido": 65.0, "critica": True},  # VIOLADO (52 < 65)
            "consistencia_identidad": {"valor": 90.0, "minimo_exigido": 75.0, "critica": True},
            "alerta_fraude_activa": False,
            "detalle_alerta_fraude": None,
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=3)).isoformat(),
            "limite_timestamp": (ahora + timedelta(hours=21)).isoformat(),
            "duracion_horas": 24,
            "horas_restantes": 21.0,
            "tiempo_restante_minutos": 1260,
            "estado_sla": "verde",
        },
        "estado_caso": "DERIVADO_A_REVISION_ASISTIDA",
        "resultado_f4": {
            "puntaje_calculado": 83.1,
            "desglose_componentes": {
                "autenticidad_documental": 32.2,
                "consistencia_datos": 22.5,
                "habilitacion_prestador": 10.4,
                "consistencia_identidad": 18.0,
            },
            "decision_algoritmica": "DERIVADO_A_REVISION_ASISTIDA",
            "causal_derivacion": "MINIMO_SENAL_INSATISFECHO",
            "detalle_causal": "La señal crítica 'habilitacion_prestador' tiene un valor de 52.0, inferior al umbral mínimo exigido de 65.0 (RF-11 / H-12).",
            "timestamp_evaluacion": (ahora - timedelta(hours=3)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "1a22c8e19034af72e90c889a2b5e190348705c48b259586118d09ca084931d4",
        "fecha_creacion": (ahora - timedelta(hours=3)).isoformat(),
    }

    # 5. CASO-2026-005 (CP-05): Sospecha de Fraude Activa (RF-12 / H-03)
    caso_005 = {
        "caso_id": "CASO-2026-005",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "11.234.567-9",
            "nombre": "Rosa Oyarzún Vera",
            "poliza_id": "POL-SALUD-9002",
            "plan": "Plan Cobertura Total Plus",
        },
        "prestador": {
            "rut": "76.112.304-5",
            "nombre": "Farmacia y Botica Central",
            "registro_superintendencia": "REG-MED-2017-31",
        },
        "prestacion": {
            "tipo": "Reembolso Medicamentos de Alto Costo (Tratamiento Inmunológico)",
            "monto_reclamado": 340000,
            "fecha_emision": "2026-09-29",
        },
        "evidencias": [
            {
                "id": "EVID-005",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Factura_Medicamentos_Adulterada.jpg",
                "archivo_url": generar_svg_boleta(
                    "45892",
                    "Rosa Oyarzún Vera",
                    "11.234.567-9",
                    "Farmacia Central",
                    "Medicamento Biológico 200mg",
                    340000,
                    alerta_roja=True,
                    texto_alerta="FOLIO ADULTERADO N° 45892",
                ),
                "hallazgos_espaciales": [
                    {
                        "id": "HALLAZGO-FRAUDE-01",
                        "tipo": "alerta_tipografia_sobrepuesta",
                        "descripcion": "Inconsistencia en fuente tipográfica del folio fiscal (Doble impresión sobrepuesta detectada)",
                        "severidad": "critica",
                        "coordenadas": {"top": 3.0, "left": 63.0, "width": 32.0, "height": 9.0},
                    }
                ],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 32.0, "minimo_exigido": 70.0, "critica": True},
            "consistencia_datos": {"valor": 85.0, "minimo_exigido": None, "critica": False},
            "habilitacion_prestador": {"valor": 90.0, "minimo_exigido": 65.0, "critica": True},
            "consistencia_identidad": {"valor": 88.0, "minimo_exigido": 75.0, "critica": True},
            "alerta_fraude_activa": True,  # PRECEDENCIA ABSOLUTA RF-12
            "detalle_alerta_fraude": "Alteración tipográfica deliberada detectada en el folio N° 45892 (Doble impresión sobrepuesta).",
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=5, minutes=20)).isoformat(),
            "limite_timestamp": (ahora + timedelta(hours=18, minutes=40)).isoformat(),
            "duracion_horas": 24,
            "horas_restantes": 18.6,
            "tiempo_restante_minutos": 1120,
            "estado_sla": "verde",
        },
        "estado_caso": "DERIVADO_A_REVISION_ASISTIDA",
        "resultado_f4": {
            "puntaje_calculado": 68.1,
            "desglose_componentes": {
                "autenticidad_documental": 11.2,
                "consistencia_datos": 21.25,
                "habilitacion_prestador": 18.0,
                "consistencia_identidad": 17.6,
            },
            "decision_algoritmica": "DERIVADO_A_REVISION_ASISTIDA",
            "causal_derivacion": "ALERTA_CRITICA_FRAUDE",
            "detalle_causal": "Alerta de fraude activa: Alteración tipográfica deliberada detectada en el folio N° 45892 (Doble impresión sobrepuesta). Precedencia de corte absoluto sobre cualquier puntaje (RF-12 / H-03).",
            "timestamp_evaluacion": (ahora - timedelta(hours=5, minutes=20)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "5c33c8e19034af72e90c889a2b5e190348705c48b259586118d09ca084931e5",
        "fecha_creacion": (ahora - timedelta(hours=5, minutes=20)).isoformat(),
    }

    # 6. CASO-2026-006 (CP-06): Información Incompleta / Fallo de Módulo (RF-13)
    caso_006 = {
        "caso_id": "CASO-2026-006",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "14.512.809-2",
            "nombre": "Beatriz Pino Navarrete",
            "poliza_id": "POL-SALUD-6120",
            "plan": "Plan Familiar Preferente",
        },
        "prestador": {
            "rut": "77.102.941-K",
            "nombre": "Hospital del Mar Viña del Mar",
            "registro_superintendencia": "REG-MED-2016-19",
        },
        "prestacion": {
            "tipo": "Procedimiento Quirúrgico Menor Ambulatorio",
            "monto_reclamado": 95000,
            "fecha_emision": "2026-09-28",
        },
        "evidencias": [
            {
                "id": "EVID-006",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Comprobante_Hospital_DelMar.pdf",
                "archivo_url": generar_svg_boleta("77124", "Beatriz Pino Navarrete", "14.512.809-2", "Hospital del Mar", "Procedimiento Ambulatorio", 95000),
                "hallazgos_espaciales": [],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 92.0, "minimo_exigido": 70.0, "critica": True},
            "consistencia_datos": {"valor": None, "minimo_exigido": None, "critica": False},  # MÓDULO NO DISPONIBLE
            "habilitacion_prestador": {"valor": 95.0, "minimo_exigido": 65.0, "critica": True},
            "consistencia_identidad": {"valor": 90.0, "minimo_exigido": 75.0, "critica": True},
            "alerta_fraude_activa": False,
            "detalle_alerta_fraude": None,
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=1, minutes=30)).isoformat(),
            "limite_timestamp": (ahora + timedelta(hours=22, minutes=30)).isoformat(),
            "duracion_horas": 24,
            "horas_restantes": 22.5,
            "tiempo_restante_minutos": 1350,
            "estado_sla": "verde",
        },
        "estado_caso": "DERIVADO_A_REVISION_ASISTIDA",
        "resultado_f4": {
            "puntaje_calculado": None,
            "desglose_componentes": {},
            "decision_algoritmica": "DERIVADO_A_REVISION_ASISTIDA",
            "causal_derivacion": "INFORMACION_INCOMPLETA",
            "detalle_causal": "Fallo de disponibilidad analítica o información incompleta en módulo(s): consistencia_datos. Derivado a revisión asistida sin imputar valores ficticios (RF-13).",
            "timestamp_evaluacion": (ahora - timedelta(hours=1, minutes=30)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "6d44c8e19034af72e90c889a2b5e190348705c48b259586118d09ca084931f6",
        "fecha_creacion": (ahora - timedelta(hours=1, minutes=30)).isoformat(),
    }

    # 7. CASO-2026-007 (CP-07): Caso para Prueba de Discrepancia del Operador (RF-19)
    caso_007 = {
        "caso_id": "CASO-2026-007",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "13.621.844-4",
            "nombre": "Verónica Alarcón Lagos",
            "poliza_id": "POL-SALUD-4421",
            "plan": "Plan Vida Plena Max",
        },
        "prestador": {
            "rut": "76.840.119-2",
            "nombre": "Clínica Oftalmológica Visión Real",
            "registro_superintendencia": "REG-MED-2020-04",
        },
        "prestacion": {
            "tipo": "Procedimiento Láser Quirúrgico de Urgencia",
            "monto_reclamado": 210000,
            "fecha_emision": "2026-09-29",
        },
        "evidencias": [
            {
                "id": "EVID-007",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Comprobante_VisionReal_Laser.pdf",
                "archivo_url": generar_svg_boleta("30291", "Verónica Alarcón Lagos", "13.621.844-4", "Clínica Oftalmológica Visión Real", "Procedimiento Láser Urgencia", 210000),
                "hallazgos_espaciales": [],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 54.0, "minimo_exigido": 70.0, "critica": False},
            "consistencia_datos": {"valor": 55.0, "minimo_exigido": None, "critica": False},
            "habilitacion_prestador": {"valor": 50.0, "minimo_exigido": 65.0, "critica": False},
            "consistencia_identidad": {"valor": 60.0, "minimo_exigido": 75.0, "critica": False},
            "alerta_fraude_activa": False,
            "detalle_alerta_fraude": None,
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=12)).isoformat(),
            "limite_timestamp": (ahora + timedelta(hours=12)).isoformat(),
            "duracion_horas": 24,
            "horas_restantes": 12.0,
            "tiempo_restante_minutos": 720,
            "estado_sla": "amarillo",
        },
        "estado_caso": "DERIVADO_A_REVISION_ASISTIDA",
        "resultado_f4": {
            "puntaje_calculado": 54.7,
            "desglose_componentes": {
                "autenticidad_documental": 18.9,
                "consistencia_datos": 13.75,
                "habilitacion_prestador": 10.0,
                "consistencia_identidad": 12.0,
            },
            "decision_algoritmica": "DERIVADO_A_REVISION_ASISTIDA",
            "causal_derivacion": "BAJO_PUNTAJE",
            "detalle_causal": "Puntaje crítico (54.7 < 60.0). Conforme al mandato DEC-07 y RF-14, requiere dictamen humano soberano.",
            "timestamp_evaluacion": (ahora - timedelta(hours=12)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "7e55c8e19034af72e90c889a2b5e190348705c48b259586118d09ca084931a7",
        "fecha_creacion": (ahora - timedelta(hours=12)).isoformat(),
    }

    # 8. CASO-2026-008 (CP-08): Caso Crítico con SLA Inminente (<1 hora restante)
    caso_008 = {
        "caso_id": "CASO-2026-008",
        "tenant_id": "org_aseguradora_piloto",
        "asegurado": {
            "rut": "17.902.411-K",
            "nombre": "Elena Morales Bahamondes",
            "poliza_id": "POL-SALUD-9912",
            "plan": "Plan Senior Preferente",
        },
        "prestador": {
            "rut": "76.321.900-K",
            "nombre": "Clínica RedSalud Valparaíso",
            "registro_superintendencia": "REG-MED-2019-88",
        },
        "prestacion": {
            "tipo": "Consulta de Urgencia Traumatológica y Yeso Brazo",
            "monto_reclamado": 75000,
            "fecha_emision": "2026-09-27",
        },
        "evidencias": [
            {
                "id": "EVID-008",
                "tipo": "boleta_honorarios_electronica",
                "nombre_archivo": "Comprobante_Urgencia_Trauma.pdf",
                "archivo_url": generar_svg_boleta("11890", "Elena Morales Bahamondes", "17.902.411-K", "Clínica RedSalud Valparaíso", "Urgencia Traumatológica Yeso", 75000),
                "hallazgos_espaciales": [],
            }
        ],
        "senales_analiticas": {
            "autenticidad_documental": {"valor": 75.0, "minimo_exigido": 70.0, "critica": True},
            "consistencia_datos": {"valor": 70.0, "minimo_exigido": None, "critica": False},
            "habilitacion_prestador": {"valor": 72.0, "minimo_exigido": 65.0, "critica": True},
            "consistencia_identidad": {"valor": 75.0, "minimo_exigido": 75.0, "critica": True},
            "alerta_fraude_activa": False,
            "detalle_alerta_fraude": None,
        },
        "sla": {
            "inicio_timestamp": (ahora - timedelta(hours=23, minutes=35)).isoformat(),
            "limite_timestamp": (ahora + timedelta(minutes=25)).isoformat(),  # SOLO 25 MINUTOS RESTANTES!
            "duracion_horas": 24,
            "horas_restantes": 0.4,
            "tiempo_restante_minutos": 25,
            "estado_sla": "rojo",
        },
        "estado_caso": "DERIVADO_A_REVISION_ASISTIDA",
        "resultado_f4": {
            "puntaje_calculado": 73.15,
            "desglose_componentes": {
                "autenticidad_documental": 26.25,
                "consistencia_datos": 17.5,
                "habilitacion_prestador": 14.4,
                "consistencia_identidad": 15.0,
            },
            "decision_algoritmica": "DERIVADO_A_REVISION_ASISTIDA",
            "causal_derivacion": "ZONA_GRIS",
            "detalle_causal": "Puntaje en zona gris (73.2). Vencimiento inminente de plazo legal de 24 horas (SLA Rojo < 1h).",
            "timestamp_evaluacion": (ahora - timedelta(hours=23, minutes=35)).isoformat(),
            "version_motor": "v1.0.0-f4",
        },
        "resolucion_humana_f1": None,
        "hash_auditoria_sha256": "8f66c8e19034af72e90c889a2b5e190348705c48b259586118d09ca084931b8",
        "fecha_creacion": (ahora - timedelta(hours=23, minutes=35)).isoformat(),
    }

    return [
        caso_001,
        caso_002,
        caso_003,
        caso_004,
        caso_005,
        caso_006,
        caso_007,
        caso_008,
    ]


def main():
    target_path = Path("backend/data/dataset.json")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    casos = generar_dataset_canonico()
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(casos, f, indent=2, ensure_ascii=False)
    print(f"✅ Inyección completada con éxito: {len(casos)} casos canónicos generados en '{target_path}'.")


if __name__ == "__main__":
    main()
