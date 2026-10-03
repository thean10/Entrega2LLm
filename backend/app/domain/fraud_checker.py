"""
Comprobación de Precedencia Absoluta por Alerta de Fraude para el Motor F4 (MIRA).
Referencia Cruzada:
- HU E2: HU-F4-03 (Precedencia Absoluta de Corte por Sospecha de Fraude)
- HU E1: HU-12 (Precedencia de corte por señal de fraude)
- Requisito E1: RF-12 / Hallazgo H-03 / CP-RF-12-01
"""

from typing import Optional, Tuple
from backend.app.domain.models import SenalesAnaliticas


class FraudChecker:
    """
    Verificador de cortocircuito lógico por sospecha de fraude.
    Garantiza que cualquier indicio de alteración, adulteración o suplantación
    corte de raíz el flujo de aprobación automática con prioridad urgente.
    """

    @staticmethod
    def verificar_fraude(senales: SenalesAnaliticas) -> Tuple[bool, Optional[str]]:
        """
        Evalúa si existe una alerta de fraude activa en las señales analíticas.

        Returns:
            Tuple con (alerta_activa: bool, detalle_motivo: Optional[str])
        """
        if senales.alerta_fraude_activa:
            motivo = senales.detalle_alerta_fraude or "Alerta crítica de fraude activa detectada en expediente (RF-12)."
            return True, motivo

        return False, None
