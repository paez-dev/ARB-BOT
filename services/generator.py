"""
ARB-BOT - Generador de Contenido
Orquesta la generación de contenido usando el modelo de IA
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    Clase para generar contenido usando modelos de IA
    Coordina el procesamiento de texto y la generación
    """
    
    def __init__(self, ai_model, text_processor):
        """
        Inicializar generador de contenido
        
        Args:
            ai_model: Instancia del modelo de IA
            text_processor: Instancia del procesador de texto
        """
        self.ai_model = ai_model
        self.text_processor = text_processor
    
    def generate(self, input_text: str, max_tokens: int = 150, 
                 temperature: float = 0.7, context: Optional[str] = None, **kwargs) -> str:
        """
        Generar contenido basado en el input, opcionalmente con contexto de documentos
        
        Args:
            input_text: Texto de entrada
            max_tokens: Longitud máxima de la salida
            temperature: Temperatura para la generación
            context: Contexto adicional de documentos (opcional)
            **kwargs: Argumentos adicionales
        
        Returns:
            Contenido generado
        """
        try:
            logger.info(f"Generando contenido para: {input_text[:50]}...")
            
            # Paso 1: Procesar el texto de entrada
            processed_input = self.text_processor.process(input_text)
            
            # Paso 2: Construir prompt con contexto si está disponible
            if context:
                prompt = self._build_prompt_with_context(processed_input, context)
            else:
                prompt = processed_input
            
            # Paso 3: Generar usando el modelo de IA
            generated = self.ai_model.generate(
                prompt=prompt,
                max_length=max_tokens,
                temperature=temperature,
                num_return_sequences=1
            )
            
            # Paso 4: Post-procesar la salida
            final_output = self._post_process(generated, processed_input)
            
            logger.info(f"Contenido generado: {len(final_output)} caracteres")
            
            return final_output
            
        except Exception as e:
            logger.error(f"Error generando contenido: {str(e)}")
            return f"Lo siento, hubo un error al generar el contenido: {str(e)}"
    
    def _build_prompt_with_context(self, query: str, context: str) -> str:
        """
        Construir prompt con contexto de documentos
        
        Args:
            query: Pregunta del usuario
            context: Contexto relevante de documentos
        
        Returns:
            Prompt formateado
        """
        prompt = f"""Basándote en la siguiente información institucional, responde la pregunta del usuario de manera clara y precisa.

INFORMACIÓN INSTITUCIONAL:
{context}

PREGUNTA DEL USUARIO:
{query}

RESPUESTA (basada únicamente en la información proporcionada):"""
        
        return prompt
    
    def _post_process(self, generated_text: str, original_input: str) -> str:
        """
        Post-procesar el texto generado
        
        Args:
            generated_text: Texto generado por el modelo
            original_input: Input original
        
        Returns:
            Texto post-procesado
        """
        # Limpiar el texto generado
        cleaned = generated_text.strip()
        
        # Remover repeticiones excesivas
        cleaned = self._remove_repetitions(cleaned)
        
        # Asegurar que termine correctamente
        if cleaned and cleaned[-1] not in '.!?':
            cleaned += '.'
        
        return cleaned
    
    def _remove_repetitions(self, text: str, max_repeat: int = 3) -> str:
        """
        Remover repeticiones excesivas en el texto
        
        Args:
            text: Texto a limpiar
            max_repeat: Número máximo de repeticiones permitidas
        
        Returns:
            Texto sin repeticiones excesivas
        """
        import re
        
        # Detectar palabras repetidas consecutivamente
        words = text.split()
        cleaned_words = []
        last_word = None
        repeat_count = 0
        
        for word in words:
            if word == last_word:
                repeat_count += 1
                if repeat_count <= max_repeat:
                    cleaned_words.append(word)
            else:
                cleaned_words.append(word)
                last_word = word
                repeat_count = 1
        
        return ' '.join(cleaned_words)
    
    def generate_with_context(self, input_text: str, context: Optional[str] = None,
                            max_tokens: int = 150, temperature: float = 0.7) -> Dict:
        """
        Generar contenido con contexto adicional
        
        Args:
            input_text: Texto de entrada
            context: Contexto adicional (opcional)
            max_tokens: Longitud máxima
            temperature: Temperatura
        
        Returns:
            Diccionario con contenido generado y metadata
        """
        try:
            # Construir prompt con contexto si está disponible
            if context:
                full_prompt = f"Contexto: {context}\n\nPregunta: {input_text}\n\nRespuesta:"
            else:
                full_prompt = input_text
            
            # Generar contenido
            generated = self.generate(
                full_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extraer keywords
            keywords = self.text_processor.extract_keywords(generated)
            
            # Obtener estadísticas
            stats = self.text_processor.get_statistics(generated)
            
            return {
                'content': generated,
                'keywords': keywords,
                'statistics': stats,
                'model_info': self.ai_model.get_model_info()
            }
            
        except Exception as e:
            logger.error(f"Error en generación con contexto: {str(e)}")
            return {
                'content': f"Error: {str(e)}",
                'keywords': [],
                'statistics': {},
                'model_info': {}
            }

