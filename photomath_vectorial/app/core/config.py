"""
config.py
---------
Configuración centralizada. Usa pydantic-settings para leer variables
de entorno (y un archivo .env en desarrollo local). Nunca hardcodear
API keys en el código fuente.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Photomath Vectorial API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # OCR / Visión
    MATHPIX_APP_ID: str = ""
    MATHPIX_APP_KEY: str = ""
    VISION_LLM_API_KEY: str = ""  # OpenAI (GPT-4o) o Google (Gemini), según adaptador usado

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]  # En producción: restringir al dominio de la app

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
