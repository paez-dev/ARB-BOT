"""
ARB-BOT - Generador de Contenido (Versión Mejorada)
Modo D: Resumen + Cita textual del RAG
Evita alucinaciones y asegura respuestas verificables.
"""

import logging
import re

logger = logging.getLogger("services.generator")


class ContentGenerator:
    def __init__(self, api_model, text_processor):
        self.api_model = api_model
        self.text_processor = text_processor

    # -----------------------------------------------------------
    # SANITIZACIÓN BÁSICA DEL RESUMEN (no borra todo el texto)
    # -----------------------------------------------------------
    def _sanitize_output(self, text: str):
        """Limpia frases de identidad del modelo, pero conserva el contenido útil."""
        if not text:
            return None

        low = text.lower()

        BLOCKED_PATTERNS = [
            "soy un modelo de lenguaje",
            "como ia",
            "como inteligencia artificial",
            "fui entrenado",
            "no tengo acceso",
            "no tengo la capacidad",
            "mi conocimiento se basa",
        ]

        # En la versión nueva, NO eliminamos todo → solo limpiamos la frase
        for pattern in BLOCKED_PATTERNS:
            if pattern in low:
                logger.warning("🟥 Eliminando frase de identidad IA detectada en la respuesta…")
                text = re.sub(re.escape(pattern), "", text, flags=re.IGNORECASE)

        # quitar dobles espacios si quedaron
        text = re.sub(r"\s+", " ", text).strip()

        return text if text else None

    # -----------------------------------------------------------
    # RESPUESTA ALTERNATIVA SI NO HAY CONTEXTO
    # -----------------------------------------------------------
    def _fallback_response(self, query: str):
        """Cuando no existe contexto en RAG."""
        return (
            "No se encontró información relacionada con tu consulta en los documentos cargados. "
            "Es posible que ese contenido no esté incluido aún. "
            "Puedes intentar otra pregunta o cargar el documento correspondiente."
        )

    # -----------------------------------------------------------
    # GENERACIÓN PRINCIPAL
    # -----------------------------------------------------------
    def generate(self, user_input, max_tokens=512, temperature=0.2, context=None):
        """
        MODO D: RESUMEN + CITA TEXTUAL
        - Se ignora completamente la respuesta principal del modelo.
        - El modelo SOLO genera el resumen.
        - La cita textual SIEMPRE viene directo del RAG.
        - Cero alucinaciones.
        """

        logger.info(f"🧩 Generando respuesta (Modo D) para: '{user_input}'")

        # Si NO hay contexto → No inventar nada
        if not context:
            logger.warning("⚠️ No se suministró contexto al generador. Aplicando fallback.")
            return self._fallback_response(user_input)

        # -------------------------------------------------------
        # 1. Prompt para generar SOLO un resumen claro y seguro
        # -------------------------------------------------------
        prompt = (
            "A continuación tienes un fragmento oficial del Manual de Convivencia Escolar Roldanista:\n\n"
            f"«{context}»\n\n"
            "INSTRUCCIONES IMPORTANTES:\n"
            "- Usa únicamente la información presente en el texto anterior.\n"
            "- No inventes información nueva.\n"
            "- No agregues interpretaciones externas.\n"
            "- No menciones que eres un modelo de lenguaje.\n\n"
            f"Pregunta del usuario: {user_input}\n\n"
            "Genera un resumen claro y fiel al contenido:\n\n"
            "Resumen:"
        )

        # -------------------------------------------------------
        # 2. Llamada al modelo (solo para el resumen)
        # -------------------------------------------------------
        try:
            resumen = self.api_model.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
        except Exception as e:
            logger.error(f"❌ Error generando resumen: {e}")
            resumen = None

        # -------------------------------------------------------
        # 3. Limpieza del resumen
        # -------------------------------------------------------
        if resumen:
            resumen = resumen.strip()
            resumen = self._sanitize_output(resumen)

        if not resumen:
            resumen = "No se pudo generar un resumen automático, pero a continuación se muestra el texto exacto."

        # -------------------------------------------------------
        # 4. Construcción de la respuesta final
        # -------------------------------------------------------
        respuesta_final = (
            "📌 **RESUMEN**\n"
            f"{resumen}\n\n"
            "────────────────────\n\n"
            "📄 **CITA TEXTUAL DEL MANUAL**\n"
            f"{context.strip()}\n"
        )

        logger.info("🟩 Respuesta generada exitosamente en Modo D.")
        return respuesta_final
