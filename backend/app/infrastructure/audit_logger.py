"""
Rastro Inmutable de Auditoría Criptográfica con SHA-256 para MIRA.
Referencia Cruzada:
- HU E2: HU-DAT-03 (Registro Inmutable de Auditoría con Hash SHA-256 y Reconstrucción)
- HU E1: HU-30 (Registro inmutable de decisiones), HU-59 (Reconstrucción forense)
- Requisitos: RNF-04 (0 discrepancias decisionales), DEC-10, H-14, FR-F1-05
"""

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class EntradaAuditoria(BaseModel):
    evento_id: str
    caso_id: str
    tenant_id: str
    tipo_evento: str  # "EVALUACION_F4" | "DICTAMEN_HUMANO_F1" | "APROBACION_AUTOMATICA"
    timestamp_utc: str
    snapshot_datos: Dict[str, Any]
    hash_sha256: str
    hash_previo: Optional[str] = None


class AuditLogger:
    """
    Gestor de auditoría inmutable append-only con encadenamiento criptográfico.
    Garantiza reconstrucción forense exacta y detección instantánea de manipulación.
    """

    def __init__(self, file_path: str = "backend/data/audit_log.json"):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self._ensure_storage()

    def _ensure_storage(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    @staticmethod
    def calcular_hash_evento(payload_canonico: Dict[str, Any], hash_previo: Optional[str] = None) -> str:
        """Calcula el hash SHA-256 determinista sobre el JSON ordenado canónicamente."""
        contenido = {
            "datos": payload_canonico,
            "hash_previo": hash_previo or "GENESIS",
        }
        cadena = json.dumps(contenido, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(cadena.encode("utf-8")).hexdigest()

    def registrar_evento(
        self,
        caso_id: str,
        tenant_id: str,
        tipo_evento: str,
        snapshot_datos: Dict[str, Any],
    ) -> EntradaAuditoria:
        """Registra un evento append-only sellado criptográficamente."""
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                logs_raw = json.load(f)

            hash_anterior = logs_raw[-1]["hash_sha256"] if logs_raw else "GENESIS"
            timestamp_str = datetime.now(timezone.utc).isoformat()
            payload_canonico = {
                "caso_id": caso_id,
                "tenant_id": tenant_id,
                "tipo_evento": tipo_evento,
                "timestamp_utc": timestamp_str,
                "snapshot": snapshot_datos,
            }

            nuevo_hash = self.calcular_hash_evento(payload_canonico, hash_anterior)
            evento_id = f"AUD-{len(logs_raw) + 1:06d}"

            entrada = EntradaAuditoria(
                evento_id=evento_id,
                caso_id=caso_id,
                tenant_id=tenant_id,
                tipo_evento=tipo_evento,
                timestamp_utc=timestamp_str,
                snapshot_datos=snapshot_datos,
                hash_sha256=nuevo_hash,
                hash_previo=hash_anterior,
            )

            logs_raw.append(entrada.model_dump())

            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(logs_raw, f, indent=2, ensure_ascii=False)
            temp_path.replace(self.file_path)

            return entrada

    def obtener_historial_caso(self, caso_id: str) -> List[EntradaAuditoria]:
        """Recupera la cadena de eventos de un caso específico."""
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                logs_raw = json.load(f)

        return [EntradaAuditoria.model_validate(e) for e in logs_raw if e.get("caso_id") == caso_id]

    def verificar_integridad_cadena(self) -> Tuple[bool, int, Optional[str]]:
        """
        Verifica la inalterabilidad de toda la cadena de auditoría (RNF-04).
        Retorna (es_valida, total_eventos, mensaje_error).
        """
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                logs_raw = json.load(f)

        hash_esperado_previo = "GENESIS"
        for i, item in enumerate(logs_raw):
            payload_canonico = {
                "caso_id": item["caso_id"],
                "tenant_id": item["tenant_id"],
                "tipo_evento": item["tipo_evento"],
                "timestamp_utc": item["timestamp_utc"],
                "snapshot": item["snapshot_datos"],
            }
            hash_recalculado = self.calcular_hash_evento(payload_canonico, hash_esperado_previo)
            if hash_recalculado != item["hash_sha256"]:
                return False, i, f"Discrepancia detectada en evento {item.get('evento_id')}: hash corrompido"
            hash_esperado_previo = item["hash_sha256"]

        return True, len(logs_raw), None
