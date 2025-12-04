"""
ARB-BOT — Configuración PRO
Sistema centralizado de variables, modelos, RAG y parámetros de IA
Optimizado para Railway + Supabase + Groq
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno automáticamente
load_dotenv()


# ===============================================================
# CONFIGURACIÓN BASE
# ===============================================================
class Config:
    """Configuración base de toda la aplicación."""

    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "arb-bot-dev-secret")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # ===============================================================
    # BASE DE DATOS LOCAL (solo interacciones)
    # ===============================================================
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///arbot.db")

    # ===============================================================
    # RAG + SUPABASE (OBLIGATORIO PARA VECTOR STORAGE)
    # ===============================================================
    SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")  # ejemplo: postgresql://...
    SUPABASE_DB_KEY = os.getenv("SUPABASE_DB_KEY", "")
    SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "arb_chunks")
    SUPABASE_CHUNK_LIMIT = int(os.getenv("SUPABASE_CHUNK_LIMIT", 100000))

    # ===============================================================
    # CONFIGURACIÓN DE IA (Groq por defecto)
    # ===============================================================
    API_PROVIDER = os.getenv("API_PROVIDER", "groq")  # groq | huggingface | gemini
    API_MODEL_NAME = os.getenv("API_MODEL_NAME", "")  # si está vacío, usa default del provider

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

    # Parámetros de generación (usados en generator.py)
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 512))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))

    # ===============================================================
    # PARÁMETROS DE PROCESAMIENTO Y LIMPIEZA
    # ===============================================================
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 8000))
    MIN_INPUT_LENGTH = int(os.getenv("MIN_INPUT_LENGTH", 3))

    # ===============================================================
    # RAG — PARÁMETROS DE CONSULTA
    # ===============================================================
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", 6))
    RAG_MAX_CONTEXT_LENGTH = int(os.getenv("RAG_MAX_CONTEXT_LENGTH", 3000))

    # ===============================================================
    # ARCHIVOS / UPLOADS
    # ===============================================================
    UPLOAD_FOLDER = "uploads"
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

    # ===============================================================
    # ADMIN
    # ===============================================================
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    # ===============================================================
    # LOGGING
    # ===============================================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "arbot.log"

    @staticmethod
    def init_app(app):
        pass


# ===============================================================
# ENTORNOS DISPONIBLES
# ===============================================================
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"


# Diccionario exportado
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

