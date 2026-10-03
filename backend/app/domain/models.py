"""
Modelos de Dominio y Esquemas Pydantic v2 para la Plataforma MIRA.
Incremento Funcional F4 (Motor de Decisión) y F1 (Bandeja de Revisión Asistida).
Cubre: HU-DAT-01, HU-F4-01..05, DEC-01..10, RNF-01..10.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class EstadoCaso(str, Enum):
    APROBADO_AUTOMATICO = "APROBADO_AUTOMATICO"
    DERIVADO_A_REVISION_ASISTIDA = "DERIVADO_A_REVISION_ASISTIDA"
    RESUELTO_POR_OPERADOR = "RESUELTO_POR_OPERADOR"


class CausalDerivacion(str, Enum):
    ALERTA_CRITICA_FRAUDE = "ALERTA_CRITICA_FRAUDE"
    MINIMO_SENAL_INSATISFECHO = "MINIMO_SENAL_INSATISFECHO"
    INFORMACION_INCOMPLETA = "INFORMACION_INCOMPLETA"
    BAJO_PUNTAJE = "BAJO_PUNTAJE"
    ZONA_GRIS = "ZONA_GRIS"


class AccionDictamen(str, Enum):
    APROBAR = "APROBAR"
    RECHAZAR = "RECHAZAR"
    SOLICITAR_ANTECEDENTES = "SOLICITAR_ANTECEDENTES"


class CoordenadasBoundingBox(BaseModel):
    top: float = Field(..., ge=0.0, le=100.0, description="Posición superior en %")
    left: float = Field(..., ge=0.0, le=100.0, description="Posición izquierda en %")
    width: float = Field(..., ge=0.0, le=100.0, description="Ancho en %")
    height: float = Field(..., ge=0.0, le=100.0, description="Alto en %")


class HallazgoEspacial(BaseModel):
    id: str = Field(..., description="Identificador único del hallazgo")
    tipo: str = Field(..., description="Tipo de anomalía detectada")
    descripcion: str = Field(..., description="Descripción comprensible del peritaje")
    severidad: str = Field(default="moderada", description="critica | moderada | leve")
    coordenadas: CoordenadasBoundingBox


class EvidenciaDocumental(BaseModel):
    id: str = Field(..., description="ID de evidencia")
    tipo: str = Field(..., description="Tipo de documento (boleta, receta, etc)")
    nombre_archivo: str = Field(..., description="Nombre del archivo adjunto")
    archivo_url: str = Field(..., description="URL o data URI del documento")
    hallazgos_espaciales: List[HallazgoEspacial] = Field(default_factory=list)


class DetalleSenal(BaseModel):
    valor: Optional[float] = Field(None, ge=0.0, le=100.0, description="Puntaje de la señal (0-100) o None si falló el módulo")
    minimo_exigido: Optional[float] = Field(None, ge=0.0, le=100.0, description="Umbral mínimo exigido (RF-11)")
    critica: bool = Field(default=False, description="Indica si la violación de mínimo genera corte")


class SenalesAnaliticas(BaseModel):
    autenticidad_documental: DetalleSenal
    consistencia_datos: DetalleSenal
    habilitacion_prestador: DetalleSenal
    consistencia_identidad: DetalleSenal
    alerta_fraude_activa: bool = Field(default=False, description="Prevalencia absoluta de corte por fraude (RF-12)")
    detalle_alerta_fraude: Optional[str] = Field(None, description="Motivo pericial de sospecha de fraude")


class Asegurado(BaseModel):
    rut: str = Field(..., description="RUT del asegurado")
    nombre: str = Field(..., description="Nombre completo")
    poliza_id: str = Field(..., description="Identificador de póliza")
    plan: str = Field(..., description="Nombre del plan de salud")


class Prestador(BaseModel):
    rut: str = Field(..., description="RUT institucional")
    nombre: str = Field(..., description="Razón social del prestador")
    registro_superintendencia: str = Field(..., description="N° de Registro en Superintendencia de Salud")


class Prestacion(BaseModel):
    tipo: str = Field(..., description="Descripción del acto médico")
    monto_reclamado: int = Field(..., ge=0, description="Monto en CLP")
    fecha_emision: str = Field(..., description="Fecha de emisión YYYY-MM-DD")


class EstadoSla(str, Enum):
    VERDE = "verde"
    AMARILLO = "amarillo"
    ROJO = "rojo"


class InformacionSla(BaseModel):
    inicio_timestamp: datetime = Field(..., description="Momento de ingreso del expediente")
    limite_timestamp: datetime = Field(..., description="Plazo máximo de resolución (24h hábiles DEC-05)")
    duracion_horas: int = Field(default=24, description="SLA normativo en horas")
    horas_restantes: Optional[float] = Field(None, description="Horas restantes dinámicas")
    tiempo_restante_minutos: Optional[int] = Field(None, description="Minutos restantes calculados")
    estado_sla: Optional[EstadoSla] = Field(None, description="verde (>4h), amarillo (1-4h), rojo (<1h)")


class ResultadoF4(BaseModel):
    puntaje_calculado: Optional[float] = Field(None, description="Puntaje ponderado 0-100 o None si incompleto")
    desglose_componentes: Dict[str, float] = Field(default_factory=dict, description="Aporte en puntos de cada señal")
    decision_algoritmica: EstadoCaso = Field(..., description="APROBADO_AUTOMATICO o DERIVADO_A_REVISION_ASISTIDA")
    causal_derivacion: Optional[CausalDerivacion] = Field(None, description="Causal tipificada si fue derivado")
    detalle_causal: Optional[str] = Field(None, description="Explicación humana y técnica de la causal")
    timestamp_evaluacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version_motor: str = Field(default="v1.0.0-f4", description="Versión auditable del motor F4 (RNF-04)")


class ResolucionHumana(BaseModel):
    decision_operador: AccionDictamen = Field(..., description="Voto soberano del revisor humano (DEC-07)")
    motivo_justificacion: str = Field(..., min_length=15, description="Fundamento técnico u operativo obligatorio (RF-19)")
    operador_id: str = Field(..., description="Identificador del usuario revisor")
    operador_nombre: str = Field(..., description="Nombre del revisor")
    discrepancia_detectada: bool = Field(default=False, description="Marca inmutable si contradice recomendación de F4 (RF-19)")
    timestamp_resolucion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CasoExpediente(BaseModel):
    caso_id: str = Field(..., description="Identificador canónico del caso (ej: CASO-2026-001)")
    tenant_id: str = Field(default="org_aseguradora_piloto", description="Aislamiento multitenant (RNF-05)")
    asegurado: Asegurado
    prestador: Prestador
    prestacion: Prestacion
    evidencias: List[EvidenciaDocumental] = Field(default_factory=list)
    senales_analiticas: SenalesAnaliticas
    sla: InformacionSla
    estado_caso: EstadoCaso = Field(default=EstadoCaso.DERIVADO_A_REVISION_ASISTIDA)
    resultado_f4: Optional[ResultadoF4] = None
    resolucion_humana_f1: Optional[ResolucionHumana] = None
    hash_auditoria_sha256: Optional[str] = Field(None, description="Sello criptográfico de auditoría (RNF-04 / DEC-10)")
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SolicitudEvaluacionCaso(BaseModel):
    caso_id: str
    tenant_id: str = "org_aseguradora_piloto"
    asegurado: Asegurado
    prestador: Prestador
    prestacion: Prestacion
    senales_analiticas: SenalesAnaliticas
    evidencias: List[EvidenciaDocumental] = Field(default_factory=list)


class SolicitudDictamen(BaseModel):
    decision: AccionDictamen
    motivo_justificacion: str = Field(..., min_length=15, description="Justificación obligatoria de al menos 15 caracteres")
    operador_id: str = Field(default="operador_marco")
    operador_nombre: str = Field(default="Marco Peñailillo")
