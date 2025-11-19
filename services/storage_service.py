"""
ARB-BOT - Servicio de Almacenamiento
Maneja almacenamiento de documentos en Supabase Storage (gratuito)
"""

import os
import logging
from typing import Optional, BinaryIO
import requests

logger = logging.getLogger(__name__)

class StorageService:
    """
    Servicio para almacenar documentos en Supabase Storage
    Si Supabase no está configurado, usa almacenamiento local
    """
    
    def __init__(self):
        """Inicializar servicio de almacenamiento"""
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.supabase_key = os.getenv('SUPABASE_KEY', '')
        self.bucket_name = os.getenv('SUPABASE_BUCKET', 'documents')
        self.use_supabase = bool(self.supabase_url and self.supabase_key)
        
        if self.use_supabase:
            logger.info("Usando Supabase Storage para persistencia")
        else:
            logger.info("Usando almacenamiento local (Supabase no configurado)")
    
    def upload_file(self, file_path: str, file_content: bytes, content_type: str = 'application/pdf') -> Optional[str]:
        """
        Subir archivo a Supabase Storage o guardar localmente
        
        Args:
            file_path: Ruta/nombre del archivo
            file_content: Contenido del archivo en bytes
            content_type: Tipo MIME del archivo
        
        Returns:
            URL o ruta del archivo guardado, None si falla
        """
        try:
            if self.use_supabase:
                return self._upload_to_supabase(file_path, file_content, content_type)
            else:
                return self._save_local(file_path, file_content)
        except Exception as e:
            logger.error(f"Error subiendo archivo: {str(e)}")
            # Fallback a local
            return self._save_local(file_path, file_content)
    
    def _upload_to_supabase(self, file_path: str, file_content: bytes, content_type: str) -> str:
        """Subir archivo a Supabase Storage"""
        try:
            # Obtener solo el nombre del archivo
            filename = os.path.basename(file_path)
            
            # URL de Supabase Storage API
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            
            headers = {
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': content_type,
                'x-upsert': 'true'  # Sobrescribir si existe
            }
            
            response = requests.post(url, data=file_content, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Retornar URL pública del archivo
            public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
            logger.info(f"Archivo subido a Supabase: {filename}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error subiendo a Supabase: {str(e)}")
            raise
    
    def _save_local(self, file_path: str, file_content: bytes) -> str:
        """Guardar archivo localmente"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        return file_path
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Descargar archivo desde Supabase o leer localmente
        
        Args:
            file_path: Ruta o nombre del archivo
        
        Returns:
            Contenido del archivo en bytes, None si no existe
        """
        try:
            if self.use_supabase:
                return self._download_from_supabase(file_path)
            else:
                return self._read_local(file_path)
        except Exception as e:
            logger.error(f"Error descargando archivo: {str(e)}")
            return None
    
    def _download_from_supabase(self, file_path: str) -> bytes:
        """Descargar archivo desde Supabase Storage"""
        filename = os.path.basename(file_path)
        url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    
    def _read_local(self, file_path: str) -> Optional[bytes]:
        """Leer archivo localmente"""
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()
        return None
    
    def save_index(self, index_data: dict, embeddings_data: bytes, file_path: str):
        """
        Guardar índice RAG en Supabase o localmente
        
        Args:
            index_data: Datos del índice (JSON)
            embeddings_data: Embeddings en formato numpy (bytes)
            file_path: Ruta del archivo de índice
        """
        try:
            import json
            
            if self.use_supabase:
                # Guardar índice JSON
                index_json = json.dumps(index_data, ensure_ascii=False).encode('utf-8')
                self._upload_to_supabase(
                    file_path,
                    index_json,
                    'application/json'
                )
                
                # Guardar embeddings
                embeddings_path = file_path.replace('.json', '_embeddings.npy')
                self._upload_to_supabase(
                    embeddings_path,
                    embeddings_data,
                    'application/octet-stream'
                )
                logger.info("Índice guardado en Supabase")
            else:
                # Guardar localmente
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, ensure_ascii=False, indent=2)
                
                embeddings_path = file_path.replace('.json', '_embeddings.npy')
                with open(embeddings_path, 'wb') as f:
                    f.write(embeddings_data)
                logger.info("Índice guardado localmente")
                
        except Exception as e:
            logger.error(f"Error guardando índice: {str(e)}")
            raise
    
    def load_index(self, file_path: str) -> Optional[tuple]:
        """
        Cargar índice RAG desde Supabase o localmente
        
        Args:
            file_path: Ruta del archivo de índice
        
        Returns:
            Tupla (index_data, embeddings_data) o None si no existe
        """
        try:
            import json
            
            if self.use_supabase:
                # Descargar índice JSON
                index_content = self._download_from_supabase(file_path)
                if not index_content:
                    return None
                
                index_data = json.loads(index_content.decode('utf-8'))
                
                # Descargar embeddings
                embeddings_path = file_path.replace('.json', '_embeddings.npy')
                embeddings_data = self._download_from_supabase(embeddings_path)
                
                logger.info("Índice cargado desde Supabase")
                return (index_data, embeddings_data)
            else:
                # Cargar localmente
                if not os.path.exists(file_path):
                    return None
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                embeddings_path = file_path.replace('.json', '_embeddings.npy')
                embeddings_data = None
                if os.path.exists(embeddings_path):
                    with open(embeddings_path, 'rb') as f:
                        embeddings_data = f.read()
                
                logger.info("Índice cargado localmente")
                return (index_data, embeddings_data)
                
        except Exception as e:
            logger.error(f"Error cargando índice: {str(e)}")
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """Verificar si un archivo existe"""
        if self.use_supabase:
            try:
                filename = os.path.basename(file_path)
                url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
                headers = {'Authorization': f'Bearer {self.supabase_key}'}
                response = requests.head(url, headers=headers, timeout=10)
                return response.status_code == 200
            except:
                return False
        else:
            return os.path.exists(file_path)

