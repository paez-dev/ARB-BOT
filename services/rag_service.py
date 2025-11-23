"""
ARB-BOT - Servicio RAG (Retrieval Augmented Generation)
Sistema de búsqueda y recuperación de información de documentos
Usa LlamaIndex con Supabase pgvector para persistencia
"""

import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class RAGService:
    """
    Servicio RAG para buscar información relevante en documentos
    Usa LlamaIndex con Supabase pgvector (100% gratuito, persistente)
    """
    
    def __init__(self, embeddings_model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Inicializar servicio RAG con LlamaIndex y Supabase
        
        Args:
            embeddings_model: Modelo de embeddings (gratuito de sentence-transformers)
        """
        self.embeddings_model_name = embeddings_model
        self.vector_store = None
        self.index = None
        self.query_engine = None
        self._initialize_llamaindex()
    
    def _initialize_llamaindex(self):
        """Inicializar LlamaIndex con Supabase como vector store"""
        try:
            from llama_index.core import VectorStoreIndex, StorageContext
            from llama_index.core.settings import Settings
            from llama_index.vector_stores.supabase import SupabaseVectorStore
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            import os
            
            # Obtener configuración de Supabase
            supabase_url = os.getenv('SUPABASE_URL', '')
            supabase_key = os.getenv('SUPABASE_KEY', '')
            supabase_db_url = os.getenv('SUPABASE_DB_URL', '')
            
            if not supabase_url or not supabase_key:
                logger.warning("⚠️ SUPABASE_URL o SUPABASE_KEY no configurados. Usando almacenamiento en memoria.")
                # Fallback a almacenamiento en memoria
                self._initialize_in_memory()
                return
            
            # Si SUPABASE_DB_URL está configurada, codificar el password si tiene caracteres especiales
            if supabase_db_url:
                # Verificar si el password necesita codificación (tiene caracteres especiales sin codificar)
                # Formato: postgresql://postgres:PASSWORD@host:port/db
                if '@' in supabase_db_url and '://' in supabase_db_url:
                    try:
                        from urllib.parse import urlparse, urlunparse, quote
                        parsed = urlparse(supabase_db_url)
                        # Si el password tiene caracteres especiales sin codificar, codificarlo
                        if parsed.password and ('$' in parsed.password or '@' in parsed.password or '#' in parsed.password):
                            # Reconstruir URL con password codificado
                            encoded_password = quote(parsed.password, safe='')
                            # Reconstruir netloc con password codificado
                            netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
                            if parsed.port:
                                netloc += f":{parsed.port}"
                            # Reconstruir URL completa
                            supabase_db_url = urlunparse((
                                parsed.scheme,
                                netloc,
                                parsed.path,
                                parsed.params,
                                parsed.query,
                                parsed.fragment
                            ))
                            logger.info("🔐 Password codificado automáticamente en SUPABASE_DB_URL")
                    except Exception as encode_error:
                        logger.warning(f"⚠️ No se pudo codificar password automáticamente: {encode_error}")
                        logger.warning("💡 Si tu password tiene caracteres especiales ($, @, #), codifícalos manualmente en la URL")
            
            if not supabase_db_url:
                # Intentar construir la connection string desde SUPABASE_URL
                # Formato: postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
                # Necesitamos extraer el host de SUPABASE_URL
                logger.warning("⚠️ SUPABASE_DB_URL no configurado. Intentando construir desde SUPABASE_URL...")
                # Extraer host de SUPABASE_URL (ej: https://xxxxx.supabase.co -> xxxxx.supabase.co)
                if 'supabase.co' in supabase_url:
                    host = supabase_url.replace('https://', '').replace('http://', '').split('/')[0]
                    logger.info(f"📋 Host extraído: {host}")
                    # Necesitamos la contraseña de la base de datos
                    db_password = os.getenv('SUPABASE_DB_PASSWORD', '')
                    if db_password:
                        # Codificar password para URL (manejar caracteres especiales como $, @, etc.)
                        from urllib.parse import quote_plus
                        password_encoded = quote_plus(db_password)
                        # Construir connection string
                        supabase_db_url = f"postgresql://postgres:{password_encoded}@db.{host}:5432/postgres"
                        logger.info(f"🔗 Connection string construida: postgresql://postgres:***@db.{host}:5432/postgres")
                    else:
                        logger.error("❌ Se necesita SUPABASE_DB_URL o SUPABASE_DB_PASSWORD para conectar a PostgreSQL")
                        logger.error("💡 Configura SUPABASE_DB_PASSWORD en Railway con tu password de base de datos")
                        self._initialize_in_memory()
                        return
                else:
                    logger.error(f"❌ No se pudo construir SUPABASE_DB_URL desde SUPABASE_URL: {supabase_url}")
                    self._initialize_in_memory()
                    return
            else:
                # Log parcial de la connection string (ocultar password)
                safe_url = supabase_db_url.split('@')[1] if '@' in supabase_db_url else '***'
                logger.info(f"🔗 Usando SUPABASE_DB_URL: postgresql://postgres:***@{safe_url}")
            
            logger.info("🔧 Inicializando LlamaIndex con Supabase pgvector...")
            
            # Configurar embeddings (nueva API de LlamaIndex 0.10.0)
            embed_model = HuggingFaceEmbedding(
                model_name=self.embeddings_model_name
            )
            Settings.embed_model = embed_model
            
            # Crear vector store de Supabase
            # Nota: collection_name y table_name deben ser consistentes
            # LlamaIndex usa collection_name para crear la tabla en el schema 'vecs'
            self.vector_store = SupabaseVectorStore(
                postgres_connection_string=supabase_db_url,
                collection_name="arbot_documents",  # Este es el nombre que usa para la tabla
                table_name="arbot_documents"  # Asegurar consistencia
            )
            
            # Crear storage context
            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            
            # Crear o cargar índice
            try:
                # Intentar cargar índice existente
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=storage_context
                )
                logger.info("✅ Índice cargado desde Supabase")
            except Exception as load_error:
                # Si no existe, crear uno nuevo
                logger.info(f"ℹ️ No se encontró índice existente en Supabase, se creará uno nuevo: {load_error}")
                self.index = VectorStoreIndex(
                    nodes=[],
                    storage_context=storage_context
                )
                logger.info("✅ Nuevo índice creado en Supabase")
            
            # No crear query engine (requiere LLM), usaremos retriever directamente en search()
            self.query_engine = None
            
            logger.info("✅ LlamaIndex inicializado correctamente con Supabase")
            
        except ImportError as e:
            logger.error(f"❌ Error importando LlamaIndex: {e}")
            logger.error("💡 Instala: pip install llama-index-vector-stores-supabase llama-index-embeddings-huggingface")
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error inicializando LlamaIndex con Supabase: {error_msg}")
            
            # Mensajes de ayuda según el tipo de error
            if "Network is unreachable" in error_msg or "connection" in error_msg.lower():
                logger.error("💡 Posibles causas:")
                logger.error("   1. La connection string está mal formada")
                logger.error("   2. El password de la base de datos es incorrecto")
                logger.error("   3. Supabase tiene restricciones de red (verifica Network Restrictions)")
                logger.error("   4. El host 'db.xxxxx.supabase.co' no es accesible desde Railway")
                logger.error("💡 Solución: Verifica SUPABASE_DB_URL o SUPABASE_DB_PASSWORD en Railway")
            elif "authentication failed" in error_msg.lower() or "password" in error_msg.lower():
                logger.error("💡 Error de autenticación:")
                logger.error("   1. Verifica que SUPABASE_DB_PASSWORD sea correcto")
                logger.error("   2. Puedes resetear el password en Supabase → Settings → Database")
            elif "does not exist" in error_msg.lower() or "extension" in error_msg.lower():
                logger.error("💡 Error de base de datos:")
                logger.error("   1. Verifica que pgvector esté habilitado en Supabase")
                logger.error("   2. Ejecuta: CREATE EXTENSION IF NOT EXISTS vector;")
            
            logger.warning("⚠️ Fallback a almacenamiento en memoria...")
            self._initialize_in_memory()
    
    def _initialize_in_memory(self):
        """Inicializar LlamaIndex en memoria (fallback)"""
        try:
            from llama_index.core import VectorStoreIndex, StorageContext
            from llama_index.core.settings import Settings
            from llama_index.core.vector_stores import SimpleVectorStore
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            
            logger.info("🔧 Inicializando LlamaIndex en memoria (fallback)...")
            
            # Configurar embeddings (nueva API de LlamaIndex 0.10.0)
            embed_model = HuggingFaceEmbedding(
                model_name=self.embeddings_model_name
            )
            Settings.embed_model = embed_model
            
            # Crear vector store simple en memoria
            vector_store = SimpleVectorStore()
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Crear índice vacío
            self.index = VectorStoreIndex(
                nodes=[],
                storage_context=storage_context
            )
            
            # No crear query engine (requiere LLM), usaremos retriever directamente en search()
            self.query_engine = None
            
            self.vector_store = vector_store
            logger.info("✅ LlamaIndex inicializado en memoria (sin persistencia)")
            
        except ImportError as import_error:
            # Si SimpleVectorStore no está disponible, intentar sin vector store
            logger.warning(f"⚠️ SimpleVectorStore no disponible ({import_error}), creando índice sin vector store...")
            try:
                from llama_index.core import VectorStoreIndex
                from llama_index.core.settings import Settings
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                
                embed_model = HuggingFaceEmbedding(
                    model_name=self.embeddings_model_name
                )
                Settings.embed_model = embed_model
                
                # Crear índice sin vector store (solo en memoria)
                self.index = VectorStoreIndex(nodes=[])
                # No crear query engine (requiere LLM), usaremos retriever directamente
                self.query_engine = None
                self.vector_store = None
                logger.info("✅ LlamaIndex inicializado en memoria (sin vector store)")
            except Exception as e2:
                logger.error(f"❌ Error en fallback alternativo: {e2}")
                raise
        except Exception as e:
            logger.error(f"❌ Error en fallback a memoria: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict]):
        """
        Agregar documentos al sistema RAG usando LlamaIndex
        
        Args:
            chunks: Lista de chunks de documentos
        """
        try:
            if not chunks:
                logger.warning("No hay chunks para agregar")
                return
            
            logger.info(f"📄 Agregando {len(chunks)} chunks al sistema RAG con LlamaIndex...")
            
            from llama_index.core import Document
            
            # Convertir chunks a documentos de LlamaIndex
            documents = []
            for chunk in chunks:
                doc = Document(
                    text=chunk.get('text', ''),
                    metadata={
                        'source': chunk.get('source', 'unknown'),
                        'chunk_id': chunk.get('id', 0),
                        'chunk_index': chunk.get('chunk_index', 0),
                        'article': chunk.get('article', None)
                    }
                )
                documents.append(doc)
            
            # Agregar documentos al índice usando el método correcto de LlamaIndex
            # LlamaIndex inserta documentos uno por uno, pero podemos optimizar
            import time
            start_time = time.time()
            
            try:
                # LlamaIndex inserta documentos individualmente
                # El método insert() es el correcto para VectorStoreIndex
                inserted_count = 0
                for idx, doc in enumerate(documents):
                    try:
                        self.index.insert(doc)
                        inserted_count += 1
                    except Exception as insert_error:
                        logger.warning(f"⚠️ Error insertando documento {idx + 1}/{len(documents)}: {insert_error}. Continuando...")
                        continue
                
                elapsed = time.time() - start_time
                logger.info(f"✅ {inserted_count}/{len(documents)} documentos agregados al índice de LlamaIndex (Tiempo: {elapsed:.1f}s)")
                
                # Refrescar el índice para asegurar que los cambios se reflejen
                # Esto es importante para que las búsquedas encuentren los nuevos documentos
                try:
                    # Forzar actualización del índice
                    if hasattr(self.index, 'refresh'):
                        self.index.refresh()
                    elif hasattr(self.index, '_refresh'):
                        self.index._refresh()
                except Exception as refresh_error:
                    logger.debug(f"⚠️ No se pudo refrescar índice (puede ser normal): {refresh_error}")
                
                if elapsed > 30:
                    logger.warning(f"⚠️ Inserción lenta: {elapsed:.1f}s para {inserted_count} documentos. Esto es normal para Supabase.")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Error agregando documentos: {error_msg}")
                elapsed = time.time() - start_time
                logger.error(f"   Tiempo transcurrido: {elapsed:.1f}s")
                raise
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error agregando documentos: {error_msg}")
            
            # Detectar error de dimensiones específico
            if "expected" in error_msg and "dimensions" in error_msg and "not" in error_msg:
                logger.error("🔴 ERROR DE DIMENSIONES DETECTADO")
                logger.error("💡 La tabla en Supabase tiene dimensiones incorrectas")
                logger.error("💡 Solución:")
                logger.error("   1. Ve a Supabase → SQL Editor")
                logger.error("   2. Ejecuta: DROP TABLE IF EXISTS vecs.arbot_documents CASCADE;")
                logger.error("   3. Ejecuta: DROP TABLE IF EXISTS vecs.arbot_vectors CASCADE;")
                logger.error("   4. Reinicia la aplicación")
                logger.error("   5. Vuelve a subir el documento")
                logger.error("📖 Ver CORREGIR_DIMENSIONES_VECTORES.md para más detalles")
            
            raise
    
    def _search_direct_supabase(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Búsqueda directa en Supabase cuando LlamaIndex falla
        Hace búsqueda vectorial directamente usando embeddings
        """
        try:
            import psycopg2
            from sentence_transformers import SentenceTransformer
            from urllib.parse import quote_plus
            
            logger.info(f"🔍 Búsqueda directa en Supabase para: '{query}'")
            
            # Generar embedding de la query
            embedder = SentenceTransformer(self.embeddings_model_name)
            query_embedding = embedder.encode(query, show_progress_bar=False)
            query_embedding_str = '[' + ','.join(map(str, query_embedding.tolist())) + ']'
            
            # Obtener conexión desde variable de entorno (más confiable)
            supabase_db_url = os.getenv('SUPABASE_DB_URL')
            if not supabase_db_url:
                # Intentar desde vector_store como fallback
                if self.vector_store and hasattr(self.vector_store, 'postgres_connection_string'):
                    conn_str = self.vector_store.postgres_connection_string
                else:
                    logger.error("❌ No hay conexión a Supabase disponible (SUPABASE_DB_URL no configurada)")
                    return []
            else:
                conn_str = supabase_db_url
            conn = psycopg2.connect(conn_str)
            cursor = conn.cursor()
            
            # Detectar columnas
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'vecs' 
                AND table_name = 'arbot_documents'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            has_vec = 'vec' in columns
            embedding_col = 'vec' if has_vec else 'embedding'
            
            # Búsqueda vectorial usando cosine distance
            # Prioridad: document column (estructura correcta) > metadata->text > metadata->document
            cursor.execute(f"""
                SELECT 
                    id,
                    {embedding_col} <=> %s::vector as distance,
                    COALESCE(document, '') as doc_text,
                    metadata->>'text' as text_from_meta,
                    metadata->>'document' as doc_from_meta,
                    metadata
                FROM vecs.arbot_documents
                WHERE document IS NOT NULL AND document != ''
                ORDER BY {embedding_col} <=> %s::vector
                LIMIT %s;
            """, (query_embedding_str, query_embedding_str, top_k))
            
            results = []
            for row in cursor.fetchall():
                node_id, distance, doc_text, text_from_meta, doc_from_meta, metadata = row
                
                # Obtener texto (prioridad: document column > metadata->text > metadata->document)
                node_text = doc_text or text_from_meta or doc_from_meta
                
                if not node_text:
                    logger.warning(f"⚠️ Nodo {node_id} sin texto recuperable")
                    continue
                
                # Convertir distancia a similitud (1 - distancia)
                similarity = max(0.0, 1.0 - float(distance)) if distance is not None else 0.5
                
                result = {
                    'text': node_text,
                    'source': metadata.get('file_name', 'unknown') if metadata else 'unknown',
                    'similarity': similarity,
                    'rank': len(results) + 1,
                    'metadata': metadata if metadata else {}
                }
                results.append(result)
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Búsqueda directa completada: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda directa Supabase: {e}")
            return []
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Buscar documentos relevantes usando LlamaIndex
        
        Args:
            query: Pregunta o consulta del usuario
            top_k: Número de resultados a retornar
        
        Returns:
            Lista de chunks relevantes con scores
        """
        try:
            if self.index is None:
                logger.warning("No hay índice disponible en el sistema RAG")
                return []
            
            # Intentar buscar siempre - no confiar completamente en get_stats()
            # Si hay documentos en Supabase, la búsqueda los encontrará aunque get_stats() falle
            try:
                stats = self.get_stats()
                total_docs = stats.get('total_documents', 0)
                if isinstance(total_docs, str):
                    total_docs = 0
                if total_docs > 0:
                    logger.debug(f"📊 get_stats() reporta {total_docs} documentos")
                else:
                    logger.debug("📊 get_stats() reporta 0 documentos, pero intentando búsqueda de todas formas (puede haber documentos aunque get_stats() falle)")
            except Exception as stats_error:
                logger.debug(f"⚠️ No se pudo verificar estadísticas: {stats_error}, pero intentando búsqueda de todas formas...")
            
            # Usar retriever directamente en lugar de query engine (no requiere LLM)
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            
            # Realizar búsqueda
            logger.info(f"🔍 Buscando: '{query}' (top_k={top_k})")
            try:
                nodes = retriever.retrieve(query)
                logger.info(f"🔍 LlamaIndex retornó {len(nodes)} nodos")
                
                # Verificar si los nodos tienen texto válido
                nodes_with_text = [n for n in nodes if hasattr(n, 'text') and n.text]
                if len(nodes_with_text) < len(nodes):
                    logger.warning(f"⚠️ {len(nodes) - len(nodes_with_text)} nodos sin texto, usando búsqueda directa en Supabase...")
                    return self._search_direct_supabase(query, top_k)
                    
            except Exception as retrieve_error:
                error_msg = str(retrieve_error)
                logger.error(f"❌ Error en búsqueda RAG: {error_msg}")
                
                # Si el error es sobre TextNode con text=None, intentar recuperar desde Supabase directamente
                if ("TextNode" in error_msg and "none is not an allowed value" in error_msg.lower()) or \
                   ("text" in error_msg.lower() and "none" in error_msg.lower()):
                    logger.warning("⚠️ LlamaIndex retornó nodos con text=None, intentando búsqueda directa en Supabase...")
                    # Hacer búsqueda directa en Supabase usando embeddings
                    return self._search_direct_supabase(query, top_k)
                else:
                    # Para otros errores, también intentar búsqueda directa como fallback
                    logger.warning("⚠️ Error en LlamaIndex, intentando búsqueda directa en Supabase como fallback...")
                    return self._search_direct_supabase(query, top_k)
            
            # Extraer resultados
                results = []
            for i, node in enumerate(nodes[:top_k]):
                # Convertir score a float de forma segura
                try:
                    if hasattr(node, 'score') and node.score is not None:
                        similarity = float(node.score) if not isinstance(node.score, str) else 0.8
                    else:
                        similarity = 0.8
                except (ValueError, TypeError):
                    similarity = 0.8
                
                # Obtener texto del nodo - PRIORIDAD: metadata primero, luego Supabase directo
                node_text = None
                
                # 1. Intentar desde node.text (puede ser None si no hay columna document)
                if hasattr(node, 'text') and node.text:
                    node_text = node.text
                    logger.debug(f"✅ Texto obtenido desde node.text")
                
                # 2. Intentar desde metadata del nodo
                if not node_text and hasattr(node, 'metadata') and node.metadata:
                    node_text = node.metadata.get('text') or node.metadata.get('document')
                    if node_text:
                        logger.debug(f"✅ Texto obtenido desde node.metadata")
                
                # 3. Si aún no hay texto, consultar directamente a Supabase usando el id del nodo
                if not node_text:
                    try:
                        import psycopg2
                        # Obtener node_id del nodo - LlamaIndex puede usar diferentes atributos
                        node_id = None
                        if hasattr(node, 'node_id'):
                            node_id = node.node_id
                        elif hasattr(node, 'id_'):
                            node_id = node.id_
                        elif hasattr(node, 'id'):
                            node_id = node.id
                        elif hasattr(node, 'ref_doc_id'):
                            node_id = node.ref_doc_id
                        elif hasattr(node, 'metadata') and node.metadata:
                            # Intentar obtener id desde metadata
                            node_id = node.metadata.get('id') or node.metadata.get('chunk_id') or node.metadata.get('_node_id')
                        
                        # Si tenemos un ID, consultar Supabase
                        if node_id and self.vector_store and hasattr(self.vector_store, 'postgres_connection_string'):
                            conn_str = self.vector_store.postgres_connection_string
                            try:
                                conn = psycopg2.connect(conn_str)
                                cursor = conn.cursor()
                                # Obtener texto desde la columna document (estructura correcta)
                                cursor.execute("""
                                    SELECT document
                                    FROM vecs.arbot_documents
                                    WHERE id = %s;
                                """, (str(node_id),))
                                result = cursor.fetchone()
                                if result and result[0]:
                                    node_text = result[0]
                                    logger.info(f"✅ Texto recuperado desde Supabase para nodo {node_id} ({len(node_text)} caracteres)")
            else:
                                    logger.warning(f"⚠️ Nodo {node_id} no encontrado o sin texto en columna document")
                                cursor.close()
                                conn.close()
                            except Exception as conn_error:
                                logger.warning(f"⚠️ Error conectando a Supabase para obtener texto: {conn_error}")
                    except Exception as db_error:
                        logger.warning(f"⚠️ No se pudo obtener texto desde Supabase: {db_error}")
                
                # 4. Si aún no hay texto, usar un fallback
                if not node_text:
                    node_text = node.metadata.get('file_name', 'Documento sin texto') if hasattr(node, 'metadata') and node.metadata else 'Sin texto disponible'
                    logger.warning(f"⚠️ Nodo sin texto recuperable, usando fallback: {node_text[:50]}...")
                
                result = {
                    'text': node_text,
                    'source': node.metadata.get('source', node.metadata.get('file_name', 'unknown')) if hasattr(node, 'metadata') and node.metadata else 'unknown',
                    'similarity': similarity,
                    'rank': i + 1,
                    'metadata': node.metadata if hasattr(node, 'metadata') and node.metadata else {}
                }
                    results.append(result)
            
            # Ordenar por similitud (de mayor a menor) de forma segura
            try:
                results.sort(key=lambda x: x['similarity'], reverse=True)
            except (TypeError, ValueError) as sort_error:
                logger.warning(f"⚠️ No se pudo ordenar resultados por similitud: {sort_error}. Usando orden original.")
            
            logger.info(f"🔍 Búsqueda completada: {len(results)} resultados encontrados")
            if results:
                logger.info(f"   Mejor match: similitud={results[0]['similarity']:.2f}, preview={results[0]['text'][:100]}...")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda RAG: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, top_k: int = 10, max_context_length: int = 2500) -> str:
        """
        Obtener contexto relevante para una consulta
        
        Args:
            query: Pregunta del usuario
            top_k: Número de chunks a recuperar
            max_context_length: Longitud máxima del contexto
        
        Returns:
            Contexto formateado
        """
        try:
            results = self.search(query, top_k=top_k)
        
        if not results:
                logger.warning("No se encontraron resultados relevantes")
            return ""
        
            # Construir contexto desde los resultados
        context_parts = []
            current_length = 0
            
            # Asegurar que max_context_length sea int
            max_context_length = int(max_context_length) if max_context_length else 2500
            
        for result in results:
                # Asegurar que text sea string
                text = str(result.get('text', ''))
                if not text:
                    continue
                
                # Limitar longitud de cada chunk individual
                if len(text) > 800:
                    text = text[:800] + "..."
                
                # Asegurar que todas las comparaciones sean con int
                text_len = int(len(text))
                if current_length + text_len > max_context_length:
                    break
                
                context_parts.append(text)
                current_length += text_len
            
            full_context = " ".join(context_parts)
            
            # Truncar si es necesario
            if len(full_context) > max_context_length:
                full_context = full_context[:max_context_length]
                # Truncar en un punto completo si es posible
                last_period = full_context.rfind('.')
                if last_period > max_context_length * 0.8:
                    full_context = full_context[:last_period + 1]
            
            logger.info(f"✅ Contexto final completo: {len(full_context)} caracteres")
            if len(full_context) == 0:
                logger.warning("⚠️ Contexto vacío - el modelo no tendrá información del manual")
            
            return full_context
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo contexto: {str(e)}")
            return ""
    
    def get_stats(self) -> Dict:
        """
        Obtener estadísticas del sistema RAG
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            if self.index is None:
                return {
                    'total_documents': 0,
                    'embeddings_model': self.embeddings_model_name,
                    'vector_store': 'none'
                }
            
            # Obtener número de documentos desde Supabase directamente
            total_docs = 0
            try:
                if self.vector_store and hasattr(self.vector_store, 'postgres_connection_string'):
                    import psycopg2
                    conn_str = self.vector_store.postgres_connection_string
                    
                    try:
                        conn = psycopg2.connect(conn_str)
                        cursor = conn.cursor()
                        
                        # Consultar tabla de vectores (LlamaIndex usa esta tabla)
                        cursor.execute("SELECT COUNT(*) FROM vecs.arbot_documents;")
                        result = cursor.fetchone()
                        total_docs = result[0] if result else 0
                        
                        cursor.close()
                        conn.close()
                        
                        logger.info(f"📊 Documentos en Supabase: {total_docs}")
                    except Exception as db_error:
                        logger.error(f"❌ Error consultando Supabase para stats: {db_error}")
                        logger.error(f"   Connection string: {conn_str[:50]}...")
                        # Fallback: intentar desde el índice
                        try:
                            if hasattr(self.index, '_vector_store'):
                                total_docs = getattr(self.index._vector_store, '_collection_size', 0)
                                logger.debug(f"   Fallback desde índice: {total_docs}")
                        except:
                            total_docs = 0
                elif hasattr(self.index, '_vector_store'):
                    # Fallback para otros tipos de vector store
                    if hasattr(self.index._vector_store, '_data'):
                        total_docs = len(self.index._vector_store._data.get('embeddings_dict', {}))
                    else:
                        total_docs = getattr(self.index._vector_store, '_collection_size', 0)
            except Exception as count_error:
                logger.debug(f"⚠️ No se pudo contar documentos: {count_error}")
                total_docs = 0
            
            # Determinar tipo de vector store
            vector_store_type = 'memory'
            if self.vector_store is not None:
                store_type_str = str(type(self.vector_store))
                if 'Supabase' in store_type_str:
                    vector_store_type = 'supabase'
                elif 'Simple' in store_type_str:
                    vector_store_type = 'memory'
            
            # Asegurar que total_docs sea un número entero
            if isinstance(total_docs, str):
                total_docs = 0
            total_docs = int(total_docs) if total_docs else 0
            
            return {
                'total_documents': total_docs,
                'embeddings_model': self.embeddings_model_name,
                'vector_store': vector_store_type
            }
        except Exception as e:
            logger.error(f"Error obteniendo stats: {str(e)}")
        return {
                'total_documents': 0,
            'embeddings_model': self.embeddings_model_name,
                'vector_store': 'unknown',
                'error': str(e)
            }
    
    def save_index(self, filepath: str):
        """
        Guardar índice (ya no necesario con Supabase, pero mantenido para compatibilidad)
        """
        logger.info("ℹ️ Con Supabase pgvector, el índice se guarda automáticamente. No se requiere guardar manualmente.")
        pass
    
    def load_index(self, filepath: str):
        """
        Cargar índice (ya no necesario con Supabase, pero mantenido para compatibilidad)
        """
        logger.info("ℹ️ Con Supabase pgvector, el índice se carga automáticamente al inicializar.")
        pass

        pass
