"""
ARB-BOT - Procesador de Documentos Institucionales
Procesa documentos PDF, DOCX para el sistema RAG
"""

import os
import logging
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Procesa documentos institucionales (PDF, DOCX)
    Extrae texto y lo prepara para embeddings
    """
    
    def __init__(self):
        """Inicializar procesador de documentos"""
        self.supported_formats = ['.pdf', '.docx', '.txt']
        self.chunk_size = 500  # Tamaño de chunks para embeddings
        self.chunk_overlap = 50  # Solapamiento entre chunks
    
    def process_document(self, file_path: str) -> List[Dict]:
        """
        Procesar un documento y extraer texto
        
        Args:
            file_path: Ruta al archivo
        
        Returns:
            Lista de chunks con texto y metadata
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                text = self._extract_from_pdf(file_path)
            elif file_ext == '.docx':
                text = self._extract_from_docx(file_path)
            elif file_ext == '.txt':
                text = self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Formato no soportado: {file_ext}")
            
            # Dividir en chunks
            chunks = self._split_into_chunks(text, file_path)
            
            logger.info(f"Documento procesado: {len(chunks)} chunks extraídos")
            return chunks
            
        except Exception as e:
            logger.error(f"Error procesando documento {file_path}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extraer texto de PDF"""
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Página {page_num + 1} ---\n{page_text}\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extrayendo PDF: {str(e)}")
            # Fallback: intentar con otra librería
            try:
                import pypdf
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text.strip()
            except ImportError:
                raise Exception(f"No se pudo extraer texto del PDF. Instala PyPDF2 o pypdf: {str(e)}")
            except Exception as fallback_error:
                raise Exception(f"No se pudo extraer texto del PDF: {str(e)}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extraer texto de DOCX"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            # También extraer texto de tablas
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join([cell.text for cell in row.cells])
                    if row_text.strip():
                        text_parts.append(row_text)
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extrayendo DOCX: {str(e)}")
            raise Exception(f"No se pudo extraer texto del DOCX: {str(e)}")
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extraer texto de TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Intentar con otra codificación
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _split_into_chunks(self, text: str, source: str) -> List[Dict]:
        """
        Dividir texto en chunks para embeddings
        
        Args:
            text: Texto completo
            source: Fuente del documento
        
        Returns:
            Lista de chunks con metadata
        """
        # Limpiar texto
        text = self._clean_text(text)
        
        # Dividir por párrafos primero
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Si el párrafo es muy largo, dividirlo
            if len(para) > self.chunk_size:
                # Dividir párrafo largo
                words = para.split()
                temp_chunk = ""
                
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > self.chunk_size:
                        if temp_chunk:
                            chunks.append({
                                'id': chunk_id,
                                'text': temp_chunk.strip(),
                                'source': source,
                                'chunk_index': chunk_id
                            })
                            chunk_id += 1
                        temp_chunk = word
                    else:
                        temp_chunk += " " + word if temp_chunk else word
                
                if temp_chunk:
                    current_chunk = temp_chunk
            else:
                # Agregar párrafo al chunk actual
                if len(current_chunk) + len(para) + 2 > self.chunk_size:
                    if current_chunk:
                        chunks.append({
                            'id': chunk_id,
                            'text': current_chunk.strip(),
                            'source': source,
                            'chunk_index': chunk_id
                        })
                        chunk_id += 1
                    current_chunk = para
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
        
        # Agregar último chunk
        if current_chunk.strip():
            chunks.append({
                'id': chunk_id,
                'text': current_chunk.strip(),
                'source': source,
                'chunk_index': chunk_id
            })
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Limpiar y normalizar texto"""
        # Remover caracteres especiales
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalizar espacios
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def process_directory(self, directory_path: str) -> List[Dict]:
        """
        Procesar todos los documentos en un directorio
        
        Args:
            directory_path: Ruta al directorio
        
        Returns:
            Lista de todos los chunks de todos los documentos
        """
        all_chunks = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in self.supported_formats:
                    try:
                        logger.info(f"Procesando: {filename}")
                        chunks = self.process_document(file_path)
                        all_chunks.extend(chunks)
                    except Exception as e:
                        logger.error(f"Error procesando {filename}: {str(e)}")
                        continue
        
        logger.info(f"Total de chunks procesados: {len(all_chunks)}")
        return all_chunks

