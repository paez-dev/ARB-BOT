"""
ARB-BOT - Servicio RAG (Retrieval Augmented Generation)
Sistema de búsqueda y recuperación de información de documentos
Usa LlamaIndex con Supabase pgvector para persistencia
"""

#!/usr/bin/env python3
"""
rag_service.py
Servicio RAG (Supabase pgvector) para ARB-BOT.

Funcionalidades:
- conexión segura a Supabase (via SUPABASE_DB_URL)
- generación de embeddings para queries (Sentence-Transformers)
- búsqueda vectorial eficiente usando ORDER BY vec <-> query_vector
- creación de contexto concatenado
- stats básicos
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("services.rag_service")
logger.setLevel(logging.INFO)

# Default config (override with env vars)
DEFAULT_SCHEMA = "vecs"
DEFAULT_TABLE = "arbot_documents"
EMBEDDING_MODEL = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "384"))


class RAGService:
    def __init__(self):
        logger.info("🚀 Inicializando RAGService...")
        self.db_url = os.getenv("SUPABASE_DB_URL")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.db_url:
            logger.error("SUPABASE_DB_URL no configurado. Revisa variables de entorno.")
            raise RuntimeError("SUPABASE_DB_URL required")

        if not self.supabase_key or not self.supabase_url:
            logger.warning("SUPABASE_URL o SUPABASE_KEY no configurados — la app puede seguir, pero algunas funciones podrían quedar limitadas.")

        self.schema = os.getenv("SCHEMA", DEFAULT_SCHEMA)
        self.table = os.getenv("TABLE", DEFAULT_TABLE)
        self.vector_dim = int(os.getenv("VECTOR_DIM", VECTOR_DIM))

        # Embeddings model (for query embeddings)
        logger.info(f"🧠 Cargando modelo de embeddings: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

        # DB connection
        logger.info("🔗 Conectando a la base de datos (Supabase Postgres)...")
        self.conn = self._connect_db()
        logger.info("🟩 Conectado a Supabase (Postgres).")

        # Quick sanity check
        self._ensure_table_exists()
        self._test_documents_loaded()

    def _connect_db(self):
        try:
            conn = psycopg2.connect(self.db_url)
            conn.autocommit = True
            return conn
        except Exception as e:
            logger.error("🟥 No fue posible conectar a Supabase Postgres.")
            logger.exception(e)
            raise

    def _ensure_table_exists(self):
        """Verifica que la tabla exista y tenga columnas mínimas."""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    """,
                    (self.schema, self.table),
                )
                cols = {r["column_name"]: r["data_type"] for r in cur.fetchall()}
                if "text" not in cols or "vec" not in cols:
                    logger.error(f"La tabla {self.schema}.{self.table} no tiene las columnas esperadas (text, vec). Columnas encontradas: {list(cols.keys())}")
                    raise RuntimeError("Invalid table schema for RAG. Expected columns: text, vec")
        except Exception as e:
            logger.exception("Error verificando esquema de tabla.")
            raise

    def _test_documents_loaded(self):
        """Cuenta documentos para informar estado."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {self.schema}.{self.table}")
                cnt = cur.fetchone()[0]
                if cnt == 0:
                    logger.warning(f"⚠️ Tabla {self.schema}.{self.table} está vacía (0 rows).")
                else:
                    logger.info(f"📚 {cnt} documentos vectores disponibles en {self.schema}.{self.table}")
        except Exception as e:
            logger.warning("No se pudo contar documentos (continuando).")
            logger.debug(e)

    def embed_text(self, text: str) -> List[float]:
        """Genera embedding (lista de floats) para un texto (query)."""
        if not text:
            return []
        arr = self.embedding_model.encode([text], show_progress_bar=False, convert_to_numpy=False)
        # arr is list of numpy arrays if convert_to_numpy=False; ensure list[float]
        emb = list(map(float, arr[0])) if hasattr(arr[0], "__iter__") else [float(arr[0])]
        if len(emb) != self.vector_dim:
            logger.debug(f"Advertencia: embedding generado dim={len(emb)} != VECTOR_DIM={self.vector_dim}")
        return emb

    def _vec_literal(self, emb: List[float]) -> str:
        """Convierte embedding a literal PostgreSQL vector: '[0.1,0.2,...]'"""
        return "[" + ",".join(map(str, emb)) + "]"

    def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca chunks similares en la tabla usando pgvector <-> distance operator.
        Retorna lista de dicts: {text, metadata, distance(optional)}
        """
        if not query or not query.strip():
            return []

        emb = self.embed_text(query)
        if not emb:
            return []

        vec_literal = self._vec_literal(emb)
        sql = f"""
            SELECT text, metadata, (vec <-> %s::vector) AS distance
            FROM {self.schema}.{self.table}
            ORDER BY distance
            LIMIT %s;
        """

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (vec_literal, top_k))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    # metadata puede venir como JSON/str
                    meta = r["metadata"]
                    if isinstance(meta, str):
                        try:
                            meta = json.loads(meta)
                        except Exception:
                            pass
                    results.append({
                        "text": r["text"],
                        "metadata": meta,
                        "distance": float(r.get("distance", 0.0))
                    })
                logger.info(f"🔎 Encontrados {len(results)} chunks (top_k={top_k})")
                return results
        except Exception as e:
            logger.exception("Error en búsqueda vectorial en Supabase.")
            return []

    def get_context_for_query(self, query: str, top_k: int = 5, max_context_length: int = 3000) -> str:
        """
        Devuelve el contexto concatenado (texto) de los mejores chunks.
        max_context_length en caracteres.
        """
        hits = self.search_similar_chunks(query, top_k=top_k)
        if not hits:
            return ""

        context_parts = []
        length = 0
        for h in hits:
            txt = h.get("text", "")
            if not txt:
                continue
            # avoid huge context: truncate each chunk if necessary
            if length + len(txt) > max_context_length:
                # take remaining
                remaining = max_context_length - length
                if remaining > 0:
                    context_parts.append(txt[:remaining])
                    length += remaining
                break
            context_parts.append(txt)
            length += len(txt)

        context = "\n\n".join(context_parts).strip()
        logger.info(f"📎 Context length: {len(context)} chars (from {len(context_parts)} chunks)")
        return context

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas simples sobre la tabla/vector store."""
        stats = {
            "service": "supabase_pgvector",
            "schema": self.schema,
            "table": self.table,
            "total_documents": "unknown",
            "embeddings_model": EMBEDDING_MODEL,
        }
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {self.schema}.{self.table}")
                stats["total_documents"] = int(cur.fetchone()[0])
        except Exception as e:
            logger.warning("No se pudo obtener stats de la tabla.")
            stats["total_documents"] = 0
        return stats

    def close(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass


# Si se importa y se quiere un singleton simple:
_rag_instance: Optional[RAGService] = None


def get_rag_instance() -> RAGService:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance