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
            
            # Cargar tokenizador y modelo con opciones de bajo consumo
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=True
            )
            
            # Cargar modelo con optimizaciones de memoria
            # Intentar con accelerate, si falla usar método simple
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    device_map="cpu"
                )
            except Exception as e:
                # Fallback: cargar sin optimizaciones avanzadas
                logger.warning(f"No se pudo cargar con optimizaciones: {e}. Usando método simple...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32
                )
            
            # Configurar padding token si no existe
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Crear pipeline de generación con opciones optimizadas
            self.generator = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # CPU
                model_kwargs={
                    'low_cpu_mem_usage': True,
                    'torch_dtype': torch.float32
                }
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
            
            self.model_name = 'distilgpt2'  # Usar el más ligero
            self.tokenizer = AutoTokenizer.from_pretrained(
                'distilgpt2',
                use_fast=True
            )
            # Cargar modelo de respaldo sin optimizaciones avanzadas
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    'distilgpt2',
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    device_map="cpu"
                )
            except Exception:
                # Fallback final: sin optimizaciones
                self.model = AutoModelForCausalLM.from_pretrained(
                    'distilgpt2',
                    torch_dtype=torch.float32
                )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.generator = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,
                model_kwargs={
                    'low_cpu_mem_usage': True,
                    'torch_dtype': torch.float32
                }
            )
            
            logger.info("Modelo de respaldo cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelo de respaldo: {str(e)}")
            raise Exception("No se pudo cargar ningún modelo de IA")
    
    def generate(self, prompt, max_length=150, temperature=0.7, num_return_sequences=1):
        """
        Generar texto basado en un prompt
        
        Args:
            prompt: Texto de entrada
            max_length: Longitud máxima de la salida
            temperature: Control de creatividad (0.0-1.0)
            num_return_sequences: Número de secuencias a generar
        
        Returns:
            Texto generado
        """
        try:
            if not self.generator:
                raise Exception("Modelo no inicializado")
            
            # Generar texto
            results = self.generator(
                prompt,
                max_length=max_length,
                temperature=temperature,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extraer texto generado
            if results and len(results) > 0:
                generated_text = results[0]['generated_text']
                # Remover el prompt original de la salida
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                return generated_text
            else:
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

