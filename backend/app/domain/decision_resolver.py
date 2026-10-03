"""
Motor de Decisión Determinista por Umbrales F4 (MIRA).
Referencia Cruzada:
- HU E2: HU-F4-04 (Tratamiento de Información Incompleta y Fallo de Módulos)
- HU E2: HU-F4-05 (Clasificación Final con Prohibición de Rechazo Automático)
- HU E1: HU-13 (Derivación por fallo de módulo analítico)
- HU E1: HU-14 (Prohibición de rechazo automático y derivación por bajo puntaje)
- Requisitos E1: RF-13, RF-14, DEC-04 (90/60), DEC-07 (Soberanía humana), FR-F4-01, FR-F4-02
"""

from typing import Dict, Optional
from datetime import datetime, timezone

from backend.app.domain.models import (
    CausalDerivacion,
    EstadoCaso,
    ResultadoF4,
    SenalesAnaliticas,
)
from backend.app.domain.score_calculator import ScoreCalculator
from backend.app.domain.signal_validator import SignalThresholdValidator
from backend.app.domain.fraud_checker import FraudChecker


class DecisionResolver:
    """
    Orquestador de evaluación algorítmica determinista F4.
    Ejecuta el pipeline de reglas absolutas, cálculo ponderado y clasificación
    asegurando la imposibilidad matemática y lógica de rechazos automáticos (DEC-07).
    """

    def __init__(
        self,
        umbral_aprobacion: float = 90.0,
        umbral_zona_gris: float = 60.0,
        score_calculator: Optional[ScoreCalculator] = None,
        signal_validator: Optional[SignalThresholdValidator] = None,
    ):
        self.umbral_aprobacion = umbral_aprobacion
        self.umbral_zona_gris = umbral_zona_gris
        self.calculator = score_calculator or ScoreCalculator()
        self.validator = signal_validator or SignalThresholdValidator()

    def evaluar(self, senales: SenalesAnaliticas) -> ResultadoF4:
        """
        Aplica los 5 pasos deterministas de evaluación:
        1. Comprobar información incompleta o fallo de módulo (RF-13).
        2. Comprobar alerta de fraude activa con precedencia absoluta (RF-12).
        3. Comprobar umbrales mínimos por señal individual (RF-11 / H-12).
        4. Calcular puntaje ponderado de confianza (RF-02 / DEC-04).
        5. Clasificar según umbrales con prohibición de rechazo automático (RF-14 / DEC-07).
        """
        timestamp_now = datetime.now(timezone.utc)

        # PASO 1: Tratamiento de Información Incompleta y Fallo de Módulos (RF-13 / HU-F4-04)
        mapa_valores: Dict[str, Optional[float]] = {
            "autenticidad_documental": senales.autenticidad_documental.valor,
            "consistencia_datos": senales.consistencia_datos.valor,
            "habilitacion_prestador": senales.habilitacion_prestador.valor,
            "consistencia_identidad": senales.consistencia_identidad.valor,
        }

        modulos_faltantes = [k for k, v in mapa_valores.items() if v is None]
        if modulos_faltantes:
            return ResultadoF4(
                puntaje_calculado=None,
                desglose_componentes={},
                decision_algoritmica=EstadoCaso.DERIVADO_A_REVISION_ASISTIDA,
                causal_derivacion=CausalDerivacion.INFORMACION_INCOMPLETA,
                detalle_causal=(
                    f"Fallo de disponibilidad analítica o información incompleta en módulo(s): "
                    f"{', '.join(modulos_faltantes)}. Derivado a revisión asistida sin imputar valores ficticios (RF-13)."
                ),
                timestamp_evaluacion=timestamp_now,
            )

        # PASO 2: Precedencia Absoluta de Corte por Sospecha de Fraude (RF-12 / HU-F4-03)
        hay_fraude, detalle_fraude = FraudChecker.verificar_fraude(senales)
        if hay_fraude:
            # Aunque haya fraude, podemos calcular referencialmente el puntaje para transparencia
            valores_puros = {k: float(v) for k, v in mapa_valores.items() if v is not None}
            puntaje, desglose = self.calculator.calcular_puntaje(valores_puros)
            return ResultadoF4(
                puntaje_calculado=puntaje,
                desglose_componentes=desglose,
                decision_algoritmica=EstadoCaso.DERIVADO_A_REVISION_ASISTIDA,
                causal_derivacion=CausalDerivacion.ALERTA_CRITICA_FRAUDE,
                detalle_causal=(
                    f"Alerta de fraude activa: {detalle_fraude}. Precedencia de corte absoluto sobre "
                    f"cualquier puntaje (RF-12 / H-03)."
                ),
                timestamp_evaluacion=timestamp_now,
            )

        # PASO 3: Verificación Estricta de Umbrales Mínimos por Señal (RF-11 / HU-F4-02 / H-12)
        minimos_ok, senal_infractora, detalle_minimo = self.validator.validar_minimos(senales)
        if not minimos_ok:
            valores_puros = {k: float(v) for k, v in mapa_valores.items() if v is not None}
            puntaje, desglose = self.calculator.calcular_puntaje(valores_puros)
            return ResultadoF4(
                puntaje_calculado=puntaje,
                desglose_componentes=desglose,
                decision_algoritmica=EstadoCaso.DERIVADO_A_REVISION_ASISTIDA,
                causal_derivacion=CausalDerivacion.MINIMO_SENAL_INSATISFECHO,
                detalle_causal=detalle_minimo,
                timestamp_evaluacion=timestamp_now,
            )

        # PASO 4: Cálculo Ponderado de Confianza (HU-F4-01 / RF-02)
        valores_puros = {k: float(v) for k, v in mapa_valores.items() if v is not None}
        puntaje_global, desglose = self.calculator.calcular_puntaje(valores_puros)

        # PASO 5: Clasificación Final con Prohibición de Rechazo Automático (HU-F4-05 / RF-14 / DEC-07)
        if puntaje_global >= self.umbral_aprobacion:
            return ResultadoF4(
                puntaje_calculado=puntaje_global,
                desglose_componentes=desglose,
                decision_algoritmica=EstadoCaso.APROBADO_AUTOMATICO,
                causal_derivacion=None,
                detalle_causal=f"Expediente con alta confianza ({puntaje_global} >= {self.umbral_aprobacion}). Aprobación directa autorizada.",
                timestamp_evaluacion=timestamp_now,
            )
        elif puntaje_global >= self.umbral_zona_gris:
            return ResultadoF4(
                puntaje_calculado=puntaje_global,
                desglose_componentes=desglose,
                decision_algoritmica=EstadoCaso.DERIVADO_A_REVISION_ASISTIDA,
                causal_derivacion=CausalDerivacion.ZONA_GRIS,
                detalle_causal=(
                    f"Puntaje de confianza en zona gris ({puntaje_global:.1f} entre {self.umbral_zona_gris} y {self.umbral_aprobacion}). "
                    f"Requiere inspección asistida humana."
                ),
                timestamp_evaluacion=timestamp_now,
            )
        else:
            # INVARIANTE DEC-07: Jamás retornar RECHAZADO directamente.
            return ResultadoF4(
                puntaje_calculado=puntaje_global,
                desglose_componentes=desglose,
                decision_algoritmica=EstadoCaso.DERIVADO_A_REVISION_ASISTIDA,
                causal_derivacion=CausalDerivacion.BAJO_PUNTAJE,
                detalle_causal=(
                    f"Puntaje crítico ({puntaje_global:.1f} < {self.umbral_zona_gris}). Conforme al mandato DEC-07 y RF-14, "
                    f"el sistema tiene prohibición de emitir rechazos automáticos. Requiere dictamen humano soberano."
                ),
                timestamp_evaluacion=timestamp_now,
            )
