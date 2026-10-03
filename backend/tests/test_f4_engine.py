"""
Suite de Pruebas Unitarias para el Motor Analítico F4 (Plataforma MIRA).
Verifica: HU-F4-01, HU-F4-02, HU-F4-03, HU-F4-04, HU-F4-05.
Casos de Prueba Vinculantes de E1: CP-01, CP-02, CP-03, CP-05, CP-06, CP-RF-11-01, CP-RF-12-01, CP-RF-13-01, CP-RF-14-01.
"""

import time
import pytest
from backend.app.domain.models import (
    CausalDerivacion,
    DetalleSenal,
    EstadoCaso,
    SenalesAnaliticas,
)
from backend.app.domain.score_calculator import ScoreCalculator
from backend.app.domain.signal_validator import SignalThresholdValidator
from backend.app.domain.fraud_checker import FraudChecker
from backend.app.domain.decision_resolver import DecisionResolver


def test_hu_f4_01_calculo_ponderado_nominal():
    """
    CP-F4-01 / CP-01:
    Dado un caso con señales: autenticidad=96, consistencia=94, prestador=98, identidad=95
    y pesos [0.35, 0.25, 0.20, 0.20]
    El puntaje es 0.35*96 + 0.25*94 + 0.20*98 + 0.20*95 = 33.6 + 23.5 + 19.6 + 19.0 = 95.7 -> redondeado a 95.7
    """
    calc = ScoreCalculator()
    senales = {
        "autenticidad_documental": 96.0,
        "consistencia_datos": 94.0,
        "habilitacion_prestador": 98.0,
        "consistencia_identidad": 95.0,
    }
    puntaje, desglose = calc.calcular_puntaje(senales)
    esperado = round(0.35 * 96.0 + 0.25 * 94.0 + 0.20 * 98.0 + 0.20 * 95.0, 1)
    assert puntaje == esperado
    assert 0.0 <= puntaje <= 100.0
    assert "autenticidad_documental" in desglose
    assert desglose["autenticidad_documental"] == round(0.35 * 96.0, 2)


def test_hu_f4_01_invariante_rango_excepcion():
    """
    Verifica que señales fuera de [0, 100] arrojen ValueError.
    """
    calc = ScoreCalculator()
    with pytest.raises(ValueError, match="Invariante de rango violado"):
        calc.calcular_puntaje({
            "autenticidad_documental": 105.0,
            "consistencia_datos": 90.0,
            "habilitacion_prestador": 90.0,
            "consistencia_identidad": 90.0,
        })

    with pytest.raises(ValueError, match="Invariante de rango violado"):
        calc.calcular_puntaje({
            "autenticidad_documental": -5.0,
            "consistencia_datos": 90.0,
            "habilitacion_prestador": 90.0,
            "consistencia_identidad": 90.0,
        })


def test_hu_f4_01_rendimiento_sub_10ms():
    """
    Verifica que el tiempo de cómputo en memoria sea menor a 10ms (NFR-F4-01 < 200ms).
    """
    calc = ScoreCalculator()
    senales = {
        "autenticidad_documental": 85.0,
        "consistencia_datos": 80.0,
        "habilitacion_prestador": 75.0,
        "consistencia_identidad": 80.0,
    }
    t0 = time.perf_counter()
    for _ in range(100):
        calc.calcular_puntaje(senales)
    dt = (time.perf_counter() - t0) / 100.0
    assert dt < 0.010, f"Tiempo de cálculo por expediente ({dt*1000:.3f} ms) excedió los 10 ms"


def test_hu_f4_02_minimo_individual_insatisfecho():
    """
    CP-RF-11-01 / CP-02:
    Caso con puntaje agregado alto (>90) pero autenticidad=55 (mínimo=70).
    Debe derivar a REVISION ASISTIDA con causal MINIMO_SENAL_INSATISFECHO.
    """
    resolver = DecisionResolver()
    senales = SenalesAnaliticas(
        autenticidad_documental=DetalleSenal(valor=55.0, minimo_exigido=70.0, critica=True),
        consistencia_datos=DetalleSenal(valor=98.0, minimo_exigido=None, critica=False),
        habilitacion_prestador=DetalleSenal(valor=99.0, minimo_exigido=65.0, critica=True),
        consistencia_identidad=DetalleSenal(valor=95.0, minimo_exigido=75.0, critica=True),
        alerta_fraude_activa=False,
    )
    resultado = resolver.evaluar(senales)
    assert resultado.decision_algoritmica == EstadoCaso.DERIVADO_A_REVISION_ASISTIDA
    assert resultado.causal_derivacion == CausalDerivacion.MINIMO_SENAL_INSATISFECHO
    assert "autenticidad_documental" in resultado.detalle_causal


