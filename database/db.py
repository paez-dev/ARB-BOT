"""
ARB-BOT - Configuración de Base de Datos
Utiliza SQLite (gratuito y embebido)
"""

import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

_db_connection = None
_db_path = None

def init_db(database_url: str):
    """
    Inicializar base de datos
    
    Args:
        database_url: URL de la base de datos (formato SQLAlchemy)
    """
    global _db_path
    
    try:
        # Extraer path de SQLite de la URL
        if database_url.startswith('sqlite:///'):
            _db_path = database_url.replace('sqlite:///', '')
        else:
            _db_path = 'arbot.db'
        
        logger.info(f"Inicializando base de datos en: {_db_path}")
        
        # Crear tablas si no existen
        with get_db_session() as conn:
            cursor = conn.cursor()
            
            # Tabla de interacciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT NOT NULL,
                    generated_output TEXT,
                    model_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processing_time REAL,
                    metadata TEXT
                )
            ''')
            
            # Tabla de estadísticas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Base de datos inicializada correctamente")
            
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {str(e)}")
        raise

@contextmanager
def get_db_session():
    """
    Context manager para sesiones de base de datos
    
    Yields:
        Conexión a la base de datos
    """
    global _db_path
    
    if _db_path is None:
        _db_path = 'arbot.db'
    
    conn = None
    try:
        conn = sqlite3.connect(_db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error en sesión de BD: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def save_interaction(user_input: str, generated_output: str, 
                    model_used: str, processing_time: float = None,
                    metadata: dict = None):
    """
    Guardar una interacción en la base de datos
    
    Args:
        user_input: Input del usuario
        generated_output: Output generado
        model_used: Modelo utilizado
        processing_time: Tiempo de procesamiento (opcional)
        metadata: Metadata adicional (opcional)
    """
    try:
        import json
        
        metadata_str = json.dumps(metadata) if metadata else None
        
        with get_db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions 
                (user_input, generated_output, model_used, processing_time, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_input, generated_output, model_used, processing_time, metadata_str))
            
            logger.info("Interacción guardada en BD")
            
    except Exception as e:
        logger.warning(f"No se pudo guardar interacción: {str(e)}")

def get_recent_interactions(limit: int = 10):
    """
    Obtener interacciones recientes
    
    Args:
        limit: Número máximo de interacciones a retornar
    
    Returns:
        Lista de interacciones
    """
    try:
        with get_db_session() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM interactions 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    except Exception as e:
        logger.error(f"Error obteniendo interacciones: {str(e)}")
        return []

