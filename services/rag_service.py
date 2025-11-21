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
    
    def __init__(self, embeddings_model='paraphrase-multilingual-MiniLM-L12-v2'):
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
            
            if not supabase_db_url:
                # Intentar construir la connection string desde SUPABASE_URL
                # Formato: postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
                # Necesitamos extraer el host de SUPABASE_URL
                logger.warning("⚠️ SUPABASE_DB_URL no configurado. Intentando construir desde SUPABASE_URL...")
                # Extraer host de SUPABASE_URL (ej: https://xxxxx.supabase.co -> xxxxx.supabase.co)
                if 'supabase.co' in supabase_url:
                    host = supabase_url.replace('https://', '').replace('http://', '').split('/')[0]
                    # Necesitamos la contraseña de la base de datos
                    db_password = os.getenv('SUPABASE_DB_PASSWORD', '')
                    if db_password:
                        supabase_db_url = f"postgresql://postgres:{db_password}@db.{host}:5432/postgres"
                    else:
                        logger.error("❌ Se necesita SUPABASE_DB_URL o SUPABASE_DB_PASSWORD para conectar a PostgreSQL")
                        self._initialize_in_memory()
                        return
                else:
                    logger.error("❌ No se pudo construir SUPABASE_DB_URL desde SUPABASE_URL")
                    self._initialize_in_memory()
                    return
            
            logger.info("🔧 Inicializando LlamaIndex con Supabase pgvector...")
            
            # Configurar embeddings (nueva API de LlamaIndex 0.10.0)
            embed_model = HuggingFaceEmbedding(
                model_name=self.embeddings_model_name
            )
            Settings.embed_model = embed_model
            
            # Crear vector store de Supabase
            self.vector_store = SupabaseVectorStore(
                postgres_connection_string=supabase_db_url,
                collection_name="arbot_documents",
                table_name="arbot_vectors"
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
            
            # Crear query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=10,
                response_mode="compact"
            )
            
            logger.info("✅ LlamaIndex inicializado correctamente con Supabase")
            
        except ImportError as e:
            logger.error(f"❌ Error importando LlamaIndex: {e}")
            logger.error("💡 Instala: pip install llama-index-vector-stores-supabase llama-index-embeddings-huggingface")
            raise
        except Exception as e:
            logger.error(f"❌ Error inicializando LlamaIndex con Supabase: {e}")
            logger.warning("⚠️ Fallback a almacenamiento en memoria...")
            self._initialize_in_memory()
    
    def _initialize_in_memory(self):
        """Inicializar LlamaIndex en memoria (fallback)"""
        try:
            from llama_index.core import VectorStoreIndex, StorageContext
            from llama_index.core.settings import Settings
            from llama_index.vector_stores.simple import SimpleVectorStore
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
            
            # Crear query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=10,
                response_mode="compact"
            )
            
            self.vector_store = vector_store
            logger.info("✅ LlamaIndex inicializado en memoria (sin persistencia)")
            
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
            
            # Agregar documentos al índice (LlamaIndex maneja embeddings automáticamente)
            # Usar insert en lugar de add para no recrear el índice completo
            for doc in documents:
                self.index.insert(doc)
            
            logger.info(f"✅ {len(documents)} documentos agregados al índice de LlamaIndex")
            
        except Exception as e:
            logger.error(f"❌ Error agregando documentos: {str(e)}")
            raise
    
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
            if self.index is None or self.query_engine is None:
                logger.warning("No hay índice disponible en el sistema RAG")
                return []
            
            # Actualizar top_k del query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=top_k,
                response_mode="compact"
            )
            
            # Realizar búsqueda
            response = self.query_engine.query(query)
            
            # Extraer resultados de la respuesta
            results = []
            if hasattr(response, 'source_nodes'):
                for i, node in enumerate(response.source_nodes[:top_k]):
                    result = {
                        'text': node.text,
                        'source': node.metadata.get('source', 'unknown'),
                        'similarity': float(node.score) if hasattr(node, 'score') and node.score else 0.8,
                        'rank': i + 1,
                        'metadata': node.metadata
                    }
                    results.append(result)
            
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
            
            for result in results:
                text = result['text']
                # Limitar longitud de cada chunk individual
                if len(text) > 800:
                    text = text[:800] + "..."
                
                if current_length + len(text) > max_context_length:
                    break
                
                context_parts.append(text)
                current_length += len(text)
            
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
            
            # Obtener número de documentos del índice
            total_docs = 0
            try:
                if hasattr(self.index, '_vector_store'):
                    # Intentar obtener conteo del vector store
                    if hasattr(self.index._vector_store, 'client'):
                        # Supabase vector store
                        total_docs = getattr(self.index._vector_store, '_collection_size', 0)
                    else:
                        # Simple vector store
                        if hasattr(self.index._vector_store, '_data'):
                            total_docs = len(self.index._vector_store._data.get('embeddings_dict', {}))
            except:
                pass
            
            # Determinar tipo de vector store
            vector_store_type = 'memory'
            if self.vector_store is not None:
                store_type_str = str(type(self.vector_store))
                if 'Supabase' in store_type_str:
                    vector_store_type = 'supabase'
                elif 'Simple' in store_type_str:
                    vector_store_type = 'memory'
            
            return {
                'total_documents': total_docs if total_docs > 0 else 'unknown',
                'embeddings_model': self.embeddings_model_name,
                'vector_store': vector_store_type
            }
        except Exception as e:
            logger.error(f"Error obteniendo stats: {str(e)}")
            return {
                'total_documents': 'error',
                'embeddings_model': self.embeddings_model_name,
                'vector_store': 'unknown'
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
