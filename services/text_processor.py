"""
ARB-BOT - Procesador de Texto
Procesamiento y limpieza de texto de entrada
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class TextProcessor:
    """
    Clase para procesar y limpiar texto
    Utiliza solo librerías estándar de Python (gratuito)
    """
    
    def __init__(self):
        """Inicializar procesador de texto"""
        self.min_length = 3
        self.max_length = 500
    
    def process(self, text: str) -> str:
        """
        Procesar texto de entrada
        
        Args:
            text: Texto a procesar
        
        Returns:
            Texto procesado y limpio
        """
        try:
            # Paso 1: Limpiar texto básico
            cleaned = self._clean_text(text)
            
            # Paso 2: Normalizar espacios
            normalized = self._normalize_spaces(cleaned)
            
            # Paso 3: Validar longitud
            validated = self._validate_length(normalized)
            
            # Paso 4: Preparar para modelo
            prepared = self._prepare_for_model(validated)
            
            logger.info(f"Texto procesado: {len(text)} -> {len(prepared)} caracteres")
            
            return prepared
            
        except Exception as e:
            logger.error(f"Error procesando texto: {str(e)}")
            return text  # Retornar texto original si hay error
    
    def _clean_text(self, text: str) -> str:
        """Limpiar texto de caracteres especiales no deseados"""
        # Remover caracteres de control excepto saltos de línea
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalizar saltos de línea
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        return text.strip()
    
    def _normalize_spaces(self, text: str) -> str:
        """Normalizar espacios en blanco"""
        # Reemplazar múltiples espacios con uno solo
        text = re.sub(r' +', ' ', text)
        
        # Reemplazar múltiples saltos de línea con uno solo
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def _validate_length(self, text: str) -> str:
        """Validar y ajustar longitud del texto"""
        if len(text) < self.min_length:
            raise ValueError(f"Texto muy corto. Mínimo {self.min_length} caracteres")
        
        if len(text) > self.max_length:
            # Truncar si es muy largo
            text = text[:self.max_length]
            logger.warning(f"Texto truncado a {self.max_length} caracteres")
        
        return text
    
    def _prepare_for_model(self, text: str) -> str:
        """Preparar texto para el modelo de IA"""
        # Asegurar que el texto termine con un punto o signo de interrogación
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extraer palabras clave del texto (implementación simple)
        
        Args:
            text: Texto del cual extraer keywords
            max_keywords: Número máximo de keywords
        
        Returns:
            Lista de palabras clave
        """
        # Palabras comunes a ignorar (stop words básicas)
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
            'no', 'haber', 'por', 'con', 'su', 'para', 'como', 'estar',
            'tener', 'le', 'lo', 'todo', 'pero', 'más', 'hacer', 'o',
            'poder', 'decir', 'este', 'ir', 'otro', 'ese', 'la', 'si',
            'me', 'ya', 'ver', 'porque', 'dar', 'cuando', 'él', 'muy',
            'sin', 'vez', 'mucho', 'saber', 'qué', 'sobre', 'mi', 'alguno',
            'mismo', 'yo', 'también', 'hasta', 'año', 'dos', 'querer',
            'entre', 'así', 'primero', 'desde', 'grande', 'eso', 'ni',
            'nos', 'llegar', 'pasar', 'tiempo', 'ella', 'sí', 'día',
            'uno', 'bien', 'poco', 'deber', 'entonces', 'poner', 'cosa',
            'tanto', 'hombre', 'parecer', 'nuestro', 'tan', 'donde',
            'ahora', 'parte', 'después', 'vida', 'quedar', 'siempre',
            'creer', 'hablar', 'llevar', 'dejar', 'nada', 'cada', 'seguir',
            'menos', 'nuevo', 'encontrar', 'venir', 'pensar', 'casa',
            'mirar', 'deber', 'encontrar', 'señor', 'problema', 'mundo',
            'hacer', 'trabajo', 'forma', 'mujer', 'caso', 'día', 'mano',
            'mientras', 'contra', 'según', 'menos', 'mismo', 'año',
            'antes', 'eje', 'parecer', 'presente', 'si', 'sin', 'trabajo',
            'tanto', 'aunque', 'centro', 'mientras', 'además', 'durante',
            'también', 'así', 'cual', 'cuando', 'donde', 'mientras', 'pero',
            'porque', 'que', 'si', 'sin', 'sobre', 'tras', 'durante',
            'mediante', 'según', 'incluso', 'además', 'también', 'aunque'
        }
        
        # Convertir a minúsculas y dividir en palabras
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrar stop words y palabras muy cortas
        keywords = [
            word for word in words
            if word not in stop_words and len(word) > 3
        ]
        
        # Contar frecuencia
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Ordenar por frecuencia y retornar top N
        sorted_keywords = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [word for word, _ in sorted_keywords[:max_keywords]]
    
    def get_statistics(self, text: str) -> Dict:
        """
        Obtener estadísticas del texto
        
        Args:
            text: Texto a analizar
        
        Returns:
            Diccionario con estadísticas
        """
        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return {
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        }

