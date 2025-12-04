#!/usr/bin/env python3
"""
app.py — ARB-BOT (Versión PRO)
Sistema robusto de chatbot institucional con RAG + IA
Optimizado para producción en Railway
"""

import os
import time
import logging
from datetime import datetime
from flask import Flask, jsonify, request, render_template

# Configuración
from config import config

# Servicios internos
from models.api_model import APIModel
from services.text_processor import TextProcessor
from services.generator import ContentGenerator
from services.rag_service import get_rag_instance

# Base de datos interna (interacciones)
from database.db import init_db, save_interaction

# ---------------------------------------------------------------------
# LOGGING PROFESIONAL
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("ARB-BOT")

# ---------------------------------------------------------------------
# FLASK APP
# ---------------------------------------------------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")

config_name = os.getenv("FLASK_ENV", "production")
app.config.from_object(config[config_name])

# SECRET KEY (requerido)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "arb-bot-secret-key")

# Iniciar DB local (para interacciones)
try:
    init_db(app.config.get("DATABASE_URL"))
    logger.info("DB interna inicializada.")
except Exception as e:
    logger.warning(f"No se pudo inicializar DB local: {e}")

# ---------------------------------------------------------------------
# INSTANCIAS LAZY (cargan solo una vez)
# ---------------------------------------------------------------------
text_processor = TextProcessor()
_ai_model_instance = None
_generator_instance = None
_rag_instance = None


# ---------------------------------------------------------------------
# IA MODEL + CONTENT GENERATOR
# ---------------------------------------------------------------------
def get_ai_components():
    """Inicializa IA model + ContentGenerator SOLO una vez y las retorna."""
    global _ai_model_instance, _generator_instance

    if _ai_model_instance is None:
        provider = app.config.get("API_PROVIDER", "groq")
        model_name = app.config.get("API_MODEL_NAME", None)

        # Selección de API key por provider
        api_key = None
        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY") or app.config.get("GROQ_API_KEY")
        elif provider == "huggingface":
            api_key = os.getenv("HUGGINGFACE_API_KEY") or app.config.get("HUGGINGFACE_API_KEY")
        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY") or app.config.get("GEMINI_API_KEY")

        if not api_key:
            logger.error(f"[FATAL] API KEY para provider '{provider}' no encontrada.")
            raise RuntimeError(f"API KEY requerida para provider {provider}")

        # Inicializar wrapper del modelo
        _ai_model_instance = APIModel(provider=provider, model_name=model_name, api_key=api_key)
        _generator_instance = ContentGenerator(_ai_model_instance, text_processor)

        logger.info(f"IA Model cargado: provider={provider} | model={model_name}")

    return _ai_model_instance, _generator_instance


# ---------------------------------------------------------------------
# RAG SERVICE (singleton)
# ---------------------------------------------------------------------
def get_rag():
    """Carga el RAGService una sola vez, con manejo de error sólido."""
    global _rag_instance
    if _rag_instance is None:
        try:
            _rag_instance = get_rag_instance()
            logger.info("RAGService inicializado correctamente.")
        except Exception as e:
            logger.error(f"[ERROR] Al inicializar RAGService: {e}")
            _rag_instance = None
    return _rag_instance


# ---------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------
@app.route("/")
def index():
    # Si tienes un index.html en templates, se servirá; si no, devuelve un simple mensaje
    try:
        return render_template("index.html")
    except Exception:
        return "<h1>ARB-BOT</h1><p>API disponible en /api/health</p>"


@app.route("/api/health", methods=["GET"])
def health():
    """Diagnóstico de salud básica del servicio."""
    rag = get_rag()
    return jsonify({
        "status": "healthy",
        "service": "ARB-BOT",
        "timestamp": datetime.utcnow().isoformat(),
        "rag_loaded": rag is not None
    })


