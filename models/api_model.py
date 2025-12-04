"""
ARB-BOT - APIModel (Versión PRO)
Modelo de IA unificado para Groq / HuggingFace / Gemini.
Optimizado para producción, Railway, timeouts y estabilidad.
"""

import logging
import requests
import os
from typing import Optional, Dict, Any

logger = logging.getLogger("services.api_model")


class APIModel:
    """Maneja modelos de IA vía API externa (RAG-safe)."""

    def __init__(self, provider: str = "groq", model_name: str = None, api_key: str = None):
        self.provider = provider.lower()
        self.model_name = model_name or self._get_default_model()
        self.api_key = api_key or self._get_api_key()

        self.base_url = self._get_base_url()

        logger.info(f"🧠 APIModel inicializado: provider={self.provider}, model={self.model_name}")

    # -------------------------------------------------------------
    # CONFIG
    # -------------------------------------------------------------
    def _get_default_model(self) -> str:
        defaults = {
            "groq": "llama-3.1-8b-instant",
            "huggingface": "microsoft/DialoGPT-medium",
            "gemini": "gemini-pro",
        }
        return defaults.get(self.provider, "microsoft/DialoGPT-medium")

    def _get_api_key(self) -> Optional[str]:
        env_keys = {
            "groq": "GROQ_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "gemini": "GEMINI_API_KEY",
        }
        return os.getenv(env_keys.get(self.provider, ""), None)

    def _get_base_url(self) -> str:
        urls = {
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "huggingface": "https://api-inference.huggingface.co/models",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
        }
        return urls.get(self.provider)

    # -------------------------------------------------------------
    # GENERATE (ENTRADA PRINCIPAL)
    # -------------------------------------------------------------
    def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        """
        Punto de entrada único.
        Maneja errores y normaliza la salida.
        """
        try:
            if self.provider == "groq":
                response = self._generate_groq(prompt, max_tokens, temperature)
            elif self.provider == "huggingface":
                response = self._generate_huggingface(prompt, max_tokens, temperature)
            elif self.provider == "gemini":
                response = self._generate_gemini(prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Proveedor no soportado: {self.provider}")

            clean = self._sanitize_response(response)
            return clean

        except Exception as e:
            logger.error(f"❌ Error generando respuesta: {e}")
            return ""

    # -------------------------------------------------------------
    # SANITIZACIÓN DE RESPUESTA
    # -------------------------------------------------------------
    def _sanitize_response(self, text: str) -> str:
        """Limpia respuestas con formato incorrecto."""
        if not text:
            return ""

        text = text.replace("\u0000", "")
        text = text.replace("\r", "").strip()

        # Evitar respuestas típicas de IA
        blocked = [
            "como modelo de lenguaje",
            "no tengo acceso",
            "fui entrenado",
            "mi conocimiento",
            "no puedo navegar",
        ]

        t = text.lower()
        for b in blocked:
            if b in t:
                logger.warning("⚠️ Respuesta parecía inventada. Bloqueando.")
                return ""

        return text

    # -------------------------------------------------------------
    # IMPLEMENTACIONES POR PROVEEDOR
    # -------------------------------------------------------------
    def _generate_groq(self, prompt: str, max_tokens: int, temperature: float) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY faltante.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "Responde únicamente con base en el contexto entregado."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=25
            )
        except Exception as e:
            logger.error(f"🚫 Error de conexión Groq: {e}")
            return ""

        if response.status_code != 200:
            logger.error(f"Groq error {response.status_code}: {response.text}")
            return ""

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return ""

    # -------------------------------------------------------------
    def _generate_huggingface(self, prompt: str, max_tokens: int, temperature: float) -> str:
        url = f"{self.base_url}/{self.model_name}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
            }
        }

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=45)
        except Exception as e:
            logger.error(f"HF connection error: {e}")
            return ""

        if r.status_code == 200:
            try:
                out = r.json()
                if isinstance(out, list) and out:
                    return out[0].get("generated_text", "").strip()
                if isinstance(out, dict):
                    return out.get("generated_text", "").strip()
            except Exception:
                return ""

        logger.error(f"HF API error: {r.status_code} → {r.text}")
        return ""

    # -------------------------------------------------------------
    def _generate_gemini(self, prompt: str, max_tokens: int, temperature: float) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY faltante")

        url = f"{self.base_url}/{self.model_name}:generateContent"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            }
        }

        try:
            r = requests.post(url, params={"key": self.api_key}, json=payload, timeout=45)
        except Exception as e:
            logger.error(f"Gemini connection error: {e}")
            return ""

        if r.status_code != 200:
            logger.error(f"Gemini error {r.status_code}: {r.text}")
            return ""

        try:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            return ""

    # -------------------------------------------------------------
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model_name,
            "api_key_loaded": bool(self.api_key),
        }
