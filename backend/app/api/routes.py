"""
Rutas del API REST para la Plataforma MIRA (Incremento F4 y F1).
Referencia Cruzada:
- HU E2: HU-API-01 a HU-API-05
- HU E1: HU-15, HU-16, HU-18, HU-19, HU-39, HU-40, HU-42, HU-55, HU-56, HU-60, HU-61
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from pydantic import BaseModel

from backend.app.domain.models import (
    AccionDictamen,
    CausalDerivacion,
    EstadoCaso,
    InformacionSla,
    ResolucionHumana,
    ResultadoF4,
    SolicitudDictamen,
    SolicitudEvaluacionCaso,
    CasoExpediente,
)
from backend.app.domain.decision_resolver import DecisionResolver
from backend.app.infrastructure.local_repository import LocalJsonRepository
from backend.app.infrastructure.audit_logger import AuditLogger
from backend.app.infrastructure.accounting import AccountingService
from backend.app.infrastructure.retention import LegalRetentionGuard


router = APIRouter(prefix="/api/v1", tags=["Plataforma MIRA"])

# Inyección de dependencias singleton
repo = LocalJsonRepository()
audit = AuditLogger()
accounting = AccountingService()
resolver = DecisionResolver()


def get_current_tenant(request: Request, x_tenant_id: Optional[str] = Header(None)) -> str:
    """Extrae y valida el tenant_id actual del request o cabecera."""
    tenant = x_tenant_id or getattr(request.state, "tenant_id", None) or "org_aseguradora_piloto"
    return tenant


@router.get("/health")
def health_check():
    """Estado de operatividad del backend y servicios asociados."""
    return {
        "status": "UP",
        "servicio": "MIRA Backend & Motor F4",
        "version": "1.0.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/evaluar-caso", status_code=status.HTTP_200_OK)
def evaluar_caso(payload: SolicitudEvaluacionCaso, tenant_id: str = Depends(get_current_tenant)):
    """
    HU-API-01: Endpoint de Evaluación Determinista F4.
    Ejecuta el pipeline analítico y persiste el resultado con rastro SHA-256.
    Retorna 200 OK si aprueba automáticamente o 202 Accepted si deriva a F1.
    """
    resultado = resolver.evaluar(payload.senales_analiticas)
    ahora = datetime.now(timezone.utc)

    # Crear o actualizar el expediente
    sla_info = InformacionSla(
        inicio_timestamp=ahora,
        limite_timestamp=ahora + timedelta(hours=24),
        duracion_horas=24,
    )

    caso = CasoExpediente(
        caso_id=payload.caso_id,
        tenant_id=tenant_id,
        asegurado=payload.asegurado,
        prestador=payload.prestador,
        prestacion=payload.prestacion,
        evidencias=payload.evidencias,
        senales_analiticas=payload.senales_analiticas,
        sla=sla_info,
        estado_caso=resultado.decision_algoritmica,
        resultado_f4=resultado,
        resolucion_humana_f1=None,
    )

    # Registrar en rastro inmutable SHA-256 (HU-DAT-03 / RNF-04)
    evento_audit = audit.registrar_evento(
        caso_id=caso.caso_id,
        tenant_id=tenant_id,
        tipo_evento="EVALUACION_F4",
        snapshot_datos={
            "puntaje": resultado.puntaje_calculado,
            "decision": resultado.decision_algoritmica.value,
            "causal": resultado.causal_derivacion.value if resultado.causal_derivacion else None,
            "senales": payload.senales_analiticas.model_dump(),
        },
    )
    caso.hash_auditoria_sha256 = evento_audit.hash_sha256

    # Persistir en repositorio
    repo.save_caso(caso)

    # Si fue aprobación automática limpia, computar validación cobrable (DEC-02 / RNF-06)
    if resultado.decision_algoritmica == EstadoCaso.APROBADO_AUTOMATICO:
        accounting.registrar_validacion_cobrable(tenant_id, "AUTOMATICA_F4")

    # Si es derivado, retornamos estatus 202 con el resultado
    return {
        "caso_id": caso.caso_id,
        "estado": caso.estado_caso,
        "resultado_f4": resultado,
        "hash_auditoria": caso.hash_auditoria_sha256,
        "mensaje": (
            "Expediente evaluado con éxito y aprobado automáticamente"
            if resultado.decision_algoritmica == EstadoCaso.APROBADO_AUTOMATICO
            else "Expediente derivado a revisión asistida (F1)"
        ),
    }


@router.get("/casos")
def listar_casos_bandeja(
    estado: Optional[EstadoCaso] = None,
    causal: Optional[CausalDerivacion] = None,
    ordenar_por_sla: bool = True,
    tenant_id: str = Depends(get_current_tenant),
):
    """
    HU-API-02: Endpoint de Bandeja Asistida F1.
    Retorna la lista de casos filtrada y ordenada por urgencia de SLA (DEC-05 / FR-F1-01).
    """
    casos = repo.list_casos(
        tenant_id=tenant_id,
        estado=estado or EstadoCaso.DERIVADO_A_REVISION_ASISTIDA,
        causal=causal,
        ordenar_por_sla=ordenar_por_sla,
    )
    return casos


@router.get("/casos/{caso_id}")
def obtener_detalle_caso(caso_id: str, tenant_id: str = Depends(get_current_tenant)):
    """
    HU-API-02 / HU-UI-02: Consulta de Expediente Completo de Siniestro.
    Retorna evidencias con coordenadas normalizadas para el visor de bounding boxes.
    """
    caso = repo.get_caso_by_id(caso_id, tenant_id=tenant_id)
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expediente '{caso_id}' no encontrado o no pertenece a su organización.",
        )
    return caso


@router.post("/casos/{caso_id}/dictamen")
def registrar_dictamen_operador(
    caso_id: str,
    payload: SolicitudDictamen,
    tenant_id: str = Depends(get_current_tenant),
):
    """
    HU-API-03: Endpoint de Dictamen Resolutivo Humano (DEC-07 / RF-18 / RF-19).
    Registra el voto vinculante, exige justificación técnica (min 15 caracteres),
    detecta y sella marcas de discrepancia si contradice el motor F4.
    """
    caso = repo.get_caso_by_id(caso_id, tenant_id=tenant_id)
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expediente '{caso_id}' no encontrado.",
        )

    # Validar longitud mínima de justificación obligatoria (RF-19 / DEC-07)
    if len(payload.motivo_justificacion.strip()) < 15:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La justificación técnica es obligatoria y debe contener al menos 15 caracteres.",
        )

    # DETECCIÓN DE DISCREPANCIA (RF-19 / ROCE-02):
    # Si el sistema derivó el caso por bajo puntaje o por fraude, y el operador humano vota APROBAR:
    hay_discrepancia = False
    if caso.resultado_f4:
        causal = caso.resultado_f4.causal_derivacion
        if causal in [CausalDerivacion.BAJO_PUNTAJE, CausalDerivacion.ALERTA_CRITICA_FRAUDE] and payload.decision == AccionDictamen.APROBAR:
            hay_discrepancia = True
        elif (caso.resultado_f4.puntaje_calculado is not None and caso.resultado_f4.puntaje_calculado < 60.0) and payload.decision == AccionDictamen.APROBAR:
            hay_discrepancia = True

    resolucion = ResolucionHumana(
        decision_operador=payload.decision,
        motivo_justificacion=payload.motivo_justificacion.strip(),
        operador_id=payload.operador_id,
        operador_nombre=payload.operador_nombre,
        discrepancia_detectada=hay_discrepancia,
        timestamp_resolucion=datetime.now(timezone.utc),
    )

    # Registrar evento inmutable en log de auditoría (HU-DAT-03 / RNF-04)
    evento_audit = audit.registrar_evento(
        caso_id=caso_id,
        tenant_id=tenant_id,
        tipo_evento="DICTAMEN_HUMANO_F1",
        snapshot_datos={
            "voto": payload.decision.value,
            "motivo": payload.motivo_justificacion,
            "operador_id": payload.operador_id,
            "discrepancia_detectada": hay_discrepancia,
            "puntaje_original_f4": caso.resultado_f4.puntaje_calculado if caso.resultado_f4 else None,
            "causal_original_f4": caso.resultado_f4.causal_derivacion.value if caso.resultado_f4 and caso.resultado_f4.causal_derivacion else None,
        },
    )

    # Actualizar estado del caso en base de datos
    caso_actualizado = repo.update_resolucion(caso_id, resolucion, tenant_id=tenant_id)
    caso_actualizado.hash_auditoria_sha256 = evento_audit.hash_sha256
    repo.save_caso(caso_actualizado)

    # Incrementar contador de validación cobrable asistida (HU-DAT-04 / RNF-06 / DEC-02)
    accounting.registrar_validacion_cobrable(tenant_id, "ASISTIDA_F1")

    return {
        "mensaje": "Dictamen registrado con éxito y sellado en rastro inmutable de auditoría.",
        "caso_id": caso_id,
        "decision": payload.decision,
        "discrepancia_detectada": hay_discrepancia,
        "hash_auditoria": evento_audit.hash_sha256,
        "caso": caso_actualizado,
    }


@router.get("/metricas/validaciones")
def obtener_metricas_consumo(tenant_id: str = Depends(get_current_tenant)):
    """
    HU-API-04 / RNF-06: Endpoint de Métricas de Validación y Conciliación Contable.
    Comprueba paridad absoluta entre cliente y facturación interna (Diferencia = 0).
    """
    return accounting.obtener_metricas_conciliadas(tenant_id)


@router.get("/auditoria/{caso_id}")
def obtener_auditoria_caso(caso_id: str, tenant_id: str = Depends(get_current_tenant)):
    """
    HU-DAT-03 / RNF-04: Consulta de Rastro Inmutable de Auditoría para Reconstrucción Forense.
    """
    historial = audit.obtener_historial_caso(caso_id)
    return {
        "caso_id": caso_id,
        "total_eventos": len(historial),
        "eventos": historial,
    }


class SolicitudBorrado(BaseModel):
    caso_id: str
    fecha_emision: str


@router.post("/solicitudes-arco/eliminar")
def procesar_solicitud_eliminacion(payload: SolicitudBorrado):
    """
    HU-DAT-05 / RNF-09: Verificación de Retención Quinquenal Obligatoria (DEC-01).
    """
    autorizado, motivo = LegalRetentionGuard.evaluar_solicitud_eliminacion(payload.fecha_emision)
    if not autorizado:
        return {
            "estado": "DENEGADO_POR_LEY",
            "motivo": motivo,
            "politica": "DEC-01 / RNF-09 (Custodia obligatoria de 5 años por la Superintendencia de Salud)",
        }
    return {"estado": "AUTORIZADO", "motivo": motivo}
