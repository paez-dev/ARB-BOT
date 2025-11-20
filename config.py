"""
ARB-BOT - Configuración del Sistema
Archivo centralizado de configuración usando herramientas gratuitas
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración de Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Configuración de Base de Datos (SQLite - Gratuita)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///arbot.db')
    
    # API Keys (Opcionales - el sistema funciona sin ellas)
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Configuración de Modelo (solo API - Groq por defecto)
    API_PROVIDER = os.getenv('API_PROVIDER', 'groq')  # groq, huggingface, gemini
    API_MODEL_NAME = os.getenv('API_MODEL_NAME', '')  # Opcional, usa defaults
    
    # Configuración de Modelos de IA (solo API)
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '200'))  # Aumentado para APIs
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Configuración de Procesamiento
    MAX_INPUT_LENGTH = 500
    MIN_INPUT_LENGTH = 3
    AUTO_WARMUP_ENABLED = os.getenv('AUTO_WARMUP_ENABLED', 'false').lower() == 'true'
    
    # Proveedores de API disponibles (solo APIs, no modelos locales)
    AVAILABLE_API_PROVIDERS = {
        'groq': {
            'name': 'Groq',
            'description': 'Gratis, MUY rápido, modelos Llama 3.1 (RECOMENDADO)',
            'free': True,
            'default_model': 'llama-3.1-8b-instant',
            'models': ['llama-3.1-8b-instant', 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768'],
            'recommended': True
        },
        'huggingface': {
            'name': 'Hugging Face',
            'description': 'Gratis, muchos modelos disponibles',
            'free': True,
            'default_model': 'microsoft/DialoGPT-medium',
            'models': ['microsoft/DialoGPT-medium', 'meta-llama/Llama-3.1-8B-Instruct'],
            'recommended': False
        },
        'gemini': {
            'name': 'Google Gemini',
            'description': 'Gratis, buena calidad, límites generosos',
            'free': True,
            'default_model': 'gemini-pro',
            'models': ['gemini-pro', 'gemini-pro-vision'],
            'recommended': False
        }
    }
    
    # Configuración de Archivos
    UPLOAD_FOLDER = 'uploads'
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Configuración de Autenticación Admin
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')  # Cambiar en producción
    
    # Configuración de Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'arbot.log'
    
    @staticmethod
    def init_app(app):
        """Inicializar configuración en la aplicación Flask"""
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    # En producción, asegurarse de tener SECRET_KEY seguro

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'  # Base de datos en memoria para tests

# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

