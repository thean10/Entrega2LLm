"""
Adaptador de Persistencia Local JSON para la Plataforma MIRA.
Referencia Cruzada:
- HU E2: HU-DAT-01 (Modelado Pydantic y Adaptador de Persistencia Local JSON)
- HU E1: HU-58 (Arranque ágil y onboarding de operación)
- Requisitos: RNF-03 (Puesta en marcha <5s), Criterio C4, AD-3
"""

import json
import os
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path

from backend.app.domain.models import (
    CasoExpediente,
    CausalDerivacion,
    EstadoCaso,
    EstadoSla,
    ResolucionHumana,
)


class LocalJsonRepository:
    """
    Repositorio JSON local seguro y atómico.
    Permite operar en modo 100% desconectado en menos de 5 segundos.
    """

    def __init__(self, file_path: str = "backend/data/dataset.json"):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self._ensure_storage()

    def _ensure_storage(self):
        """Crea el directorio y archivo si no existen."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _actualizar_sla_dinamico(self, caso: CasoExpediente) -> CasoExpediente:
        """Calcula el tiempo restante dinámico del SLA y fija el estado cromático."""
        ahora = datetime.now(timezone.utc)
        limite = caso.sla.limite_timestamp
        if limite.tzinfo is None:
            limite = limite.replace(tzinfo=timezone.utc)

        delta = limite - ahora
        minutos_restantes = int(delta.total_seconds() / 60)
        horas_restantes = round(delta.total_seconds() / 3600.0, 1)

        caso.sla.tiempo_restante_minutos = minutos_restantes
        caso.sla.horas_restantes = horas_restantes

        if minutos_restantes <= 60:
            caso.sla.estado_sla = EstadoSla.ROJO
        elif minutos_restantes <= 240:
            caso.sla.estado_sla = EstadoSla.AMARILLO
        else:
            caso.sla.estado_sla = EstadoSla.VERDE

        return caso

    def get_caso_by_id(self, caso_id: str, tenant_id: Optional[str] = None) -> Optional[CasoExpediente]:
        """Obtiene un expediente por ID, validando tenant si se provee (RNF-05)."""
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                casos_raw = json.load(f)

            for raw in casos_raw:
                if raw.get("caso_id") == caso_id:
                    if tenant_id and raw.get("tenant_id") != tenant_id:
                        return None  # Bloqueado por política multitenant
                    caso = CasoExpediente.model_validate(raw)
                    return self._actualizar_sla_dinamico(caso)
            return None

    def list_casos(
        self,
        tenant_id: str,
        estado: Optional[EstadoCaso] = None,
        causal: Optional[CausalDerivacion] = None,
        ordenar_por_sla: bool = True,
    ) -> List[CasoExpediente]:
        """Lista expedientes filtrados por tenant, estado y causal."""
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                casos_raw = json.load(f)

        resultado = []
        for raw in casos_raw:
            # Aislamiento multitenant estricto (RNF-05)
            if raw.get("tenant_id") != tenant_id:
                continue

            caso = CasoExpediente.model_validate(raw)
            if estado and caso.estado_caso != estado:
                continue

            if causal:
                if not caso.resultado_f4 or caso.resultado_f4.causal_derivacion != causal:
                    continue

            caso_actualizado = self._actualizar_sla_dinamico(caso)
            resultado.append(caso_actualizado)

        if ordenar_por_sla:
            # Ordenar ascendente por tiempo restante (los más urgentes primero)
            resultado.sort(key=lambda c: c.sla.tiempo_restante_minutos if c.sla.tiempo_restante_minutos is not None else 999999)

        return resultado

    def save_caso(self, caso: CasoExpediente) -> None:
        """Guarda o actualiza un caso atómicamente."""
        with self._lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                casos_raw = json.load(f)

            # Reemplazar o insertar
            updated = False
            for i, raw in enumerate(casos_raw):
                if raw.get("caso_id") == caso.caso_id:
                    casos_raw[i] = json.loads(caso.model_dump_json())
                    updated = True
                    break

            if not updated:
                casos_raw.append(json.loads(caso.model_dump_json()))

            # Escritura atómica a archivo temporal y rename
            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(casos_raw, f, indent=2, ensure_ascii=False)

            temp_path.replace(self.file_path)

    def update_resolucion(self, caso_id: str, resolucion: ResolucionHumana, tenant_id: str) -> Optional[CasoExpediente]:
        """Actualiza un caso con la resolución soberana del revisor humano (DEC-07 / RF-19)."""
        caso = self.get_caso_by_id(caso_id, tenant_id=tenant_id)
        if not caso:
            return None

        caso.resolucion_humana_f1 = resolucion
        caso.estado_caso = EstadoCaso.RESUELTO_POR_OPERADOR
        self.save_caso(caso)
        return caso
