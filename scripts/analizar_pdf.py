"""
Script para analizar el PDF antes de la ingesta
Ejecutar en Google Colab o localmente con: python scripts/analizar_pdf.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def analyze_pdf(file_path: str):
    """
    Analizar PDF y mostrar estadísticas importantes
    """
    try:
        import PyPDF2
        import re
        
        print("=" * 60)
        print("📄 ANÁLISIS DEL PDF")
        print("=" * 60)
        
        # Abrir PDF
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            
            print(f"\n📊 INFORMACIÓN BÁSICA:")
            print(f"   Archivo: {os.path.basename(file_path)}")
            print(f"   Total de páginas: {total_pages}")
            
            # Extraer texto de todas las páginas
            print(f"\n📖 Extrayendo texto de todas las páginas...")
            all_text = ""
            pages_with_text = 0
            pages_text_length = []
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        pages_with_text += 1
                        text_len = len(page_text)
                        pages_text_length.append(text_len)
                        all_text += f"\n--- Página {page_num} ---\n{page_text}"
                        
                        if page_num % 20 == 0:
                            print(f"   Procesadas {page_num}/{total_pages} páginas...")
                except Exception as e:
                    print(f"   ⚠️ Error en página {page_num}: {e}")
                    continue
            
            print(f"\n✅ Extracción completada:")
            print(f"   Páginas con texto: {pages_with_text}/{total_pages}")
            print(f"   Total de caracteres: {len(all_text):,}")
            print(f"   Promedio por página: {len(all_text) // pages_with_text if pages_with_text > 0 else 0:,} caracteres")
            
            # Analizar estructura
            print(f"\n🔍 ANÁLISIS DE ESTRUCTURA:")
            
            # Buscar artículos
            article_pattern = re.compile(r'(?i)(?:art[ií]culo|art\.?)\s+(\d+)', re.IGNORECASE)
            articles_found = article_pattern.findall(all_text)
            unique_articles = sorted(set(articles_found), key=lambda x: int(x) if x.isdigit() else 9999)
            
            print(f"   Artículos detectados: {len(unique_articles)}")
            if unique_articles:
                print(f"   Rango: Artículo {unique_articles[0]} - Artículo {unique_articles[-1]}")
                print(f"   Primeros 10: {', '.join(unique_articles[:10])}")
                if len(unique_articles) > 10:
                    print(f"   Últimos 10: {', '.join(unique_articles[-10:])}")
            
            # Buscar secciones
            section_pattern = re.compile(r'(?i)(?:secci[oó]n|cap[ií]tulo|t[ií]tulo)\s+([IVX\d]+)', re.IGNORECASE)
            sections_found = section_pattern.findall(all_text)
            print(f"   Secciones/Capítulos detectados: {len(set(sections_found))}")
            
            # Analizar distribución de texto
            print(f"\n📊 DISTRIBUCIÓN DE CONTENIDO:")
            if pages_text_length:
                avg_page_len = sum(pages_text_length) / len(pages_text_length)
                min_page_len = min(pages_text_length)
                max_page_len = max(pages_text_length)
                print(f"   Páginas con texto: {pages_with_text}")
                print(f"   Promedio por página: {avg_page_len:.0f} caracteres")
                print(f"   Mínimo: {min_page_len} caracteres")
                print(f"   Máximo: {max_page_len} caracteres")
            
            # Estimar chunks esperados
            print(f"\n🎯 ESTIMACIÓN DE CHUNKS:")
            
            # Asumiendo chunk_size de ~1000 tokens (~800 caracteres en español)
            chunk_size_chars = 800
            estimated_chunks_simple = len(all_text) // chunk_size_chars
            estimated_chunks_with_overlap = int(len(all_text) / (chunk_size_chars * 0.8))  # Con overlap
            
            print(f"   Con chunking simple (800 chars): ~{estimated_chunks_simple} chunks")
            print(f"   Con chunking + overlap (20%): ~{estimated_chunks_with_overlap} chunks")
            print(f"   Con chunking semántico: ~{estimated_chunks_with_overlap * 0.7:.0f}-{estimated_chunks_with_overlap * 1.3:.0f} chunks")
            print(f"   (El semántico puede agrupar o dividir más)")
            
            # Verificar si hay mucho texto en metadata vs contenido
            print(f"\n⚠️ VERIFICACIONES:")
            
            # Buscar patrones que puedan indicar problemas
            empty_pages = total_pages - pages_with_text
            if empty_pages > 0:
                print(f"   ⚠️ {empty_pages} páginas sin texto (pueden ser imágenes o portadas)")
            
            # Verificar si hay mucho texto repetitivo
            words = all_text.split()
            unique_words = set(words)
            if len(words) > 0:
                uniqueness_ratio = len(unique_words) / len(words)
                if uniqueness_ratio < 0.3:
                    print(f"   ⚠️ Mucho texto repetitivo (ratio: {uniqueness_ratio:.2f})")
            
            # Buscar el artículo 52 específicamente
            print(f"\n🔍 BÚSQUEDA ESPECÍFICA:")
            if '52' in unique_articles:
                article_52_pattern = re.compile(r'(?i)(?:art[ií]culo|art\.?)\s+52[^\d]', re.IGNORECASE)
                matches = article_52_pattern.findall(all_text)
                print(f"   ✅ Artículo 52 encontrado en el texto")
                print(f"   Menciones: {len(matches)}")
                
                # Buscar contexto del artículo 52
                article_52_context = re.search(
                    r'(?i)(?:art[ií]culo|art\.?)\s+52[^\d].{0,500}',
                    all_text,
                    re.DOTALL
                )
                if article_52_context:
                    preview = article_52_context.group(0)[:200].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
            else:
                print(f"   ❌ Artículo 52 NO encontrado en el texto")
                print(f"   (Puede estar escrito de forma diferente)")
            
            # Recomendaciones
            print(f"\n💡 RECOMENDACIONES:")
            
            if estimated_chunks_simple < 100 and total_pages > 50:
                print(f"   ⚠️ ADVERTENCIA: Se esperarían más chunks para un PDF de {total_pages} páginas")
                print(f"   Posibles causas:")
                print(f"   - El PDF tiene muchas imágenes y poco texto")
                print(f"   - El texto está en formato de imagen (OCR necesario)")
                print(f"   - El chunking semántico está agrupando demasiado")
            
            if len(unique_articles) < 10 and total_pages > 50:
                print(f"   ⚠️ Pocos artículos detectados para un documento grande")
                print(f"   Puede que el formato de artículos sea diferente")
            
            print(f"\n✅ Análisis completado")
            print("=" * 60)
            
            return {
                'total_pages': total_pages,
                'pages_with_text': pages_with_text,
                'total_characters': len(all_text),
                'articles_found': len(unique_articles),
                'estimated_chunks': estimated_chunks_with_overlap
            }
            
    except ImportError:
        print("❌ Error: PyPDF2 no está instalado")
        print("   Instala con: pip install PyPDF2")
        return None
    except Exception as e:
        print(f"❌ Error analizando PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Buscar el PDF en la carpeta
    pdf_folder = Path(__file__).parent.parent / "documento que usaré en la ingesta"
    pdf_file = pdf_folder / "MANUAL DE CONVIVENCIA ESCOLAR ROLDANISTA 2023.pdf"
    
    if pdf_file.exists():
        print(f"📁 Encontrado: {pdf_file}")
        analyze_pdf(str(pdf_file))
    else:
        print(f"❌ No se encontró el PDF en: {pdf_folder}")
        print(f"\n💡 Para usar este script:")
        print(f"   1. Ejecuta: python scripts/analizar_pdf.py")
        print(f"   2. O copia el código a Google Colab")
        print(f"   3. O proporciona la ruta del PDF como argumento")