@app.route("/api/generate", methods=["POST"])
def generate_content():
    """
    Endpoint PRO para generación:
      1. Validación estricta del input
      2. Limpieza con TextProcessor
      3. Búsqueda contextual con RAG
      4. Generación segura (Modo D aplicado en generator.py)
      5. Guardado de interacción con latencia real
    """
    start_time = time.time()
    try:
        payload = request.get_json(force=True)
        if not payload or "input" not in payload:
            return jsonify({"status": "error", "message": "Input requerido"}), 400

        user_input = str(payload["input"]).strip()
        if not user_input:
            return jsonify({"status": "error", "message": "Input vacío"}), 400

        # Validación de longitud
        min_len = int(app.config.get("MIN_INPUT_LENGTH", 3))
        max_len = int(app.config.get("MAX_INPUT_LENGTH", 8000))
        if len(user_input) < min_len:
            return jsonify({"status": "error", "message": f"Input muy corto. Mínimo {min_len} chars"}), 400
        if len(user_input) > max_len:
            return jsonify({"status": "error", "message": f"Input muy largo. Máximo {max_len} chars"}), 400

        logger.info(f"Pregunta recibida ({len(user_input)} chars)")

        # 1) Procesar input
        processed_input = text_processor.process(user_input)

        # 2) Obtener contexto RAG (si existe)
        rag = get_rag()
        context = ""
        context_metadata = None
        rag_docs_count = 0
        if rag:
            try:
                stats = rag.get_stats() or {}
                rag_docs_count = int(stats.get("total_documents", 0) or 0)
                if rag_docs_count > 0:
                    # Top_k y max_context_length pueden ajustarse en config
                    top_k = int(app.config.get("RAG_TOP_K", 6))
                    max_ctx = int(app.config.get("RAG_MAX_CONTEXT_LENGTH", 6000))
                    result = rag.get_context_with_metadata(processed_input, top_k=top_k, max_context_length=max_ctx)
                    context = result.get("context", "")
                    context_metadata = result.get("metadata")
                    logger.info(f"Contexto obtenido: {len(context)} chars (top_k={top_k})")
            except Exception as e:
                logger.warning(f"Error consultando RAG: {e}")
                context = ""

        # 3) Generación (usa generator MODO D si está implementado)
        ia_model, generator = get_ai_components()
        generated = generator.generate(
            processed_input,
            max_tokens=int(app.config.get("MAX_TOKENS", 512)),
            temperature=float(app.config.get("TEMPERATURE", 0.2)),
            context=context if context else None,
            metadata=context_metadata
        )

        # 4) Guardar interacción (no crítico)
        latency = round(time.time() - start_time, 4)
        try:
            save_interaction(
                user_input=user_input,
                generated_output=generated,
                model_used=f"{ia_model.provider}-{ia_model.model_name}",
                processing_time=latency,
                metadata={"context_used": bool(context), "rag_total_docs": rag_docs_count}
            )
        except Exception as e:
            logger.debug(f"save_interaction falló: {e}")

        # 5) Responder
        return jsonify({
            "status": "success",
            "input": user_input,
            "processed_input": processed_input,
            "generated_content": generated,
            "context_used": bool(context),
            "rag_total_docs": rag_docs_count,
            "latency_seconds": latency
        }), 200

    except Exception as e:
        logger.exception("ERROR en /api/generate")
        return jsonify({
            "status": "error",
            "message": "Error interno en el servidor",
            "details": str(e)
        }), 500


@app.route("/api/search-documents", methods=["POST"])
def search_documents():
    """Buscar chunks en RAG y devolverlos (útil para debug/admin)."""
    try:
        data = request.get_json(force=True)
        if not data or "query" not in data:
            return jsonify({"status": "error", "message": "Query requerida"}), 400

        query = str(data["query"])
        top_k = int(data.get("top_k", 5))
        rag = get_rag()
        if not rag:
            return jsonify({"status": "error", "message": "RAG no disponible"}), 503

        results = rag.search_similar_chunks(query, top_k=top_k)
        return jsonify({
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }), 200

    except Exception as e:
        logger.exception("Error en /api/search-documents")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rag-stats", methods=["GET"])
def rag_stats():
    """Devolver estadísticas básicas del RAG."""
    try:
        rag = get_rag()
        if not rag:
            return jsonify({"status": "error", "message": "RAG no cargado"}), 503
        stats = rag.get_stats() or {}
        return jsonify({"status": "success", "stats": stats}), 200
    except Exception as e:
        logger.exception("Error en /api/rag-stats")
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------------------------------------------------------------
# START SERVER
# ---------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("ARB-BOT iniciando (PRO)...")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
