"""
ARB-BOT - Procesador de Texto (Versión Optimizada)
Procesamiento, normalización y sanitización segura del texto de entrada.
Diseñado para proteger el modelo, evitar prompts dañinos y estandarizar la entrada.
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger("services.text_processor")


class TextProcessor:
    """
    Procesador de texto para:
    - limpiar caracteres peligrosos
    - normalizar saltos y espacios
    - validar longitud
    - preparar prompt para el modelo
    - extraer palabras clave (simple)
    - obtener métricas del texto
    """

    def __init__(self, min_length: int = 3, max_length: int = 500):
        self.min_length = min_length
        self.max_length = max_length

    # ==========================================================
    #                  PROCESAMIENTO PRINCIPAL
    # ==========================================================
    def process(self, text: str) -> str:
        """Procesa y limpia texto de entrada antes de pasarlo al modelo."""
        try:
            if not isinstance(text, str):
                raise ValueError("Texto inválido: se esperaba un string.")

            logger.debug(f"Texto original recibido ({len(text)} chars).")

            text = self._clean_text(text)
            text = self._normalize_spaces(text)
            text = self._validate_length(text)
            text = self._prepare_for_model(text)

            logger.info(f"Texto procesado: {len(text)} chars.")
            return text

        except Exception as e:
            logger.error(f"❌ Error procesando texto: {str(e)} — devolviendo texto original.")
            return text

    # ==========================================================
    #                  MÉTODOS DE LIMPIEZA
    # ==========================================================
    def _clean_text(self, text: str) -> str:
        """Elimina caracteres de control, normaliza saltos, protege estructura básica."""
        
        # Eliminar caracteres de control invisibles (excepto \n)
        text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)

        # Normalizar saltos a estándar UNIX
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Evitar inyecciones accidentales de backticks u otros símbolos repetidos
        text = re.sub(r"`{2,}", "`", text)
        text = re.sub(r"[<>]{2,}", "", text)

        return text.strip()

    def _normalize_spaces(self, text: str) -> str:
        """Reduce espacios múltiples y saltos excesivos."""
        text = re.sub(r" +", " ", text)        # espacios repetidos
        text = re.sub(r"\n{2,}", "\n", text)  # saltos excesivos
        return text.strip()

    # ==========================================================
    #                  VALIDACIÓN DE LONGITUD
    # ==========================================================
    def _validate_length(self, text: str) -> str:
        """Garantiza que el texto esté dentro del rango permitido."""
        if len(text) < self.min_length:
            raise ValueError(f"Texto demasiado corto (mínimo {self.min_length} caracteres).")

        if len(text) > self.max_length:
            logger.warning(f"⚠️ Texto truncado a {self.max_length} caracteres.")
            return text[:self.max_length]

        return text

    # ==========================================================
    #                  PREPARACIÓN PARA MODELO
    # ==========================================================
    def _prepare_for_model(self, text: str) -> str:
        """Asegura cierre apropiado de frase, necesario para modelos."""
        if text and text[-1] not in ".!?":
            return text + "."
        return text

    # ==========================================================
    #                  KEYWORDS (versión simple)
    # ==========================================================
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extrae palabras clave relevantes (sin librerías externas)."""

        STOP_WORDS = {
            'el','la','los','las','de','y','que','a','en','un','una','ser','se',
            'por','con','su','para','como','estar','tener','lo','todo','pero',
            'más','hacer','poder','decir','este','ese','eso','ir','si','ya',
            'me','mi','tu','él','ella','ellos','ellas','nos','muy','sin','del',
            'al','porque','cuando','aquí','allí','donde','sobre','entre','desde',
            'hasta','cada','quien','cual','qué','cual','donde','quizá','aunque',
            'también','además','durante','según','tras'
        }

        words = re.findall(r"\b\w+\b", text.lower())
        valid = [w for w in words if w not in STOP_WORDS and len(w) > 3]

        freq = {}
        for w in valid:
            freq[w] = freq.get(w, 0) + 1

        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        return [w for w, _ in sorted_words[:max_keywords]]

    # ==========================================================
    #                  ESTADÍSTICAS DEL TEXTO
    # ==========================================================
    def get_statistics(self, text: str) -> Dict:
        """Obtiene estadísticas básicas sobre el texto."""
        words = re.findall(r"\b\w+\b", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        return {
            "char_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "avg_sentence_length": sum(len(s) for s in sentences) / len(sentences) if sentences else 0,
        }
