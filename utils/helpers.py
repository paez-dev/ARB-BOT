"""
ARB-BOT - Funciones Auxiliares
Utilidades generales para el sistema
"""

import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def validate_input(text: str, min_length: int = 3, max_length: int = 500):
    """
    Validar input del usuario
    
    Args:
        text: Texto a validar
        min_length: Longitud mínima
        max_length: Longitud máxima
    
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not text or not isinstance(text, str):
        return False, "Input inválido: debe ser texto"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"Input muy corto. Mínimo {min_length} caracteres"
    
    if len(text) > max_length:
        return False, f"Input muy largo. Máximo {max_length} caracteres"
    
    # Validar caracteres peligrosos (básico)
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onload='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Input contiene caracteres no permitidos"
    
    return True, None

def format_response(data: Dict[str, Any], status: str = 'success') -> Dict[str, Any]:
    """
    Formatear respuesta estándar
    
    Args:
        data: Datos a incluir en la respuesta
        status: Estado de la respuesta
    
    Returns:
        Respuesta formateada
    """
    return {
        'status': status,
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }

def calculate_metrics(input_text: str, output_text: str, 
                     processing_time: float = None) -> Dict[str, Any]:
    """
    Calcular métricas de una interacción
    
    Args:
        input_text: Texto de entrada
        output_text: Texto de salida
        processing_time: Tiempo de procesamiento (opcional)
    
    Returns:
        Diccionario con métricas
    """
    metrics = {
        'input_length': len(input_text),
        'output_length': len(output_text),
        'input_word_count': len(input_text.split()),
        'output_word_count': len(output_text.split()),
        'expansion_ratio': len(output_text) / len(input_text) if input_text else 0
    }
    
    if processing_time:
        metrics['processing_time'] = processing_time
        metrics['chars_per_second'] = len(output_text) / processing_time if processing_time > 0 else 0
    
    return metrics

def sanitize_text(text: str) -> str:
    """
    Sanitizar texto para prevenir inyecciones
    
    Args:
        text: Texto a sanitizar
    
    Returns:
        Texto sanitizado
    """
    # Remover caracteres de control
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limitar longitud
    text = text[:1000]
    
    return text.strip()

def format_error(error: Exception, include_traceback: bool = False) -> Dict[str, Any]:
    """
    Formatear error para respuesta
    
    Args:
        error: Excepción capturada
        include_traceback: Incluir traceback (solo en desarrollo)
    
    Returns:
        Diccionario con información del error
    """
    error_info = {
        'error': str(error),
        'type': type(error).__name__,
        'timestamp': datetime.now().isoformat()
    }
    
    if include_traceback:
        import traceback
        error_info['traceback'] = traceback.format_exc()
    
    return error_info

