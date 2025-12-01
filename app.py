"""
ARB-BOT - Aplicación Principal
Sistema de chatbot institucional con IA usando RAG
"""

#!/usr/bin/env python3
"""
app.py - ARB-BOT Flask application
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, session, render_template

from config import config  # as you had
from models.api_model import APIModel
from services.text_processor import TextProcessor
from services.generator import ContentGenerator
from services.rag_service import get_rag_instance, RAGService
from database.db import init_db, save_interaction, get_recent_interactions

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app")

app = Flask(__name__, static_folder="static", template_folder="templates")

# Load configuration
config_name = os.getenv("FLASK_ENV", "development")
app.config.from_object(config[config_name])

# Secret key for session (set in env in production)
app.secret_key = os.getenv("FLASK_SECRET_KEY", app.secret_key or "change-me-in-prod")

# Init DB (local interactions DB)
init_db(app.config["DATABASE_URL"])

# Services
text_processor = TextProcessor()
ai_model = None
content_generator = None
rag_service_singleton = None  # loaded lazily


def get_ai_model():
    """Lazy load AI model wrapper (APIModel + ContentGenerator)."""
    global ai_model, content_generator
    if ai_model is None:
        provider = app.config.get("API_PROVIDER", "groq")
        model_name = app.config.get("API_MODEL_NAME")
        api_key = None
        if provider == "groq":
            api_key = app.config.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.error("GROQ_API_KEY no encontrada.")
                raise RuntimeError("GROQ_API_KEY required for provider groq")
        elif provider == "huggingface":
            api_key = app.config.get("HUGGINGFACE_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
        elif provider == "gemini":
            api_key = app.config.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        ai_model = APIModel(provider=provider, model_name=model_name, api_key=api_key)
        content_generator = ContentGenerator(ai_model, text_processor)
        logger.info(f"API model initialized: {provider} - {ai_model.model_name}")
    return ai_model, content_generator


def get_rag_service():
    """Lazy load RAG service (Supabase)."""
    global rag_service_singleton
    if rag_service_singleton is None:
        try:
            rag_service_singleton = get_rag_instance()
        except Exception as e:
            logger.error(f"Error inicializando RAGService: {e}")
            rag_service_singleton = None
            raise
    return rag_service_singleton


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ARB-BOT",
        "timestamp": datetime.utcnow().isoformat(),
        "rag_loaded": rag_service_singleton is not None
    })


@app.route("/api/generate", methods=["POST"])
def generate_content():
    """
    Endpoint principal de generación:
    - recibe input
    - procesa texto
    - obtiene contexto desde RAG (Supabase)
    - genera respuesta con el modelo seleccionado
    """
    try:
        payload = request.get_json()
        if not payload or "input" not in payload:
            return jsonify({"error": "Input requerido", "status": "error"}), 400

        user_input = payload["input"]
        if len(user_input) < app.config.get("MIN_INPUT_LENGTH", 2):
            return jsonify({"error": "Input muy corto", "status": "error"}), 400
        if len(user_input) > app.config.get("MAX_INPUT_LENGTH", 8000):
            return jsonify({"error": "Input muy largo", "status": "error"}), 400

        logger.info(f"Procesando input: {user_input[:80]}...")

        # 1) Procesar input (limpieza)
        processed_input = text_processor.process(user_input)

        # 2) Obtener contexto RAG
        context = ""
        rag_docs_count = 0
        rag = None
        try:
            rag = get_rag_service()
            if rag:
                stats = rag.get_stats()
                rag_docs_count = int(stats.get("total_documents", 0) or 0)
                # Solo buscar si hay documentos
                if rag_docs_count > 0:
                    context = rag.get_context_for_query(processed_input, top_k=6, max_context_length=3000)
                    if context:
                        logger.info(f"Context encontrado: {len(context)} chars")
                    else:
                        logger.info("No se encontró contexto relevante para la query.")
            else:
                logger.warning("RAG service no disponible.")
        except Exception as e:
            # No queremos bloquear la respuesta por fallo en RAG
            logger.warning(f"Error consultando RAG: {e}")
            context = ""

        # 3) Generar respuesta
        ai_inst, generator = get_ai_model()
        generated = generator.generate(
            processed_input,
            max_tokens=app.config.get("MAX_TOKENS", 512),
            temperature=app.config.get("TEMPERATURE", 0.2),
            context=context if context else None
        )

        # 4) Guardar interacción (no crítico)
        try:
            save_interaction(
                user_input=user_input,
                generated_output=generated,
                model_used=f"{app.config.get('API_PROVIDER','groq')}-{ai_inst.model_name if ai_inst else 'N/A'}",
                processing_time=0.0,
                metadata={"context_used": bool(context)}
            )
        except Exception as e:
            logger.warning(f"No se pudo guardar interacción: {e}")

        return jsonify({
            "status": "success",
            "input": user_input,
            "processed_input": processed_input,
            "generated_content": generated,
            "context_used": bool(context),
            "rag_total_docs": rag_docs_count
        }), 200

    except Exception as e:
        logger.exception("Error en /api/generate")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/search-documents", methods=["POST"])
def search_documents():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Query requerido", "status": "error"}), 400
        query = data["query"]
        top_k = int(data.get("top_k", 5))
        rag = get_rag_service()
        results = rag.search_similar_chunks(query, top_k=top_k)
        return jsonify({"status": "success", "query": query, "results": results, "count": len(results)})
    except Exception as e:
        logger.exception("Error en /api/search-documents")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rag-stats", methods=["GET"])
def rag_stats():
    try:
        rag = get_rag_service()
        stats = rag.get_stats() if rag else {}
        return jsonify({"status": "success", "stats": stats})
    except Exception as e:
        logger.exception("Error en /api/rag-stats")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    logger.info("Starting ARB-BOT app...")
    env = os.getenv("FLASK_ENV", "development")
    logger.info(f"Environment: {env}")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)