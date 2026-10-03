"""
Punto de Entrada Principal de la Aplicación ASGI FastAPI (Plataforma MIRA).
Incremento Funcional F4 (Motor de Decisión) y F1 (Bandeja de Revisión Asistida).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router as api_router
from backend.app.api.middleware import LeakyBucketMiddleware, MultitenantSecurityMiddleware


app = FastAPI(
    title="MIRA — Plataforma de Inteligencia Multimodal para Decisiones Empresariales",
    description=(
        "Backend de Servicios y Motor de Decisión F4 + BFF para la Bandeja F1. "
        "Desarrollado bajo el Método BMAD para la Entrega 2."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Configuración de CORS para permitir SPA Vite y pruebas locales
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Retry-After", "X-Tenant-ID"],
)

# 2. Middleware de Rate Limiting Leaky Bucket (RNF-01 / DEC-06)
app.add_middleware(LeakyBucketMiddleware, capacidad=100, tasa=1.67)

# 3. Middleware de Aislamiento Multitenant (RNF-05 / DEC-08)
app.add_middleware(MultitenantSecurityMiddleware, tenant_default="org_aseguradora_piloto")

# 4. Registrar Router de API
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "plataforma": "MIRA — Inteligencia Multimodal",
        "incremento": "F4 (Motor Analítico) + F1 (Bandeja Asistida)",
        "estado": "Operacional",
        "documentacion": "/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
