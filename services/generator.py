"""
ARB-BOT - Generador de Contenido
Orquesta la generación de contenido usando el modelo de IA
"""

import logging
import re

logger = logging.getLogger("services.generator")

class ContentGenerator:
    def __init__(self, api_model, text_processor):
        self.api_model = api_model
        self.text_processor = text_processor

    def _sanitize_output(self, text):
        """Limpia frases tipo chatbot o modelo de lenguaje."""
        low = text.lower()

        BLOCKED_PATTERNS = [
            "soy un modelo de lenguaje",
            "no tengo acceso",
            "no tengo la capacidad",
            "como ia",
            "como inteligencia artificial",
            "fui entrenado",
            "no puedo navegar",
            "no puedo acceder a",
            "mi conocimiento se basa",
            "no tengo información suficiente",
            "no encuentro información específica",
            "no tengo conocimientos",
        ]

        for p in BLOCKED_PATTERNS:
            if p in low:
                logger.warning("🟥 Detectado output típico de IA — reescribiendo...")
                return None

        return text

    def _format_contextual_answer(self, query, context):
        """Cuando se usa contexto real"""
        intro = "Según el Manual de Convivencia Escolar Roldanista, se establece lo siguiente:\n\n"
        response = intro + context
        return response.strip()

    def _rewrite_based_on_context(self, query, context):
        """En caso de que el modelo genere frases IA, reescribimos manualmente"""

        return f"De acuerdo con el contenido del Manual de Convivencia Escolar, en relación con tu consulta:\n\n🧾 *{query}*\n\nSe establece lo siguiente:\n\n{context}"

    def _fallback_response(self, query):
        """Cuando NO hay contexto disponible"""
        return (
            "Actualmente no tengo información cargada en mi base documental relacionada con tu consulta. "
            "Es posible que el documento aún no haya sido cargado en el sistema o que no contenga ese contenido. "
            "Si lo deseas, puedo intentar ayudarte con otra pregunta relacionada."
        )

    def generate(self, user_input, max_tokens=512, temperature=0.2, context=None):
        """Generación final controlada"""

        logger.info(f"🧩 Generando respuesta para: '{user_input}'")

        # SIN CONTEXTO → NO inventar
        if not context:
            logger.warning("⚠️ No se suministró contexto al generador. Evitando alucinaciones.")
            return self._fallback_response(user_input)

        # Con contexto → generar respuesta
        prompt = (
            "Con base únicamente en el siguiente texto del Manual de Convivencia Escolar Roldanista:\n\n"
            f"«{context}»\n\n"
            "Responde a la siguiente pregunta del usuario, sin inventar información y citando textualmente cuando sea posible:\n\n"
            f"Pregunta: {user_input}\n\n"
            "Respuesta:"
        )

        raw_output = self.api_model.generate(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

        if not raw_output:
            logger.warning("⚠️ El modelo no devolvió respuesta. Usando fallback.")
            return self._fallback_response(user_input)

        # Limpieza
        output = raw_output.strip()
        filtered = self._sanitize_output(output)

        if filtered:
            logger.info("🟩 Respuesta aprobada por filtro de alucinación.")
            return filtered

        # Si el modelo intenta sonar como ChatGPT
        logger.warning("⚠️ Reescribiendo respuesta con estilo documental.")
        return self._rewrite_based_on_context(user_input, context)
