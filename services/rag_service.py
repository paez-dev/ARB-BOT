"""
ARB-BOT - Servicio RAG (Retrieval Augmented Generation)
Sistema de búsqueda y recuperación de información de documentos
"""

import os
import logging
import json
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RAGService:
    """
    Servicio RAG para buscar información relevante en documentos
    Usa embeddings y búsqueda semántica (100% gratuito)
    """
    
    def __init__(self, embeddings_model='all-MiniLM-L6-v2'):
        """
        Inicializar servicio RAG
        
        Args:
            embeddings_model: Modelo de embeddings (gratuito de sentence-transformers)
        """
        self.embeddings_model_name = embeddings_model
        self.embeddings_model = None
        self.document_store = []
        self.embeddings_store = None
        self.index = None
        self._load_embeddings_model()
    
    def _load_embeddings_model(self):
        """Cargar modelo de embeddings con optimizaciones de memoria"""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            import gc
            
            # Optimizaciones de memoria agresivas
            torch.set_num_threads(1)
            # Limpiar caché antes de cargar
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info(f"Cargando modelo de embeddings: {self.embeddings_model_name} (esto puede tardar ~30-60 segundos)...")
            
            # Cargar modelo con timeout implícito (si tarda mucho, puede ser problema de red)
            import time
            start_time = time.time()
            
            # Cargar modelo de embeddings (sentence-transformers no acepta model_kwargs)
            self.embeddings_model = SentenceTransformer(
                self.embeddings_model_name,
                device='cpu'
            )
            
            # Limpiar memoria después de cargar
            gc.collect()
            
            load_time = time.time() - start_time
            logger.info(f"Modelo de embeddings cargado exitosamente en {load_time:.2f} segundos")
            
        except Exception as e:
            logger.error(f"Error cargando modelo de embeddings: {str(e)}")
            raise
    
    def add_documents(self, chunks: List[Dict]):
        """
        Agregar documentos al sistema RAG
        
        Args:
            chunks: Lista de chunks de documentos
        """
        try:
            if not chunks:
                logger.warning("No hay chunks para agregar")
                return
            
            logger.info(f"Agregando {len(chunks)} chunks al sistema RAG...")
            
            # Generar embeddings para todos los chunks con optimizaciones de memoria
            texts = [chunk['text'] for chunk in chunks]
            import gc
            
            # Generar embeddings en batches pequeños para ahorrar memoria
            batch_size = min(10, len(texts))  # Máximo 10 chunks por vez
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.embeddings_model.encode(
                    batch_texts,
                    show_progress_bar=False,  # Desactivar para ahorrar memoria
                    convert_to_numpy=True,
                    batch_size=5,  # Procesar en mini-batches
                    normalize_embeddings=True
                )
                all_embeddings.append(batch_embeddings)
                # Limpiar memoria después de cada batch
                gc.collect()
            
            # Concatenar todos los embeddings
            embeddings = np.vstack(all_embeddings)
            
            # Guardar documentos y embeddings
            start_id = len(self.document_store)
            for i, chunk in enumerate(chunks):
                chunk['id'] = start_id + i
                self.document_store.append(chunk)
            
            # Guardar embeddings
            if self.embeddings_store is None:
                self.embeddings_store = embeddings
            else:
                self.embeddings_store = np.vstack([self.embeddings_store, embeddings])
            
            # Crear índice FAISS para búsqueda rápida
            self._build_index()
            
            logger.info(f"Documentos agregados. Total en sistema: {len(self.document_store)}")
            
        except Exception as e:
            logger.error(f"Error agregando documentos: {str(e)}")
            raise
    
    def _build_index(self):
        """Construir índice FAISS para búsqueda rápida"""
        try:
            import faiss
            
            if self.embeddings_store is None or len(self.embeddings_store) == 0:
                return
            
            dimension = self.embeddings_store.shape[1]
            
            # Crear índice FAISS (L2 distance)
            self.index = faiss.IndexFlatL2(dimension)
            
            # Normalizar embeddings para búsqueda por coseno
            faiss.normalize_L2(self.embeddings_store)
            
            # Agregar embeddings al índice
            self.index.add(self.embeddings_store.astype('float32'))
            
            logger.info(f"Índice FAISS construido con {self.index.ntotal} vectores")
            
        except ImportError:
            logger.warning("FAISS no disponible, usando búsqueda lineal")
            self.index = None
        except Exception as e:
            logger.error(f"Error construyendo índice: {str(e)}")
            self.index = None
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Buscar documentos relevantes para una consulta
        
        Args:
            query: Pregunta o consulta del usuario
            top_k: Número de resultados a retornar
        
        Returns:
            Lista de chunks relevantes con scores
        """
        try:
            if not self.document_store or len(self.document_store) == 0:
                logger.warning("No hay documentos en el sistema RAG")
                return []
            
            # Generar embedding de la consulta
            query_embedding = self.embeddings_model.encode(
                [query],
                convert_to_numpy=True
            )
            
            # Buscar documentos similares
            if self.index is not None:
                # Búsqueda con FAISS (rápida)
                try:
                    import faiss
                    faiss.normalize_L2(query_embedding)
                    distances, indices = self.index.search(
                        query_embedding.astype('float32'),
                        min(top_k, len(self.document_store))
                    )
                    
                    results = []
                    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                        if idx < len(self.document_store):
                            similarity = 1 - distance  # Convertir distancia a similitud
                            result = self.document_store[idx].copy()
                            result['similarity'] = float(similarity)
                            result['rank'] = i + 1
                            results.append(result)
                except (ImportError, NameError) as e:
                    # Si FAISS no está disponible, usar búsqueda lineal
                    logger.warning(f"FAISS no disponible en búsqueda ({e}), usando método lineal")
                    self.index = None  # Forzar búsqueda lineal en el futuro
                    # Continuar con búsqueda lineal
                    query_embedding = query_embedding[0]
                    similarities = []
                    
                    for i, doc_embedding in enumerate(self.embeddings_store):
                        # Calcular similitud coseno
                        similarity = np.dot(query_embedding, doc_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                        similarities.append((similarity, i))
                    
                    # Ordenar por similitud
                    similarities.sort(reverse=True, key=lambda x: x[0])
                    
                    results = []
                    for rank, (similarity, idx) in enumerate(similarities[:top_k]):
                        result = self.document_store[idx].copy()
                        result['similarity'] = float(similarity)
                        result['rank'] = rank + 1
                        results.append(result)
                
            else:
                # Búsqueda lineal (más lenta pero funciona sin FAISS)
                query_embedding = query_embedding[0]
                similarities = []
                
                for i, doc_embedding in enumerate(self.embeddings_store):
                    # Calcular similitud coseno
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    similarities.append((similarity, i))
                
                # Ordenar por similitud
                similarities.sort(reverse=True, key=lambda x: x[0])
                
                results = []
                for rank, (similarity, idx) in enumerate(similarities[:top_k]):
                    result = self.document_store[idx].copy()
                    result['similarity'] = float(similarity)
                    result['rank'] = rank + 1
                    results.append(result)
            
            logger.info(f"Búsqueda completada: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """
        Obtener contexto relevante para una consulta
        
        Args:
            query: Pregunta del usuario
            top_k: Número de chunks a incluir
        
        Returns:
            Texto de contexto formateado
        """
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            context_parts.append(
                f"[Fuente: {os.path.basename(result.get('source', 'Desconocido'))}]\n"
                f"{result['text']}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def save_index(self, filepath: str):
        """Guardar índice y documentos"""
        try:
            data = {
                'documents': self.document_store,
                'embeddings_model': self.embeddings_model_name
            }
            
            # Preparar embeddings para guardar
            embeddings_data = None
            if self.embeddings_store is not None:
                import io
                embeddings_buffer = io.BytesIO()
                np.save(embeddings_buffer, self.embeddings_store)
                embeddings_data = embeddings_buffer.getvalue()
            
            # Usar StorageService si está disponible
            try:
                from services.storage_service import StorageService
                storage = StorageService()
                storage.save_index(data, embeddings_data or b'', filepath)
                logger.info(f"Índice guardado (usando storage service)")
            except ImportError:
                # Fallback: guardar localmente
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                if embeddings_data:
                    with open(filepath.replace('.json', '_embeddings.npy'), 'wb') as f:
                        f.write(embeddings_data)
                
                logger.info(f"Índice guardado localmente en: {filepath}")
            
        except Exception as e:
            logger.error(f"Error guardando índice: {str(e)}")
    
    def load_index(self, filepath: str):
        """Cargar índice y documentos"""
        try:
            # Intentar usar StorageService primero
            try:
                from services.storage_service import StorageService
                storage = StorageService()
                result = storage.load_index(filepath)
                
                if result:
                    data, embeddings_data = result
                    self.document_store = data['documents']
                    self.embeddings_model_name = data.get('embeddings_model', 'all-MiniLM-L6-v2')
                    
                    # Cargar embeddings desde bytes
                    if embeddings_data:
                        import io
                        embeddings_buffer = io.BytesIO(embeddings_data)
                        self.embeddings_store = np.load(embeddings_buffer)
                        self._build_index()
                    
                    logger.info(f"Índice cargado desde storage: {len(self.document_store)} documentos")
                    return
            except ImportError:
                pass  # Continuar con método local
            
            # Fallback: cargar localmente
            if not os.path.exists(filepath):
                logger.warning(f"Índice no encontrado en: {filepath}")
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.document_store = data['documents']
            self.embeddings_model_name = data.get('embeddings_model', 'all-MiniLM-L6-v2')
            
            # Cargar embeddings
            embeddings_file = filepath.replace('.json', '_embeddings.npy')
            if os.path.exists(embeddings_file):
                self.embeddings_store = np.load(embeddings_file)
                self._build_index()
            
            logger.info(f"Índice cargado localmente: {len(self.document_store)} documentos")
            
        except Exception as e:
            logger.error(f"Error cargando índice: {str(e)}")
            raise
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del sistema RAG"""
        return {
            'total_documents': len(self.document_store),
            'embeddings_model': self.embeddings_model_name,
            'has_index': self.index is not None,
            'sources': list(set([doc.get('source', 'Desconocido') for doc in self.document_store]))
        }

