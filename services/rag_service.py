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
        """Cargar modelo de embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Cargando modelo de embeddings: {self.embeddings_model_name}")
            self.embeddings_model = SentenceTransformer(self.embeddings_model_name)
            logger.info("Modelo de embeddings cargado exitosamente")
            
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
            
            # Generar embeddings para todos los chunks
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embeddings_model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
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
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Guardar embeddings si es posible
            if self.embeddings_store is not None:
                np.save(filepath.replace('.json', '_embeddings.npy'), self.embeddings_store)
            
            logger.info(f"Índice guardado en: {filepath}")
            
        except Exception as e:
            logger.error(f"Error guardando índice: {str(e)}")
    
    def load_index(self, filepath: str):
        """Cargar índice y documentos"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.document_store = data['documents']
            self.embeddings_model_name = data.get('embeddings_model', 'all-MiniLM-L6-v2')
            
            # Cargar embeddings
            embeddings_file = filepath.replace('.json', '_embeddings.npy')
            if os.path.exists(embeddings_file):
                self.embeddings_store = np.load(embeddings_file)
                self._build_index()
            
            logger.info(f"Índice cargado: {len(self.document_store)} documentos")
            
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

