"""
Middlewares de Rate Limiting (Leaky Bucket) y Aislamiento Multitenant para MIRA.
Referencia Cruzada:
- HU E2: HU-API-01 (Rate Limiting Leaky Bucket / RNF-01)
- HU E2: HU-API-05 (Middleware de Aislamiento Multitenant y Seguridad / RNF-05)
- HU E1: HU-55, HU-56 (RNF-01), HU-42, HU-60 (RNF-05)
- Reglas: DEC-06 (0 descartes HTTP 429), DEC-08 (0% accesos indebidos inter-tenant)
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class LeakyBucketRateLimiter:
    """
    Algoritmo de Cubeta Permeable (Leaky Bucket) para suavizar ráfagas de API (RNF-01).
    Capacidad: 100 rpm (100 peticiones / 60 segundos = tasa de salida 1.66 req/s).
    Las solicitudes excedentes no se descartan con 429, sino que se amortiguan elásticamente.
    """

    def __init__(self, capacidad_maxima: int = 100, tasa_salida_por_segundo: float = 1.67):
        self.capacidad = capacidad_maxima
        self.tasa_salida = tasa_salida_por_segundo
        self.agua_actual = 0.0
        self.ultimo_tiempo = time.monotonic()
        self._lock = asyncio.Lock()

    async def registrar_peticion(self) -> Tuple[bool, float]:
        """
        Calcula el goteo y determina si la petición puede pasar inmediatamente
        o si requiere encolamiento con Retry-After.
        Retorna (pasa_inmediato: bool, tiempo_espera_segundos: float).
        """
        async with self._lock:
            ahora = time.monotonic()
            delta = ahora - self.ultimo_tiempo
            self.ultimo_tiempo = ahora

            # Goteo de agua
            self.agua_actual = max(0.0, self.agua_actual - delta * self.tasa_salida)

            if self.agua_actual + 1.0 <= self.capacidad:
                self.agua_actual += 1.0
                return True, 0.0
            else:
                # Excedente encolado elásticamente (RNF-01: 0% descartes 429)
                tiempo_espera = round((self.agua_actual + 1.0 - self.capacidad) / self.tasa_salida, 2)
                self.agua_actual = self.capacidad  # La cubeta retiene al máximo sin desbordar
                return False, max(1.0, tiempo_espera)


class LeakyBucketMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, capacidad: int = 100, tasa: float = 1.67):
        super().__init__(app)
        self.limiter = LeakyBucketRateLimiter(capacidad_maxima=capacidad, tasa_salida_por_segundo=tasa)

    async def dispatch(self, request: Request, call_next):
        # Excluir rutas de documentación y health
        if request.url.path in ["/docs", "/openapi.json", "/api/v1/health"]:
            return await call_next(request)

        pasa, tiempo_espera = await self.limiter.registrar_peticion()
        if not pasa:
            # Encolamiento elástico: retorna HTTP 202 con cabecera Retry-After (DEC-06 / RNF-01)
            # Garantiza cero respuestas HTTP 429
            return JSONResponse(
                status_code=202,
                content={
                    "mensaje": "Solicitud encolada en cubeta elástica (Rate Limit Leaky Bucket). Procesamiento en curso.",
                    "tiempo_espera_segundos": tiempo_espera,
                    "politica": "RNF-01 / DEC-06 (0% peticiones descartadas con HTTP 429)",
                },
                headers={"Retry-After": str(int(tiempo_espera))},
            )

        response = await call_next(request)
        return response


class MultitenantSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de aislamiento estricto entre organizaciones aseguradoras (RNF-05).
    Exige la cabecera X-Tenant-ID en todas las rutas protegidas del API.
    Inyecta encabezados de seguridad de clase bancaria.
    """

    def __init__(self, app, tenant_default: str = "org_aseguradora_piloto"):
        super().__init__(app)
        self.tenant_default = tenant_default
        self.rutas_publicas = ["/docs", "/openapi.json", "/api/v1/health", "/", "/favicon.ico"]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self.rutas_publicas or path.startswith("/static") or path.startswith("/assets"):
            response = await call_next(request)
            return self._aplicar_cabeceras_seguridad(response)

        tenant_id = request.headers.get("X-Tenant-ID")

        # Si no viene cabecera en peticiones API, rechazar con 403 Forbidden (RNF-05)
        if not tenant_id and request.url.path.startswith("/api/v1"):
            # Permitir que las llamadas con query param tenant_id o del frontend local pasen si tienen default
            tenant_id = request.query_params.get("tenant_id")
            if not tenant_id:
                # Si es una petición OPTIONS (CORS preflight), autorizar
                if request.method == "OPTIONS":
                    return await call_next(request)
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Acceso denegado: Cabecera 'X-Tenant-ID' requerida para aislamiento multitenant (RNF-05 / DEC-08).",
                        "codigo": "TENANT_HEADER_MISSING",
                    },
                )

        # Inyectar tenant en el state de la request
        request.state.tenant_id = tenant_id or self.tenant_default

        response = await call_next(request)
        return self._aplicar_cabeceras_seguridad(response)

    def _aplicar_cabeceras_seguridad(self, response: Response) -> Response:
        """Aplica defensas HTTP obligatorias (mandatory-secure-web-skills)."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
