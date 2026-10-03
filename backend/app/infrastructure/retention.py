"""
Gestor de Custodia de Evidencias y Retención Quinquenal para MIRA.
Referencia Cruzada:
- HU E2: HU-DAT-05 (Custodia de Evidencias y Retención Quinquenal Inalterable)
- HU E1: HU-45 (Conservación y retención de evidencias), HU-64 (Cumplimiento normativo)
- Requisitos: RNF-09 (Retención obligatoria 5 años), DEC-01 (Superintendencia de Salud)
"""

from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional


DIAS_RETENCION_OBLIGATORIA = 1825  # 5 años (DEC-01)


class LegalRetentionGuard:
    """
    Guardián normativo de retención de antecedentes probatorios de siniestros.
    Bloquea el borrado físico de expedientes en período de litigio o fiscalización.
    """

    @staticmethod
    def evaluar_solicitud_eliminacion(fecha_emision_prestacion: str) -> Tuple[bool, str]:
        """
        Evalúa si procede la eliminación de datos conforme al marco legal chileno.

        Args:
            fecha_emision_prestacion: Fecha en formato ISO YYYY-MM-DD.

        Returns:
            Tuple con (eliminacion_permitida: bool, motivo_resolucion: str)
        """
        try:
            fecha_doc = datetime.strptime(fecha_emision_prestacion, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            fecha_doc = datetime.now(timezone.utc)

        antiguedad = datetime.now(timezone.utc) - fecha_doc

        if antiguedad < timedelta(days=DIAS_RETENCION_OBLIGATORIA):
            dias_restantes = DIAS_RETENCION_OBLIGATORIA - antiguedad.days
            motivo = (
                f"SOLICITUD_DENEGADA: El expediente tiene una antigüedad de {antiguedad.days} días, "
                f"inferior al plazo legal de 5 años ({DIAS_RETENCION_OBLIGATORIA} días) exigido por la "
                f"Superintendencia de Salud y el mandato DEC-01 para litigios y peritajes de cobertura. "
                f"Quedan {dias_restantes} días de custodia inalterable obligatoria (RNF-09)."
            )
            return False, motivo

        return True, "SOLICITUD_AUTORIZADA: Plazo de retención quinquenal cumplido."
