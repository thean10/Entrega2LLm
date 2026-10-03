"""
Suite de Pruebas de Integración para Endpoints FastAPI (Plataforma MIRA).
Verifica: HU-API-01, HU-API-02, HU-API-03, HU-API-04, HU-API-05.
Casos de Prueba Vinculantes de E1: CP-API-01, CP-API-02, CP-07, CP-08, CP-RNF-05-01, CP-RNF-06-01.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.domain.models import AccionDictamen, EstadoCaso


@pytest.fixture
def client():
    # TestClient de starlette/fastapi
    return TestClient(app, raise_server_exceptions=True)


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"


def test_hu_api_02_listar_casos_ordenados_por_sla(client):
    """
    CP-API-02 / CP-08:
    Comprueba que GET /api/v1/casos retorna los casos derivados ordenados por criticidad de SLA.
    """
    headers = {"X-Tenant-ID": "org_aseguradora_piloto"}
    response = client.get("/api/v1/casos", headers=headers)
    assert response.status_code == 200
    casos = response.json()
    assert len(casos) >= 5, "Deben existir casos en la bandeja F1"

    # Verificar que el primer caso es el más urgente (tiempo restante menor)
    tiempos = [c["sla"]["tiempo_restante_minutos"] for c in casos if c["sla"]["tiempo_restante_minutos"] is not None]
    assert tiempos == sorted(tiempos), "Los casos deben venir ordenados cronológicamente por SLA ascendente"

    # Verificar presencia de caso crítico
    casos_ids = [c["caso_id"] for c in casos]
    assert "CASO-2026-008" in casos_ids or "CASO-2026-005" in casos_ids


def test_hu_api_02_detalle_caso_con_bounding_boxes(client):
    """
    Verifica que GET /api/v1/casos/{id} entrega las evidencias con coordenadas normalizadas.
    """
    headers = {"X-Tenant-ID": "org_aseguradora_piloto"}
    response = client.get("/api/v1/casos/CASO-2026-005", headers=headers)
    assert response.status_code == 200
    caso = response.json()
    assert caso["caso_id"] == "CASO-2026-005"
    assert caso["senales_analiticas"]["alerta_fraude_activa"] is True
    assert len(caso["evidencias"]) > 0
    evid = caso["evidencias"][0]
    assert len(evid["hallazgos_espaciales"]) > 0
    coords = evid["hallazgos_espaciales"][0]["coordenadas"]
    assert "top" in coords and "left" in coords and "width" in coords and "height" in coords


def test_hu_api_03_dictamen_con_discrepancia_y_justificacion(client):
    """
    CP-RF-19-01 / CP-07:
    Dictamen sobre caso de bajo puntaje CASO-2026-007.
    Si el operador aprueba, el sistema detecta discrepancia=True,
    exige justificación >=15 caracteres y sella el registro SHA-256.
    """
    headers = {"X-Tenant-ID": "org_aseguradora_piloto"}

    # 1. Intento con justificación demasiado corta (<15 caracteres) -> HTTP 422
    payload_corto = {
        "decision": AccionDictamen.APROBAR.value,
        "motivo_justificacion": "Aprobado ok",  # Solo 11 caracteres
        "operador_id": "operador_marco",
        "operador_nombre": "Marco Peñailillo",
    }
    res_invalida = client.post("/api/v1/casos/CASO-2026-007/dictamen", json=payload_corto, headers=headers)
    assert res_invalida.status_code == 422

    # 2. Dictamen con justificación válida
    payload_valido = {
        "decision": AccionDictamen.APROBAR.value,
        "motivo_justificacion": "Se autoriza cobertura excepcional por tratarse de una urgencia oftalmológica impostergable.",
        "operador_id": "operador_marco",
        "operador_nombre": "Marco Peñailillo",
    }
    res_valida = client.post("/api/v1/casos/CASO-2026-007/dictamen", json=payload_valido, headers=headers)
    assert res_valida.status_code == 200
    data = res_valida.json()
    assert data["discrepancia_detectada"] is True, "Debe activarse la marca de discrepancia (RF-19)"
    assert data["hash_auditoria"] is not None
    assert len(data["hash_auditoria"]) == 64  # Longitud SHA-256


def test_hu_api_04_metricas_conciliacion_contable(client):
    """
    CP-RNF-06-01 / CP-API-04:
    Consulta de métricas con comprobación de Diferencia = 0 entre cliente y finanzas.
    """
    headers = {"X-Tenant-ID": "org_aseguradora_piloto"}
    response = client.get("/api/v1/metricas/validaciones", headers=headers)
    assert response.status_code == 200
    metricas = response.json()
    assert "total_validaciones_cobrables" in metricas
    assert "diferencia_auditoria" in metricas
    assert metricas["diferencia_auditoria"] == 0, "La discrepancia contable cliente vs facturación debe ser 0 (RNF-06)"


def test_hu_api_05_aislamiento_multitenant_403(client):
    """
    CP-RNF-05-01 / CP-API-05:
    Intento de consulta cruzada a expediente de otra organización o sin cabecera X-Tenant-ID.
    """
    # 1. Sin cabecera X-Tenant-ID en llamada API
    res_sin_tenant = client.get("/api/v1/casos")
    assert res_sin_tenant.status_code == 403
    assert "X-Tenant-ID" in res_sin_tenant.json()["error"]

    # 2. Con tenant ajeno intentando acceder a caso de la aseguradora piloto
    headers_ajeno = {"X-Tenant-ID": "org_aseguradora_competencia_02"}
    res_ajena = client.get("/api/v1/casos/CASO-2026-001", headers=headers_ajeno)
    assert res_ajena.status_code == 404, "No debe permitir ver casos pertenecientes a otro tenant (RNF-05)"
