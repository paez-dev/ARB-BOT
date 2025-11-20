"""
ARB-BOT - Procesador de Documentos Institucionales
Procesa documentos PDF, DOCX para el sistema RAG
"""

import os
import logging
from typing import List, Dict, Optional
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
        self.chunk_size = 500  # Tamaño de chunks balanceado (aumentado de 300 para mejor contexto)
        self.chunk_overlap = 50  # Solapamiento entre chunks (aumentado para mantener contexto)
    
    def process_document(self, file_path: str, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Procesar un documento y extraer texto
        
        Args:
            file_path: Ruta al archivo
            max_pages: Número máximo de páginas para PDFs (por defecto 100)
        
        Returns:
            Lista de chunks con texto y metadata
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            logger.info(f"Iniciando extracción de texto de {file_ext}")
            
            if file_ext == '.pdf':
                text = self._extract_from_pdf(file_path, max_pages=max_pages)
                if not text or len(text.strip()) < 10:
                    raise ValueError("No se pudo extraer texto del PDF. El documento puede estar protegido o corrupto.")
            elif file_ext == '.docx':
                text = self._extract_from_docx(file_path)
            elif file_ext == '.txt':
                text = self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Formato no soportado: {file_ext}")
            
            if not text or len(text.strip()) < 10:
                raise ValueError("No se pudo extraer texto del documento o el documento está vacío")
            
            logger.info(f"Texto extraído: {len(text)} caracteres")
            
            # Dividir en chunks
            logger.info("Dividiendo texto en chunks...")
            chunks = self._split_into_chunks(text, file_path)
            
            logger.info(f"Documento procesado: {len(chunks)} chunks extraídos")
            return chunks
            
        except Exception as e:
            logger.error(f"Error procesando documento {file_path}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_path: str, max_pages: Optional[int] = None) -> str:
        """
        Extraer texto de PDF con límite opcional de páginas
        
        Args:
            file_path: Ruta al archivo PDF
            max_pages: Número máximo de páginas a procesar (None = procesar todo)
        """
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Determinar cuántas páginas procesar
                if max_pages is None:
                    pages_to_process = total_pages
                    logger.info(f"Procesando todas las {total_pages} páginas del PDF...")
                else:
                    pages_to_process = min(total_pages, max_pages)
                    if total_pages > max_pages:
                        logger.warning(f"PDF tiene {total_pages} páginas. Procesando solo las primeras {max_pages} páginas.")
                
                # Procesar páginas con logging de progreso y límite de tiempo
                import time
                start_time = time.time()
                max_processing_time = 600  # 10 minutos máximo para extracción (aumentado para documentos grandes)
                
                for page_num in range(pages_to_process):
                    # Verificar tiempo transcurrido
                    elapsed = time.time() - start_time
                    if elapsed > max_processing_time:
                        logger.warning(f"Tiempo de procesamiento excedido ({elapsed:.1f}s). Procesadas {page_num}/{pages_to_process} páginas.")
                        text += f"\n\n[Nota: Procesamiento interrumpido por tiempo. Se procesaron {page_num} de {total_pages} páginas.]"
                        break
                    
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text.strip():
                            # Limitar tamaño de texto por página para evitar problemas de memoria
                            if len(page_text) > 8000:  # Reducido para evitar problemas
                                page_text = page_text[:8000] + "... [texto truncado por tamaño]"
                            text += f"\n--- Página {page_num + 1} ---\n{page_text}\n"
                        
                        # Log cada 10 páginas para monitorear progreso
                        if (page_num + 1) % 10 == 0:
                            elapsed = time.time() - start_time
                            logger.info(f"Procesadas {page_num + 1}/{pages_to_process} páginas... ({((page_num + 1) / pages_to_process * 100):.1f}%) - Tiempo: {elapsed:.1f}s")
                    except Exception as page_error:
                        logger.warning(f"Error extrayendo página {page_num + 1}: {str(page_error)}")
                        continue
                
                if max_pages and total_pages > max_pages:
                    text += f"\n\n[Nota: Este documento tiene {total_pages} páginas. Se procesaron las primeras {max_pages} páginas.]"
                else:
                    logger.info(f"✅ Procesadas todas las {total_pages} páginas exitosamente")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extrayendo PDF: {str(e)}")
            # Fallback: intentar con otra librería
            try:
                import pypdf
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    
                    if max_pages is None:
                        pages_to_process = total_pages
                        logger.info(f"Procesando todas las {total_pages} páginas del PDF...")
                    else:
                        pages_to_process = min(total_pages, max_pages)
                        if total_pages > max_pages:
                            logger.warning(f"PDF tiene {total_pages} páginas. Procesando solo las primeras {max_pages} páginas.")
                    
                    import time
                    start_time = time.time()
                    max_processing_time = 600  # 10 minutos máximo (aumentado para documentos grandes)
                    
                    for page_num in range(pages_to_process):
                        elapsed = time.time() - start_time
                        if elapsed > max_processing_time:
                            logger.warning(f"Tiempo excedido. Procesadas {page_num}/{pages_to_process} páginas.")
                            text += f"\n\n[Nota: Procesamiento interrumpido. Se procesaron {page_num} de {total_pages} páginas.]"
                            break
                        
                        try:
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text.strip():
                                if len(page_text) > 8000:
                                    page_text = page_text[:8000] + "... [texto truncado]"
                                text += page_text + "\n"
                            
                            if (page_num + 1) % 10 == 0:
                                elapsed = time.time() - start_time
                                logger.info(f"Procesadas {page_num + 1}/{pages_to_process} páginas... ({((page_num + 1) / pages_to_process * 100):.1f}%) - Tiempo: {elapsed:.1f}s")
                        except Exception:
                            continue
                    
                    if max_pages and total_pages > max_pages:
                        text += f"\n\n[Nota: Este documento tiene {total_pages} páginas. Se procesaron las primeras {max_pages} páginas.]"
                    else:
                        logger.info(f"✅ Procesadas todas las {total_pages} páginas exitosamente")
                
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

