"""
main.py
-------
Punto de entrada de la aplicación. Instancia FastAPI, configura CORS
(necesario para que la app Flutter/React Native en dispositivo/emulador
pueda llamar a la API), y monta el router versionado.

Ejecutar en desarrollo:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Documentación interactiva autogenerada:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Motor de resolución simbólica paso a paso para álgebra, "
                "cálculo univariable y cálculo vectorial (gradiente, "
                "divergencia, rotacional, integrales múltiples).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
