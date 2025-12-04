"""
ARB-BOT - Servicio RAG Profesional
Optimizado para Railway, Supabase pgvector y modelo MiniLM-L12-V2.
Incluye caching, singleton real y uso eficiente de RAM.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer

# ============================================================
# LOGGING
# ============================================================
logger = logging.getLogger("services.rag_service")
logger.setLevel(logging.INFO)


# ============================================================
# SINGLETON PARA EL MODELO DE EMBEDDINGS
# ============================================================
class EmbeddingsSingleton:
    _model = None

    @staticmethod
    def get_model():
        """Carga el modelo UNA sola vez en toda la app."""
        if EmbeddingsSingleton._model is None:
            model_name = os.getenv(
                "EMBEDDINGS_MODEL",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            logger.info(f"🧠 Cargando modelo de embeddings: {model_name}")
            EmbeddingsSingleton._model = SentenceTransformer(model_name)
        return EmbeddingsSingleton._model


# Dimensión del modelo MiniLM-L12-v2 = 384
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "384"))

DEFAULT_SCHEMA = "vecs"
DEFAULT_TABLE = "arbot_documents"


# ============================================================
# RAG SERVICE
# ============================================================
class RAGService:
    """Servicio profesional RAG conectado a Supabase con pgvector."""

    def __init__(self):
        logger.info("🚀 Inicializando RAGService…")

        # --------------------------
        # VARIABLES DE ENTORNO
        # --------------------------
        self.db_url = os.getenv("SUPABASE_DB_URL")
        if not self.db_url:
            raise RuntimeError("SUPABASE_DB_URL requerido para RAG.")

        self.schema = os.getenv("SCHEMA", DEFAULT_SCHEMA)
        self.table = os.getenv("TABLE", DEFAULT_TABLE)
        self.vector_dim = VECTOR_DIM

        # --------------------------
        # CONEXIÓN BD
        # --------------------------
        self.conn = self._connect_db()
        self._ensure_table()
        self._log_stats()

        # Modelo NO se carga aquí → lazy load con Singleton
        logger.info("🟩 RAGService listo.")

    # ==========================================================
    # BASE DE DATOS
    # ==========================================================
    def _connect_db(self):
        try:
            conn = psycopg2.connect(self.db_url)
            conn.autocommit = True
            logger.info("🔗 Conectado a Supabase Postgres.")
            return conn
        except Exception as e:
            logger.error("❌ Error conectando a Supabase.")
            raise e

    def _ensure_table(self):
        """Valida que la tabla tenga columnas text + vec."""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s;
                """, (self.schema, self.table))

                cols = {row["column_name"] for row in cur.fetchall()}

                if "text" not in cols or "vec" not in cols:
                    raise RuntimeError(
                        f"Tabla {self.schema}.{self.table} inválida. "
                        "Debe tener columnas: text (text), vec (vector)"
                    )
        except Exception:
            logger.exception("❌ Error verificando tabla de RAG.")
            raise

    def _log_stats(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {self.schema}.{self.table}")
                total = cur.fetchone()[0]
                logger.info(f"📚 Documentos cargados: {total}")
        except Exception:
            logger.warning("⚠️ No se pudo obtener stats del RAG.")

    # ==========================================================
    # EMBEDDINGS
    # ==========================================================
    def embed(self, text: str) -> List[float]:
        """Convierte texto → vector usando Singleton (muy bajo RAM)."""
        if not text:
            return []

        try:
            model = EmbeddingsSingleton.get_model()
            emb = model.encode(
                text,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return emb.tolist()
        except Exception as e:
            logger.error(f"❌ Error generando embedding: {e}")
            return []

    def _vec_literal(self, emb: List[float]) -> str:
        """Convierte embedding en literal PostgreSQL pgvector."""
        return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"

    # ==========================================================
    # BÚSQUEDA VECTORIAL
    # ==========================================================
    def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not query:
            return []

        emb = self.embed(query)
        if not emb:
            return []

        vec = self._vec_literal(emb)

        sql = f"""
            SELECT text, metadata, (vec <-> %s::vector) AS distance
            FROM {self.schema}.{self.table}
            ORDER BY distance ASC
            LIMIT %s;
        """

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (vec, top_k))
                rows = cur.fetchall()

            results = []
            for row in rows:
                meta = row["metadata"]
                if isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except:
                        pass

                results.append({
                    "text": row["text"],
                    "metadata": meta,
                    "distance": float(row["distance"]),
                })

            return results

        except Exception:
            logger.exception("❌ Error en búsqueda pgvector.")
            return []

    # ==========================================================
    # CONTEXTO
    # ==========================================================
    def get_context_for_query(self, query: str, top_k: int = 5, max_context_length: int = 3000) -> str:
        """Devuelve contexto concatenado para el modelo."""
        hits = self.search_similar_chunks(query, top_k)
        if not hits:
            return ""

        parts = []
        total = 0

        for hit in hits:
            chunk = hit["text"]
            if not chunk:
                continue

            if total + len(chunk) > max_context_length:
                parts.append(chunk[:max_context_length-total])
                break

            parts.append(chunk)
            total += len(chunk)

        context = "\n\n".join(parts)
        logger.info(f"📎 Contexto generado: {len(context)} chars.")
        return context

    # ==========================================================
    # ESTADÍSTICAS
    # ==========================================================
    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "service": "supabase_pgvector",
            "model": os.getenv("EMBEDDINGS_MODEL"),
            "schema": self.schema,
            "table": self.table,
            "total_documents": 0,
        }

        try:
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {self.schema}.{self.table}")
                stats["total_documents"] = cur.fetchone()[0]
        except:
            pass

        return stats

    def close(self):
        try:
            self.conn.close()
        except:
            pass


# ================================================================
# SINGLETON GLOBAL
# ================================================================
_rag_instance: Optional[RAGService] = None

def get_rag_instance() -> RAGService:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
