"""
Contador Atómico de Validaciones Cobrables y Conciliación para MIRA.
Referencia Cruzada:
- HU E2: HU-DAT-04 (Contador Atómico de Validaciones Cobrables)
- HU E2: HU-API-04 (Endpoint de Métricas de Validación y Conciliación)
- HU E1: HU-40 (Registro de eventos de validación cobrable), HU-61 (Consistencia de conteo)
- Requisitos: RNF-06 (Diferencia = 0 cliente vs facturación), DEC-02
"""

import json
import threading
from pathlib import Path
from typing import Dict, Any


class AccountingService:
    """
    Servicio de registro atómico de consumo y conciliación contable.
    Garantiza paridad absoluta entre la vista del cliente y el registro de cobranza.
    """

    def __init__(self, file_path: str = "backend/data/accounting.json"):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self._ensure_storage()

    def _ensure_storage(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            datos_iniciales = {
                "contadores_tenant": {},
                "registro_facturacion_interno": {},
            }
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(datos_iniciales, f, indent=2)

    def registrar_validacion_cobrable(self, tenant_id: str, tipo_cierre: str) -> Dict[str, Any]:
        """
        Incrementa atómicamente el contador del tenant y el de facturación en la misma transacción (DEC-02).
        tipo_cierre: 'AUTOMATICA_F4' | 'ASISTIDA_F1'
        """
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if tenant_id not in data["contadores_tenant"]:
                data["contadores_tenant"][tenant_id] = {
                    "total_validaciones_cobrables": 0,
                    "automaticas_f4": 0,
                    "asistidas_f1": 0,
                }

            if tenant_id not in data["registro_facturacion_interno"]:
                data["registro_facturacion_interno"][tenant_id] = {
                    "total_cobros_registrados": 0,
                }

            # Incrementos en el mismo ciclo atómico
            data["contadores_tenant"][tenant_id]["total_validaciones_cobrables"] += 1
            if tipo_cierre == "AUTOMATICA_F4":
                data["contadores_tenant"][tenant_id]["automaticas_f4"] += 1
            else:
                data["contadores_tenant"][tenant_id]["asistidas_f1"] += 1

            data["registro_facturacion_interno"][tenant_id]["total_cobros_registrados"] += 1

            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.file_path)

            return data["contadores_tenant"][tenant_id]

    def obtener_metricas_conciliadas(self, tenant_id: str) -> Dict[str, Any]:
        """
        Retorna las métricas y calcula la diferencia de conciliación (debe ser estrictamente 0).
        """
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        tenant_data = data["contadores_tenant"].get(
            tenant_id,
            {"total_validaciones_cobrables": 0, "automaticas_f4": 0, "asistidas_f1": 0},
        )
        fact_data = data["registro_facturacion_interno"].get(
            tenant_id,
            {"total_cobros_registrados": 0},
        )

        diferencia = tenant_data["total_validaciones_cobrables"] - fact_data["total_cobros_registrados"]

        return {
            "tenant_id": tenant_id,
            "total_validaciones_cobrables": tenant_data["total_validaciones_cobrables"],
            "automaticas_f4": tenant_data["automaticas_f4"],
            "asistidas_f1": tenant_data["asistidas_f1"],
            "total_facturacion_interna": fact_data["total_cobros_registrados"],
            "diferencia_auditoria": diferencia,  # RNF-06: Diferencia == 0
        }
