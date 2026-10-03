"""
Adaptador Dual Firestore / Fallback Local para la Plataforma MIRA.
Referencia Cruzada:
- HU E2: HU-DAT-02 (Adaptador Firestore para Sincronización Reactiva en Nube)
- HU E1: HU-57 (Confiabilidad y tolerancia ante fallos de persistencia)
- Requisitos: RNF-02 (0 casos perdidos ante fallos externos), AD-3, ROCE-01
"""

import logging
import os
from typing import List, Optional

from backend.app.domain.models import CasoExpediente, CausalDerivacion, EstadoCaso, ResolucionHumana
from backend.app.infrastructure.local_repository import LocalJsonRepository

logger = logging.getLogger("mira.firestore")


class FirestoreRepository:
    """
    Adaptador de persistencia con soporte nativo de Google Cloud Firestore
    y conmutación por falla (fallback) transparente hacia LocalJsonRepository.
    Garantiza 0 casos perdidos ante caídas de red o ausencia de credenciales cloud (RNF-02).
    """

    def __init__(self, local_fallback: Optional[LocalJsonRepository] = None):
        self.local_repo = local_fallback or LocalJsonRepository()
        self.storage_mode = os.getenv("STORAGE_MODE", "local").lower()
        self.client = None

        if self.storage_mode == "firestore":
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore

                if not firebase_admin._apps:
                    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                    if cred_path and os.path.exists(cred_path):
                        cred = credentials.Certificate(cred_path)
                        firebase_admin.initialize_app(cred)
                    else:
                        firebase_admin.initialize_app()
                self.client = firestore.client()
                logger.info("Conexión exitosa a Google Cloud Firestore.")
            except Exception as e:
                logger.warning(
                    f"No se pudo inicializar Firebase Firestore ({e}). "
                    f"Conmutando automáticamente a LocalJsonRepository (RNF-02 / Criterio C4)."
                )
                self.storage_mode = "local"

    def get_caso_by_id(self, caso_id: str, tenant_id: Optional[str] = None) -> Optional[CasoExpediente]:
        if self.storage_mode == "firestore" and self.client:
            try:
                doc = self.client.collection("casos_siniestros").document(caso_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    if tenant_id and data.get("tenant_id") != tenant_id:
                        return None
                    caso = CasoExpediente.model_validate(data)
                    return self.local_repo._actualizar_sla_dinamico(caso)
                return None
            except Exception as e:
                logger.error(f"Fallo al leer de Firestore ({e}). Recurriendo a fallback local.")

        return self.local_repo.get_caso_by_id(caso_id, tenant_id=tenant_id)

    def list_casos(
        self,
        tenant_id: str,
        estado: Optional[EstadoCaso] = None,
        causal: Optional[CausalDerivacion] = None,
        ordenar_por_sla: bool = True,
    ) -> List[CasoExpediente]:
        if self.storage_mode == "firestore" and self.client:
            try:
                query = self.client.collection("casos_siniestros").where("tenant_id", "==", tenant_id)
                if estado:
                    query = query.where("estado_caso", "==", estado.value)
                docs = query.stream()
                casos = []
                for doc in docs:
                    data = doc.to_dict()
                    caso = CasoExpediente.model_validate(data)
                    if causal and (not caso.resultado_f4 or caso.resultado_f4.causal_derivacion != causal):
                        continue
                    casos.append(self.local_repo._actualizar_sla_dinamico(caso))

                if ordenar_por_sla:
                    casos.sort(key=lambda c: c.sla.tiempo_restante_minutos if c.sla.tiempo_restante_minutos is not None else 999999)
                return casos
            except Exception as e:
                logger.error(f"Fallo al consultar Firestore ({e}). Recurriendo a fallback local.")

        return self.local_repo.list_casos(tenant_id, estado, causal, ordenar_por_sla)

    def save_caso(self, caso: CasoExpediente) -> None:
        # Siempre persistir en local para redundancia C4
        self.local_repo.save_caso(caso)

        if self.storage_mode == "firestore" and self.client:
            try:
                doc_ref = self.client.collection("casos_siniestros").document(caso.caso_id)
                doc_ref.set(caso.model_dump())
            except Exception as e:
                logger.error(f"Fallo al sincronizar con Firestore ({e}). Estado preservado en fallback local.")

    def update_resolucion(self, caso_id: str, resolucion: ResolucionHumana, tenant_id: str) -> Optional[CasoExpediente]:
        return self.local_repo.update_resolucion(caso_id, resolucion, tenant_id)
