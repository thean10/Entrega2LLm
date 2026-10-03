"""
Cálculo Ponderado de Confianza Multimodal para el Motor F4 (MIRA).
Referencia Cruzada:
- HU E2: HU-F4-01 (Inicialización del Motor y Cálculo Ponderado de Confianza)
- HU E1: HU-02 (Cálculo automático de puntaje de confianza multimodal)
- Requisito E1: RF-02 / DEC-04 (Umbrales paramétricos) / FR-F4-01
"""

from typing import Dict, Tuple


# Pesos paramétricos por defecto según arquitectura (DEC-04 / RF-02)
# Suma de pesos = 1.0 (35% + 25% + 20% + 20%)
DEFAULT_PESOS = {
    "autenticidad_documental": 0.35,
    "consistencia_datos": 0.25,
    "habilitacion_prestador": 0.20,
    "consistencia_identidad": 0.20,
}


class ScoreCalculator:
    """
    Calculadora determinista de puntaje ponderado de confianza multimodal.
    Garantiza precisión de punto flotante, invariante de rango [0.0, 100.0]
    y desglose transparente por componente.
    """

    def __init__(self, pesos: Dict[str, float] = None):
        self.pesos = pesos or DEFAULT_PESOS.copy()
        total_pesos = sum(self.pesos.values())
        if abs(total_pesos - 1.0) > 1e-6:
            raise ValueError(f"La suma de ponderaciones debe ser exactamente 1.0 (actual: {total_pesos})")

    def calcular_puntaje(self, senales_valores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Calcula la combinación lineal S = sum(w_i * s_i).

        Args:
            senales_valores: Diccionario con el valor de cada señal en escala [0.0, 100.0].

        Returns:
            Tuple con (puntaje_global_redondeado, desglose_de_puntos)

        Raises:
            ValueError: Si alguna señal es menor a 0 o mayor a 100, o si falta alguna señal requerida.
        """
        desglose = {}
        puntaje_acumulado = 0.0

        for clave, peso in self.pesos.items():
            if clave not in senales_valores:
                raise ValueError(f"Falta señal requerida en el vector de evaluación: '{clave}'")

            val = senales_valores[clave]
            if val is None:
                raise ValueError(f"El valor de la señal '{clave}' no puede ser nulo en el cálculo matemático")

            if not (0.0 <= val <= 100.0):
                raise ValueError(f"Invariante de rango violado en señal '{clave}': {val} no está en [0.0, 100.0]")

            puntos_componente = round(peso * val, 3)
            desglose[clave] = round(puntos_componente, 2)
            puntaje_acumulado += peso * val

        # Invariante de acotamiento estricto
        puntaje_final = max(0.0, min(100.0, puntaje_acumulado))
        puntaje_redondeado = round(puntaje_final, 1)

        return puntaje_redondeado, desglose
