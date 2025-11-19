"""
ARB-BOT - Generador de Contenido
Orquesta la generación de contenido usando el modelo de IA
"""

import logging
import re
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
        
        # Respuestas predefinidas para saludos comunes
        self.greeting_responses = {
            'hola': '¡Hola! 👋 Soy ARB-BOT, tu asistente institucional. Puedo responder preguntas sobre el manual de convivencia, reglamentos y políticas de la institución. ¿En qué puedo ayudarte?',
            'buenos días': '¡Buenos días! 👋 Soy ARB-BOT, tu asistente institucional. Estoy aquí para ayudarte con información sobre el manual de convivencia y las políticas de la institución. ¿Qué te gustaría saber?',
            'buenas tardes': '¡Buenas tardes! 👋 Soy ARB-BOT, tu asistente institucional. Puedo ayudarte con información sobre el manual de convivencia y las políticas de la institución. ¿En qué puedo asistirte?',
            'buenas noches': '¡Buenas noches! 👋 Soy ARB-BOT, tu asistente institucional. Estoy disponible para responder tus preguntas sobre el manual de convivencia y las políticas de la institución. ¿Cómo puedo ayudarte?',
            'hi': '¡Hola! 👋 Soy ARB-BOT, tu asistente institucional. Puedo responder preguntas sobre el manual de convivencia, reglamentos y políticas de la institución. ¿En qué puedo ayudarte?',
            'hello': '¡Hola! 👋 Soy ARB-BOT, tu asistente institucional. Puedo responder preguntas sobre el manual de convivencia, reglamentos y políticas de la institución. ¿En qué puedo ayudarte?',
        }
    
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
            
            # Paso 0: Verificar si es un saludo simple
            greeting_response = self._check_greeting(input_text)
            if greeting_response:
                logger.info("Detectado saludo simple, usando respuesta predefinida")
                return greeting_response
            
            # Paso 1: Procesar el texto de entrada
            processed_input = self.text_processor.process(input_text)
            
            # Paso 2: Construir prompt con contexto si está disponible
            if context:
                prompt = self._build_prompt_with_context(processed_input, context)
            else:
                # Si no hay contexto, usar un prompt más instructivo
                prompt = self._build_prompt_without_context(processed_input)
            
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
    
    def _check_greeting(self, input_text: str) -> Optional[str]:
        """
        Verificar si el input es un saludo simple y retornar respuesta predefinida
        
        Args:
            input_text: Texto de entrada
        
        Returns:
            Respuesta predefinida si es un saludo, None en caso contrario
        """
        # Normalizar el texto (minúsculas, sin puntuación)
        normalized = re.sub(r'[^\w\s]', '', input_text.lower().strip())
        
        # Verificar saludos exactos
        if normalized in self.greeting_responses:
            return self.greeting_responses[normalized]
        
        # Verificar saludos que empiezan con estas palabras
        words = normalized.split()
        if words:
            first_word = words[0]
            if first_word in ['hola', 'hi', 'hello']:
                return self.greeting_responses.get(first_word, self.greeting_responses['hola'])
            if len(words) >= 2:
                if f"{words[0]} {words[1]}" in self.greeting_responses:
                    return self.greeting_responses[f"{words[0]} {words[1]}"]
        
        return None
    
    def _build_prompt_without_context(self, query: str) -> str:
        """
        Construir prompt cuando no hay contexto de documentos
        
        Args:
            query: Pregunta del usuario
        
        Returns:
            Prompt formateado
        """
        prompt = f"""Eres ARB-BOT, un asistente virtual profesional de una institución educativa. Tu función es ayudar a los usuarios con información sobre el manual de convivencia, reglamentos y políticas institucionales.

INSTRUCCIONES:
- Responde SIEMPRE en español
- Sé claro, profesional y amable
- Si no tienes información específica, indica que necesitas que se carguen documentos en el sistema
- Mantén las respuestas concisas y útiles
- Si el usuario hace una pregunta que no puedes responder sin documentos, explica que necesitas que se carguen documentos primero

PREGUNTA DEL USUARIO:
{query}

RESPUESTA (en español, clara y profesional):"""
        
        return prompt
    
    def _build_prompt_with_context(self, query: str, context: str) -> str:
        """
        Construir prompt con contexto de documentos
        
        Args:
            query: Pregunta del usuario
            context: Contexto relevante de documentos
        
        Returns:
            Prompt formateado
        """
        prompt = f"""Eres ARB-BOT, un asistente virtual profesional de una institución educativa. Tu función es ayudar a los usuarios con información sobre el manual de convivencia, reglamentos y políticas institucionales.

INFORMACIÓN INSTITUCIONAL (usa esta información para responder):
{context}

PREGUNTA DEL USUARIO:
{query}

INSTRUCCIONES:
- Responde SIEMPRE en español
- Basa tu respuesta ÚNICAMENTE en la información proporcionada arriba
- Si la información no está en el contexto, indica que no tienes esa información específica
- Sé claro, profesional y amable
- Mantén las respuestas concisas y útiles

RESPUESTA (en español, basada en la información proporcionada):"""
        
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