def test_hu_f4_03_precedencia_fraude_absoluta():
    """
    CP-RF-12-01 / CP-05:
    Caso con puntaje de 98.0 y todos los mínimos satisfechos, pero alerta_fraude_activa=True.
    Debe derivar inmediatamente a ALERTA_CRITICA_FRAUDE y jamás autorizar APROBADO_AUTOMATICO.
    """
    resolver = DecisionResolver()
    senales = SenalesAnaliticas(
        autenticidad_documental=DetalleSenal(valor=98.0, minimo_exigido=70.0, critica=True),
        consistencia_datos=DetalleSenal(valor=99.0, minimo_exigido=None, critica=False),
        habilitacion_prestador=DetalleSenal(valor=100.0, minimo_exigido=65.0, critica=True),
        consistencia_identidad=DetalleSenal(valor=97.0, minimo_exigido=75.0, critica=True),
        alerta_fraude_activa=True,
        detalle_alerta_fraude="Alteración en folio fiscal detectada en base compartida",
    )
    resultado = resolver.evaluar(senales)
    assert resultado.decision_algoritmica == EstadoCaso.DERIVADO_A_REVISION_ASISTIDA
    assert resultado.causal_derivacion == CausalDerivacion.ALERTA_CRITICA_FRAUDE
    assert "fraude" in resultado.detalle_causal.lower()


def test_hu_f4_04_modulo_incompleto_tolerancia():
    """
    CP-RF-13-01 / CP-06:
    Señal faltante (None) por fallo o timeout de módulo.
    Debe derivar a INFORMACION_INCOMPLETA sin inventar valores ficticios.
    """
    resolver = DecisionResolver()
    senales = SenalesAnaliticas(
        autenticidad_documental=DetalleSenal(valor=90.0, minimo_exigido=70.0, critica=True),
        consistencia_datos=DetalleSenal(valor=None, minimo_exigido=None, critica=False),  # Módulo caído
        habilitacion_prestador=DetalleSenal(valor=90.0, minimo_exigido=65.0, critica=True),
        consistencia_identidad=DetalleSenal(valor=90.0, minimo_exigido=75.0, critica=True),
        alerta_fraude_activa=False,
    )
    resultado = resolver.evaluar(senales)
    assert resultado.decision_algoritmica == EstadoCaso.DERIVADO_A_REVISION_ASISTIDA
    assert resultado.causal_derivacion == CausalDerivacion.INFORMACION_INCOMPLETA
    assert resultado.puntaje_calculado is None
    assert "consistencia_datos" in resultado.detalle_causal


def test_hu_f4_05_prohibicion_rechazo_automatico_bajo_puntaje():
    """
    CP-RF-14-01 / CP-03:
    Caso legítimo pero con puntaje muy bajo (35.0 < 60.0).
    Conforme a DEC-07 y RF-14, el sistema NO PUEDE emitir RECHAZADO.
    Debe derivar a DERIVADO_A_REVISION_ASISTIDA bajo causal BAJO_PUNTAJE.
    """
    resolver = DecisionResolver()
    senales = SenalesAnaliticas(
        autenticidad_documental=DetalleSenal(valor=40.0, minimo_exigido=0.0, critica=False),
        consistencia_datos=DetalleSenal(valor=30.0, minimo_exigido=0.0, critica=False),
        habilitacion_prestador=DetalleSenal(valor=35.0, minimo_exigido=0.0, critica=False),
        consistencia_identidad=DetalleSenal(valor=35.0, minimo_exigido=0.0, critica=False),
        alerta_fraude_activa=False,
    )
    resultado = resolver.evaluar(senales)
    assert resultado.decision_algoritmica == EstadoCaso.DERIVADO_A_REVISION_ASISTIDA
    assert resultado.decision_algoritmica != "RECHAZADO"
    assert resultado.causal_derivacion == CausalDerivacion.BAJO_PUNTAJE
    assert resultado.puntaje_calculado is not None
    assert resultado.puntaje_calculado < 60.0


def test_hu_f4_05_aprobacion_limpia():
    """
    CP-01:
    Caso sin alertas, con mínimos superados y puntaje >= 90.0.
    Debe ser APROBADO_AUTOMATICO.
    """
    resolver = DecisionResolver()
    senales = SenalesAnaliticas(
        autenticidad_documental=DetalleSenal(valor=95.0, minimo_exigido=70.0, critica=True),
        consistencia_datos=DetalleSenal(valor=92.0, minimo_exigido=None, critica=False),
        habilitacion_prestador=DetalleSenal(valor=96.0, minimo_exigido=65.0, critica=True),
        consistencia_identidad=DetalleSenal(valor=94.0, minimo_exigido=75.0, critica=True),
        alerta_fraude_activa=False,
    )
    resultado = resolver.evaluar(senales)
    assert resultado.decision_algoritmica == EstadoCaso.APROBADO_AUTOMATICO
    assert resultado.puntaje_calculado >= 90.0
    assert resultado.causal_derivacion is None
