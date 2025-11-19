"""
ARB-BOT - Modelo de IA
Implementación usando modelos gratuitos de Hugging Face
"""

import logging
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

logger = logging.getLogger(__name__)

class AIModel:
    """
    Clase para manejar modelos de IA gratuitos
    Utiliza Hugging Face Transformers (100% gratuito)
    """
    
    def __init__(self, model_name='distilgpt2'):
        """
        Inicializar modelo de IA
        
        Args:
            model_name: Nombre del modelo a usar (debe estar en Hugging Face)
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.generator = None
        self._load_model()
    
    def _load_model(self):
        """Cargar el modelo desde Hugging Face con optimizaciones de memoria"""
        try:
            logger.info(f"Cargando modelo: {self.model_name}")
            
            # Optimizaciones de memoria para PyTorch
            import torch
            torch.set_num_threads(1)  # Reducir threads para ahorrar memoria
            
            # Intentar cargar tokenizador (primero con use_fast, luego sin)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    use_fast=True
                )
            except Exception as tokenizer_error:
                logger.warning(f"No se pudo cargar tokenizer rápido, intentando sin use_fast: {tokenizer_error}")
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.model_name,
                        use_fast=False
                    )
                except Exception:
                    logger.error(f"No se pudo cargar tokenizer para {self.model_name}")
                    raise tokenizer_error
            
            # Cargar modelo con optimizaciones de memoria
            # No usar device_map para evitar conflictos con accelerate
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            # Mover modelo a CPU explícitamente (si no está ya)
            if torch.cuda.is_available():
                self.model = self.model.to('cpu')
            else:
                self.model = self.model.to('cpu')
            
            # Configurar padding token si no existe
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Crear pipeline de generación sin especificar device
            # El modelo ya está en CPU, no necesitamos especificarlo
            self.generator = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                model_kwargs={
                    'low_cpu_mem_usage': True,
                    'torch_dtype': torch.float32
                },
                truncation=True
            )
            
            logger.info(f"Modelo {self.model_name} cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {str(e)}")
            # Fallback a un modelo más simple
            logger.info("Intentando cargar modelo alternativo...")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Cargar modelo de respaldo si el principal falla"""
        try:
            import torch
            torch.set_num_threads(1)
            
            # Determinar modelo de respaldo basado en el modelo original
            original_model = self.model_name.lower()
            if 'spanish' in original_model or 'es' in original_model or 'bne' in original_model or 'plan' in original_model:
                # Si el modelo original era en español, intentar modelos en español
                fallback_models = ['microsoft/DialoGPT-small', 'gpt2', 'distilgpt2']
            else:
                # Si no, usar modelos estándar
                fallback_models = ['distilgpt2', 'gpt2']
            
            # Intentar cargar modelos de respaldo en orden
            for fallback_model in fallback_models:
                try:
                    logger.info(f"Intentando cargar modelo de respaldo: {fallback_model}")
                    self.model_name = fallback_model
                    
                    # Intentar cargar tokenizer
                    try:
                        self.tokenizer = AutoTokenizer.from_pretrained(
                            fallback_model,
                            use_fast=True
                        )
                    except Exception:
                        self.tokenizer = AutoTokenizer.from_pretrained(
                            fallback_model,
                            use_fast=False
                        )
                    
                    # Cargar modelo de respaldo
                    self.model = AutoModelForCausalLM.from_pretrained(
                        fallback_model,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True
                    )
                    
                    # Mover modelo a CPU
                    self.model = self.model.to('cpu')
                    
                    if self.tokenizer.pad_token is None:
                        self.tokenizer.pad_token = self.tokenizer.eos_token
                    
                    # Crear pipeline sin especificar device
                    self.generator = pipeline(
                        'text-generation',
                        model=self.model,
                        tokenizer=self.tokenizer,
                        model_kwargs={
                            'low_cpu_mem_usage': True,
                            'torch_dtype': torch.float32
                        },
                        truncation=True
                    )
                    
                    logger.info(f"Modelo de respaldo {fallback_model} cargado exitosamente")
                    return  # Éxito, salir del bucle
                    
                except Exception as fallback_error:
                    logger.warning(f"No se pudo cargar {fallback_model}: {fallback_error}")
                    continue  # Intentar siguiente modelo
            
            # Si todos los modelos de respaldo fallaron
            raise Exception("No se pudo cargar ningún modelo de respaldo")
            
        except Exception as e:
            logger.error(f"Error cargando modelo de respaldo: {str(e)}")
            raise Exception("No se pudo cargar ningún modelo de IA")
    
    def generate(self, prompt, max_length=150, temperature=0.7, num_return_sequences=1):
        """
        Generar texto basado en un prompt
        
        Args:
            prompt: Texto de entrada
            max_length: Longitud máxima total (prompt + generación) - DEPRECATED, usar max_new_tokens
            temperature: Control de creatividad (0.0-1.0)
            num_return_sequences: Número de secuencias a generar
        
        Returns:
            Texto generado
        """
        try:
            if not self.generator:
                raise Exception("Modelo no inicializado")
            
            # Calcular max_new_tokens basado en max_length y longitud del prompt
            # Si max_length es 150 y el prompt es largo, usar max_new_tokens en su lugar
            prompt_tokens = len(self.tokenizer.encode(prompt))
            
            # Usar max_new_tokens para evitar el error cuando el prompt es largo
            # max_new_tokens especifica cuántos tokens nuevos generar, no el total
            # Para DialoGPT, dar más espacio para generar respuestas completas
            if prompt_tokens >= max_length:
                # Si el prompt ya es muy largo, generar al menos 100 tokens nuevos
                max_new_tokens = 100
            else:
                # Generar tokens nuevos hasta alcanzar max_length total
                # Asegurar mínimo de 100 tokens para respuestas útiles (aumentado para DialoGPT)
                max_new_tokens = max(100, min(150, max_length - prompt_tokens + 50))
            
            logger.debug(f"Prompt tokens: {prompt_tokens}, max_new_tokens: {max_new_tokens}")
            
            # Generar texto usando max_new_tokens en lugar de max_length
            results = self.generator(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                truncation=True
            )
            
            # Extraer texto generado
            if results and len(results) > 0:
                generated_text = results[0]['generated_text']
                logger.info(f"Texto generado completo (primeros 300 chars): {generated_text[:300]}")
                logger.info(f"Longitud del texto generado: {len(generated_text)} caracteres")
                logger.info(f"Longitud del prompt: {len(prompt)} caracteres")
                
                # Para DialoGPT, el formato puede ser diferente
                # DialoGPT puede incluir el prompt o generar directamente
                original_generated = generated_text
                
                # Remover el prompt original de la salida
                # Para DialoGPT, el prompt puede estar al inicio o puede que el modelo genere directamente
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                    logger.info(f"Prompt encontrado al inicio, texto restante: {len(generated_text)} caracteres")
                else:
                    # Intentar encontrar el prompt en el texto
                    prompt_index = generated_text.find(prompt)
                    if prompt_index >= 0:
                        generated_text = generated_text[prompt_index + len(prompt):].strip()
                        logger.info(f"Prompt encontrado en posición {prompt_index}, texto restante: {len(generated_text)} caracteres")
                    else:
                        # Si no se encuentra el prompt completo, intentar encontrar solo la última parte
                        # Buscar "Respuesta:" o "Responde" que es lo que viene después del contexto
                        if "Respuesta:" in generated_text:
                            generated_text = generated_text.split("Respuesta:")[-1].strip()
                            logger.info(f"Encontrado 'Respuesta:' en el texto, usando lo que viene después")
                        elif "Responde" in generated_text and ":" in generated_text:
                            # Buscar la última ocurrencia de "Responde" seguida de ":"
                            parts = generated_text.split("Responde")
                            if len(parts) > 1:
                                last_part = parts[-1]
                                if ":" in last_part:
                                    generated_text = last_part.split(":", 1)[-1].strip()
                                    logger.info(f"Encontrado 'Responde:' en el texto, usando lo que viene después")
                        else:
                            # Si no se encuentra, usar todo el texto generado (DialoGPT puede hacer esto)
                            logger.info(f"Prompt no encontrado en el texto generado, usando todo el texto generado")
                            generated_text = generated_text.strip()
                
                # Validar que el texto generado no esté vacío
                if not generated_text or len(generated_text.strip()) == 0:
                    logger.warning(f"El modelo generó texto vacío después de remover prompt.")
                    logger.warning(f"Texto original completo: '{original_generated}'")
                    logger.warning(f"Prompt usado: '{prompt[:200]}...'")
                    logger.warning("Intentando con parámetros diferentes...")
                    
                    # Intentar de nuevo con más tokens y temperatura más alta
                    # También intentar con un prompt MUY simple - solo la pregunta
                    try:
                        # Extraer solo la pregunta del usuario del prompt
                        question_part = None
                        
                        # Buscar diferentes formatos de pregunta en el prompt
                        if "Responde esta pregunta en español:" in prompt:
                            question_part = prompt.split("Responde esta pregunta en español:")[-1].split("Respuesta:")[0].strip()
                        elif "Pregunta:" in prompt:
                            question_part = prompt.split("Pregunta:")[-1].split("Responde")[0].strip()
                        elif "PREGUNTA DEL USUARIO:" in prompt:
                            question_part = prompt.split("PREGUNTA DEL USUARIO:")[-1].split("RESPUESTA")[0].strip()
                        
                        if question_part and len(question_part) > 5:
                            # Usar solo la pregunta, sin contexto
                            simple_prompt = f"{question_part}\n\nRespuesta:"
                        else:
                            # Si no encontramos la pregunta, usar solo los últimos 50 caracteres
                            simple_prompt = prompt[-100:] if len(prompt) > 100 else prompt
                        
                        logger.info(f"Segundo intento con prompt simplificado (solo pregunta): {simple_prompt[:150]}")
                        
                        results = self.generator(
                            simple_prompt,
                            max_new_tokens=120,
                            temperature=min(0.9, temperature + 0.2),
                            num_return_sequences=1,
                            do_sample=True,
                            pad_token_id=self.tokenizer.eos_token_id,
                            truncation=True
                        )
                        if results and len(results) > 0:
                            generated_text = results[0]['generated_text']
                            logger.info(f"Segundo intento - Texto generado completo: {generated_text[:300]}")
                            
                            # Para el segundo intento, remover el prompt simple si está presente
                            if generated_text.startswith(simple_prompt):
                                generated_text = generated_text[len(simple_prompt):].strip()
                            elif "Respuesta:" in generated_text:
                                # Si hay "Respuesta:" en el texto, usar solo lo que viene después
                                generated_text = generated_text.split("Respuesta:")[-1].strip()
                            elif simple_prompt in generated_text:
                                # Si el prompt está en algún lugar del texto, removerlo
                                prompt_index = generated_text.find(simple_prompt)
                                if prompt_index >= 0:
                                    generated_text = generated_text[prompt_index + len(simple_prompt):].strip()
                                else:
                                    generated_text = generated_text.strip()
                            else:
                                # Para DialoGPT, puede que no incluya el prompt - usar todo
                                generated_text = generated_text.strip()
                            
                            logger.info(f"Segundo intento - Texto después de remover prompt: '{generated_text[:200]}'")
                    except Exception as retry_error:
                        logger.error(f"Error en segundo intento: {retry_error}")
                
                # Si aún está vacío, verificar si el texto original tiene contenido útil
                if not generated_text or len(generated_text.strip()) == 0:
                    # Último recurso: verificar si el texto original tiene algo útil
                    # A veces DialoGPT genera sin incluir el prompt completo
                    if original_generated and len(original_generated) > len(prompt):
                        # Si el texto generado es más largo que el prompt, puede que tenga contenido
                        # Intentar extraer solo las últimas palabras que no están en el prompt
                        words_generated = original_generated.split()
                        words_prompt = prompt.split()
                        
                        # Buscar dónde termina el prompt en el texto generado
                        if len(words_generated) > len(words_prompt):
                            # Tomar las últimas palabras que no están en el prompt
                            potential_response = ' '.join(words_generated[len(words_prompt):])
                            if potential_response.strip() and len(potential_response.strip()) > 10:
                                logger.info(f"Extrayendo respuesta de texto generado: {potential_response[:100]}")
                                generated_text = potential_response.strip()
                
                # Validar que la respuesta tenga sentido (mínimo 10 caracteres y al menos 3 palabras)
                if not generated_text or len(generated_text.strip()) < 10:
                    logger.error(f"Respuesta generada muy corta o vacía. Modelo: {self.model_name}")
                    logger.error(f"Texto generado: '{generated_text}'")
                    logger.error(f"Prompt usado (últimos 300 chars): ...{prompt[-300:]}")
                    logger.error(f"Texto original generado (primeros 200 chars): {original_generated[:200]}")
                    return "Lo siento, no pude generar una respuesta coherente. Por favor, intenta reformular tu pregunta de manera más específica o verifica que hay documentos cargados en el sistema."
                
                # Validar que tenga al menos 3 palabras
                words = generated_text.split()
                if len(words) < 3:
                    logger.warning(f"Respuesta generada tiene muy pocas palabras ({len(words)}): '{generated_text}'")
                    return "Lo siento, la respuesta generada no es suficientemente completa. Por favor, intenta hacer una pregunta más específica."
                
                logger.info(f"Texto final generado: {len(generated_text)} caracteres - '{generated_text[:100]}...'")
                return generated_text
            else:
                logger.error("El modelo no retornó resultados")
                return "No se pudo generar contenido."
                
        except Exception as e:
            logger.error(f"Error en generación: {str(e)}")
            return f"Error al generar contenido: {str(e)}"
    
    def get_model_info(self):
        """Obtener información del modelo actual"""
        return {
            'name': self.model_name,
            'type': 'causal_lm',
            'provider': 'huggingface',
            'free': True,
            'device': 'CPU'
        }

