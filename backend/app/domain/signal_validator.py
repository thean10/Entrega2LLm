"""
Verificación de Umbrales Mínimos por Señal Individual para el Motor F4 (MIRA).
Referencia Cruzada:
- HU E2: HU-F4-02 (Verificación Estricta de Umbrales Mínimos por Señal)
- HU E1: HU-11 (Verificación de umbrales mínimos por señal individual)
- Requisito E1: RF-11 / Cierra Hallazgo H-12 (Riesgo de promedios ponderados engañosos)
"""

from typing import Dict, List, Optional, Tuple
from backend.app.domain.models import SenalesAnaliticas


# Umbrales mínimos normativos por defecto (RF-11 / H-12)
DEFAULT_MINIMOS = {
    "autenticidad_documental": 70.0,
    "habilitacion_prestador": 65.0,
    "consistencia_identidad": 75.0,
}


class SignalThresholdValidator:
    """
    Validador de reglas de corte duro por señal crítica individual.
    Impide que un puntaje global alto encubra una falla grave en autenticidad o habilitación.
    """

    def __init__(self, minimos: Dict[str, float] = None):
        self.minimos = minimos or DEFAULT_MINIMOS.copy()

    def validar_minimos(self, senales: SenalesAnaliticas) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verifica que todas las señales críticas superen sus mínimos requeridos.

        Returns:
            Tuple con (es_valido, senal_infractora, detalle_motivo)
        """
        mapa_senales = {
            "autenticidad_documental": senales.autenticidad_documental,
            "consistencia_datos": senales.consistencia_datos,
            "habilitacion_prestador": senales.habilitacion_prestador,
            "consistencia_identidad": senales.consistencia_identidad,
        }

        for clave, min_val in self.minimos.items():
            detalle = mapa_senales.get(clave)
            if detalle and detalle.valor is not None:
                # Comprobar mínimo exigido ya sea del objeto o del parámetro por defecto
                cota_minima = detalle.minimo_exigido if detalle.minimo_exigido is not None else min_val
                if detalle.valor < cota_minima:
                    motivo = (
                        f"La señal crítica '{clave}' tiene un valor de {detalle.valor:.1f}, "
                        f"inferior al umbral mínimo exigido de {cota_minima:.1f} (RF-11 / H-12)."
                    )
                    return False, clave, motivo

        return True, None, None
