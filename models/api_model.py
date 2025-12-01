"""
ARB-BOT - Modelo de IA mediante API
Implementación usando APIs gratuitas de modelos avanzados
Soporta: Hugging Face Inference API, Groq, Google Gemini
"""

import logging
import requests
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class APIModel:
    """
    Clase para manejar modelos de IA mediante APIs gratuitas
    Soporta múltiples proveedores de API
    """
    
    def __init__(self, provider: str = 'huggingface', model_name: str = None, api_key: str = None):
        """
        Inicializar modelo de IA mediante API
        
        Args:
            provider: Proveedor de API ('huggingface', 'groq', 'gemini')
            model_name: Nombre del modelo (opcional, usa defaults)
            api_key: API key (opcional, puede venir de env vars)
        """
        self.provider = provider.lower()
        self.model_name = model_name or self._get_default_model()
        self.api_key = api_key or self._get_api_key()
        self.base_url = self._get_base_url()
        
        logger.info(f"Inicializando modelo API: {self.provider} - {self.model_name}")
    
    def _get_default_model(self) -> str:
        """Obtener modelo por defecto según el proveedor"""
        defaults = {
            'huggingface': 'microsoft/DialoGPT-medium',
            'groq': 'llama-3.1-8b-instant',
            'gemini': 'gemini-pro'
        }
        return defaults.get(self.provider, defaults['huggingface'])
    
    def _get_api_key(self) -> Optional[str]:
        """Obtener API key de variables de entorno"""
        env_vars = {
            'huggingface': 'HUGGINGFACE_API_KEY',
            'groq': 'GROQ_API_KEY',
            'gemini': 'GEMINI_API_KEY'
        }
        env_var = env_vars.get(self.provider)
        if env_var:
            return os.getenv(env_var)
        return None
    
    def _get_base_url(self) -> str:
        """Obtener URL base según el proveedor"""
        urls = {
            'huggingface': 'https://api-inference.huggingface.co/models',
            'groq': 'https://api.groq.com/openai/v1/chat/completions',
            'gemini': 'https://generativelanguage.googleapis.com/v1beta/models'
        }
        return urls.get(self.provider, urls['huggingface'])
    
    def generate(self, prompt: str, max_length: int = 200, temperature: float = 0.7, **kwargs) -> str:
        """
        Generar texto usando la API
        
        Args:
            prompt: Texto de entrada
            max_length: Longitud máxima (tokens aproximados)
            temperature: Control de creatividad
            **kwargs: Argumentos adicionales
        
        Returns:
            Texto generado
        """
        try:
            if self.provider == 'huggingface':
                return self._generate_huggingface(prompt, max_length, temperature)
            elif self.provider == 'groq':
                return self._generate_groq(prompt, max_length, temperature)
            elif self.provider == 'gemini':
                return self._generate_gemini(prompt, max_length, temperature)
            else:
                raise ValueError(f"Proveedor no soportado: {self.provider}")
        except Exception as e:
            logger.error(f"Error generando con API {self.provider}: {str(e)}")
            raise
    
    def _generate_huggingface(self, prompt: str, max_length: int, temperature: float) -> str:
        """Generar usando Hugging Face Inference API"""
        url = f"{self.base_url}/{self.model_name}"
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": temperature,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            elif isinstance(result, dict):
                return result.get('generated_text', '').strip()
            return str(result)
        elif response.status_code == 503:
            # Modelo cargándose, esperar un poco
            logger.warning("Modelo cargándose, esperando...")
            import time
            time.sleep(5)
            return self._generate_huggingface(prompt, max_length, temperature)
        else:
            error_msg = response.text
            logger.error(f"Error en Hugging Face API: {response.status_code} - {error_msg}")
            raise Exception(f"Error en API: {error_msg}")
    
    def _generate_groq(self, prompt: str, max_length: int, temperature: float) -> str:
        """Generar usando Groq API (gratis y rápido)"""
        if not self.api_key:
            # Intentar obtener de variables de entorno como último recurso
            self.api_key = os.getenv('GROQ_API_KEY')
            if not self.api_key:
                logger.error("GROQ_API_KEY no encontrada. Verifica que esté configurada en Railway → Settings → Variables")
                raise ValueError("GROQ_API_KEY requerida. Agrega la variable GROQ_API_KEY en Railway → Settings → Variables. Obtén una gratis en https://console.groq.com")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Groq usa formato de chat
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente útil que responde preguntas basándote en el contexto proporcionado. Responde siempre en español."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_length,
            "temperature": temperature
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            choices = result.get('choices', [])
            if choices and len(choices) > 0:
                return choices[0]['message']['content'].strip()
            return ""
        else:
            error_msg = response.text
            logger.error(f"Error en Groq API: {response.status_code} - {error_msg}")
            raise Exception(f"Error en API: {error_msg}")
    
    def _generate_gemini(self, prompt: str, max_length: int, temperature: float) -> str:
        """Generar usando Google Gemini API"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY requerida. Obtén una gratis en https://makersuite.google.com/app/apikey")
        
        url = f"{self.base_url}/{self.model_name}:generateContent"
        
        params = {
            "key": self.api_key
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": max_length,
                "temperature": temperature
            }
        }
        
        response = requests.post(url, params=params, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            candidates = result.get('candidates', [])
            if candidates and len(candidates) > 0:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts and len(parts) > 0:
                    return parts[0].get('text', '').strip()
            return ""
        else:
            error_msg = response.text
            logger.error(f"Error en Gemini API: {response.status_code} - {error_msg}")
            raise Exception(f"Error en API: {error_msg}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo"""
        return {
            'name': self.model_name,
            'provider': self.provider,
            'type': 'api',
            'free': True,
            'device': 'cloud'
        }

