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
            
            # Generar embeddings en batches (aumentado para Railway con más memoria)
            batch_size = min(20, len(texts))  # Máximo 20 chunks por vez (aumentado de 10)
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
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Buscar documentos relevantes para una consulta usando búsqueda híbrida
        (semántica + palabras clave para mejor recuperación)
        
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
            
            # BÚSQUEDA HÍBRIDA: Combinar semántica + palabras clave
            # 1. Búsqueda semántica (embeddings)
            query_embedding = self.embeddings_model.encode(
                [query],
                convert_to_numpy=True
            )
            
            # 2. Extraer palabras clave importantes de la consulta
            import re
            # Extraer números (artículos, etc.)
            numbers = re.findall(r'\d+', query)
            # Extraer palabras importantes (más de 3 caracteres, no artículos comunes)
            stop_words = {'que', 'del', 'de', 'la', 'el', 'los', 'las', 'un', 'una', 'es', 'son', 'está', 'están', 'dice', 'dicen', 'según', 'sobre', 'para', 'con', 'por', 'en', 'a', 'al', 'se', 'le', 'me', 'te', 'nos', 'les'}
            words = re.findall(r'\b\w{4,}\b', query.lower())
            keywords = [w for w in words if w not in stop_words]
            
            logger.info(f"Búsqueda: query='{query}', keywords={keywords}, numbers={numbers}")
            
            # Intentar importar FAISS al inicio para verificar disponibilidad
            faiss_available = False
            try:
                import faiss
                faiss_available = True
            except (ImportError, NameError):
                faiss_available = False
                if self.index is not None:
                    logger.warning("FAISS no disponible, desactivando índice FAISS")
                    self.index = None
            
            # Buscar documentos similares
            if self.index is not None and faiss_available:
                # Búsqueda con FAISS (rápida)
                try:
                    faiss.normalize_L2(query_embedding)
                    distances, indices = self.index.search(
                        query_embedding.astype('float32'),
                        min(top_k, len(self.document_store))
                    )
                    
                    semantic_results = []
                    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                        if idx < len(self.document_store):
                            similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
                            result = self.document_store[idx].copy()
                            result['similarity'] = float(similarity)
                            result['rank'] = i + 1
                            semantic_results.append(result)
                    
                    # BÚSQUEDA POR PALABRAS CLAVE (boost para resultados que contienen keywords)
                    keyword_boost = {}
                    query_lower = query.lower()
                    chunk_texts = [doc['text'].lower() for doc in self.document_store]
                    
                    for idx, chunk_text in enumerate(chunk_texts):
                        boost = 0.0
                        # Boost por números encontrados (artículos, etc.)
                        for num in numbers:
                            if num in chunk_text:
                                boost += 0.3
                        # Boost por palabras clave encontradas
                        for keyword in keywords:
                            if keyword in chunk_text:
                                boost += 0.2
                        # Boost si palabras de la consulta están en el chunk
                        if len(query_lower) > 5:
                            query_words = [w for w in query_lower.split() if len(w) > 3]
                            matches = sum(1 for word in query_words if word in chunk_text)
                            if matches > 0:
                                boost += (matches / max(len(query_words), 1)) * 0.3
                        
                        if boost > 0:
                            keyword_boost[idx] = min(boost, 0.5)
                    
                    # Combinar resultados semánticos con boost de keywords
                    results = []
                    seen_indices = set()
                    
                    # Primero agregar resultados con keyword boost (prioridad)
                    for idx, boost in sorted(keyword_boost.items(), key=lambda x: x[1], reverse=True)[:top_k]:
                        if idx < len(self.document_store):
                            result = self.document_store[idx].copy()
                            # Buscar similitud semántica si existe
                            semantic_sim = next((r['similarity'] for r in semantic_results if r.get('id') == result.get('id', idx)), 0.0)
                            # Combinar similitud semántica + keyword boost
                            result['similarity'] = min(1.0, semantic_sim + boost)
                            result['rank'] = len(results) + 1
                            result['has_keywords'] = True
                            results.append(result)
                            seen_indices.add(idx)
                    
                    # Agregar resultados semánticos que no están ya incluidos
                    for result in semantic_results:
                        result_idx = result.get('id', -1)
                        if result_idx not in seen_indices and result['similarity'] >= 0.2:
                            result['has_keywords'] = False
                            results.append(result)
                            seen_indices.add(result_idx)
                            if len(results) >= top_k * 2:
                                break
                    
                    # Ordenar por similitud combinada y tomar top_k
                    results.sort(key=lambda x: x['similarity'], reverse=True)
                    results = results[:top_k]
                    
                    # Filtrar resultados con similitud muy baja (< 0.2 ahora más permisivo)
                    results = [r for r in results if r['similarity'] >= 0.2]
                    
                    logger.info(f"Búsqueda híbrida: {len([r for r in results if r.get('has_keywords', False)])} con keywords, {len(results)} total")
                except Exception as e:
                    logger.warning(f"Error usando FAISS ({e}), usando búsqueda lineal")
                    self.index = None
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
    
    def get_context_for_query(self, query: str, top_k: int = 10, max_context_length: int = 2500) -> str:
        """
        Obtener contexto relevante para una consulta con búsqueda expandida si no encuentra resultados
        
        Args:
            query: Pregunta del usuario
            top_k: Número de chunks a incluir
            max_context_length: Longitud máxima del contexto en caracteres
        
        Returns:
            Texto de contexto formateado
        """
        # Intento 1: Búsqueda normal
        results = self.search(query, top_k)
        
        if not results:
            logger.warning(f"⚠️ No se encontraron resultados para: {query[:50]}")
            # Intento 2: Búsqueda expandida con más resultados
            logger.info("🔄 Intentando búsqueda expandida con más resultados...")
            results = self.search(query, top_k=20)  # Aumentar a 20 resultados
        
        # Filtrar resultados con similitud >= 0.25
        quality_results = [r for r in results if r.get('similarity', 0) >= 0.25]
        
        if not quality_results:
            logger.warning(f"⚠️ No se encontraron resultados con similitud >= 0.25")
            # Intento 3: Búsqueda más permisiva (umbral más bajo)
            logger.info("🔄 Intentando búsqueda más permisiva (umbral 0.15)...")
            quality_results = [r for r in results if r.get('similarity', 0) >= 0.15]
        
        if not quality_results:
            # Intento 4: Búsqueda por palabras clave directa (sin embeddings)
            logger.info("🔄 Intentando búsqueda por palabras clave directa...")
            quality_results = self._keyword_search(query, top_k=15)
        
        if not quality_results:
            logger.warning(f"❌ No se encontró información relevante después de múltiples intentos para: {query[:50]}")
            logger.info(f"   Total de documentos en sistema: {len(self.document_store)}")
            return ""
        
        # Usar solo los resultados de calidad
        results = quality_results
        logger.info(f"✅ Usando {len(results)} resultados de calidad para construir contexto")
        
        context_parts = []
        total_length = 0
        
        for result in results:
            # Limitar el texto de cada chunk si es muy largo
            chunk_text = result['text']
            # Limitar cada chunk a 800 caracteres (aumentado para Railway con más memoria)
            # Esto permite mantener más contexto completo por chunk
            if len(chunk_text) > 800:
                # Truncar en un punto completo si es posible
                truncated = chunk_text[:800]
                last_period = truncated.rfind('.')
                if last_period > 600:
                    chunk_text = truncated[:last_period + 1]
                else:
                    chunk_text = truncated + "..."
            
            # Formato más limpio sin etiquetas de fuente (se removerán después)
            context_part = chunk_text.strip()
            
            # Verificar si agregar este chunk excedería el límite
            # Usar un margen más flexible para incluir más chunks
            if total_length + len(context_part) + 10 > max_context_length:  # +10 para separador
                # Si ya tenemos al menos 3 chunks, parar aquí (mejor que solo 1-2)
                if len(context_parts) >= 3:
                    break
                # Si tenemos menos de 3 chunks, intentar incluir al menos parte de este
                remaining = max_context_length - total_length - 10
                if remaining > 100:  # Aumentado de 50 para incluir más texto
                    truncated = context_part[:remaining]
                    last_period = truncated.rfind('.')
                    if last_period > remaining * 0.7:
                        context_part = truncated[:last_period + 1]
                    else:
                        context_part = truncated + "..."
                    context_parts.append(context_part)
                break
            
            context_parts.append(context_part)
            total_length += len(context_part) + 10  # +10 para separador estimado
        
        # Logging para diagnóstico
        if context_parts:
            logger.info(f"Contexto construido: {len(context_parts)} chunks, {total_length} caracteres totales (máx: {max_context_length})")
            # Log de los primeros 200 caracteres de cada chunk para diagnóstico
            for i, part in enumerate(context_parts[:3]):  # Solo primeros 3 para no saturar logs
                preview = part[:200].replace('\n', ' ')
                logger.info(f"  Chunk {i+1} preview: {preview}...")
        
        # Unir con espacios simples (más limpio que "---")
        full_context = " ".join(context_parts)
        logger.info(f"Contexto final completo: {len(full_context)} caracteres")
        return full_context
    
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
                    
                    # Logging detallado para diagnóstico
                    logger.info(f"Índice cargado desde storage: {len(self.document_store)} documentos")
                    if len(self.document_store) > 0:
                        # Mostrar preview de algunos chunks para verificar
                        sample_chunks = self.document_store[:3]
                        for i, chunk in enumerate(sample_chunks):
                            preview = chunk.get('text', '')[:100].replace('\n', ' ')
                            logger.info(f"  Chunk {i+1} sample: {preview}...")
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

