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
    
    # Configuración de Modelos de IA
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'distilgpt2')  # Modelo gratuito de Hugging Face
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '150'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Configuración de Procesamiento
    MAX_INPUT_LENGTH = 500
    MIN_INPUT_LENGTH = 3
    AUTO_WARMUP_ENABLED = os.getenv('AUTO_WARMUP_ENABLED', 'false').lower() == 'true'
    
    # Modelos disponibles (todos gratuitos)
    AVAILABLE_MODELS = {
        'distilgpt2': {
            'name': 'DistilGPT-2',
            'provider': 'huggingface',
            'description': 'Modelo ligero y rápido (básico, respuestas limitadas)',
            'free': True,
            'size': '~250MB',
            'recommended': False
        },
        'gpt2': {
            'name': 'GPT-2',
            'provider': 'huggingface',
            'description': 'Modelo original GPT-2 - Mejor calidad que DistilGPT-2',
            'free': True,
            'size': '~500MB',
            'recommended': True
        },
        'microsoft/DialoGPT-small': {
            'name': 'DialoGPT Small',
            'provider': 'huggingface',
            'description': 'Entrenado para conversaciones - Mejor para preguntas/respuestas',
            'free': True,
            'size': '~250MB',
            'recommended': True
        },
        'microsoft/DialoGPT-medium': {
            'name': 'DialoGPT Medium',
            'provider': 'huggingface',
            'description': 'DialoGPT más grande - Mejor calidad de respuestas',
            'free': True,
            'size': '~500MB',
            'recommended': True
        },
        'facebook/blenderbot-small-90M': {
            'name': 'BlenderBot Small',
            'provider': 'huggingface',
            'description': 'Entrenado para chatbots - Respuestas más coherentes',
            'free': True,
            'size': '~350MB',
            'recommended': True
        },
        'PlanTL-GOB-ES/gpt2-base-bne': {
            'name': 'GPT-2 Español (BNE)',
            'provider': 'huggingface',
            'description': 'GPT-2 entrenado en español - Mejor para español',
            'free': True,
            'size': '~500MB',
            'recommended': True,
            'spanish': True
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

