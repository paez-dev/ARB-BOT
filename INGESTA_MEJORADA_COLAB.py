# ============================================================
# 🚀 ARB-BOT — INGESTA MEJORADA V2.0
# ============================================================
# 
# INSTRUCCIONES:
# 1. Abre Google Colab: https://colab.research.google.com
# 2. Crea un nuevo notebook
# 3. Copia y pega este código en celdas separadas (donde dice "# --- CELDA ---")
# 4. Sube tu PDF: MANUAL DE CONVIVENCIA ESCOLAR ROLDANISTA 2023.pdf
# 5. Ejecuta celda por celda
#
# CAMBIOS vs versión anterior:
# - Usa pdfplumber (mejor extracción que PyPDF2)
# - Función fix_broken_words() que repara "institu ción" → "institución"
# - Limpieza automática en todo el proceso
# ============================================================

# --- CELDA 1: Instalar dependencias ---
# !pip install -q supabase sentence-transformers psycopg2-binary pdfplumber

# --- CELDA 2: Imports ---
import os
import json
import re
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
import pdfplumber
from datetime import datetime, timezone
from pathlib import Path

print('✅ Imports listos')

# --- CELDA 3: Configuración ---
SUPABASE_URL = "https://ympekltzqzlsbdgbzbpz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltcGVrbHR6cXpsc2JkZ2J6YnB6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MDQ4NDYsImV4cCI6MjA3OTA4MDg0Nn0.0aFi8Za_N2vJ4CKiG7BofnOpLHa7J1BY41b8Y6BLV7Q"

DB_HOST = "aws-1-us-east-1.pooler.supabase.com"
DB_NAME = "postgres"
DB_USER = "postgres.ympekltzqzlsbdgbzbpz"
DB_PASS = "Z32pp23z$$1124$$"
DB_PORT = "6543"

SCHEMA = "vecs"
TABLE = "arbot_documents"
VECTOR_DIM = 384

PDF_FILE = "MANUAL DE CONVIVENCIA ESCOLAR ROLDANISTA 2023.pdf"

print('✅ Configuración cargada')

# --- CELDA 4: Conexión a BD ---
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

# Test conexión
try:
    conn_test = get_connection()
    conn_test.close()
    print('✅ Conexión a Supabase OK')
except Exception as e:
    print(f'❌ Error: {e}')

# --- CELDA 5: 🔧 FUNCIÓN CLAVE - Limpiar palabras cortadas ---
def fix_broken_words(text: str) -> str:
    """
    Repara palabras cortadas por mal OCR/extracción.
    
    Ejemplos:
        'institu ción' → 'institución'
        'ESTUDIANTE S' → 'ESTUDIANTES'
        'Anton io' → 'Antonio'
    """
    if not text:
        return text
    
    # Patrón 1: minúscula + espacio + minúscula
    text = re.sub(r'([a-záéíóúñü]) ([a-záéíóúñü])', r'\1\2', text)
    
    # Patrón 2: Mayúscula + espacio + minúscula
    text = re.sub(r'([A-ZÁÉÍÓÚÑÜ]) ([a-záéíóúñü])', r'\1\2', text)
    
    # Patrón 3: Mayúscula + espacio + Mayúscula (palabras en MAYÚSCULAS)
    text = re.sub(r'([A-ZÁÉÍÓÚÑÜ]) ([A-ZÁÉÍÓÚÑÜ])(?=[A-ZÁÉÍÓÚÑÜ\s]|$)', r'\1\2', text)
    
    # Repetir para casos anidados
    text = re.sub(r'([a-záéíóúñü]) ([a-záéíóúñü])', r'\1\2', text)
    text = re.sub(r'([A-ZÁÉÍÓÚÑÜ]) ([a-záéíóúñü])', r'\1\2', text)
    
    # Limpiar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# Test de la función
print("🧪 Test de limpieza:")
tests = [
    "institu ción educat iva",
    "ESTUDIANTE S",
    "Anton io Rol dán",
    "derech o al debido proces o"
]
for t in tests:
    print(f"  '{t}' → '{fix_broken_words(t)}'")

print('\n✅ Función de limpieza lista')

# --- CELDA 6: Extracción de texto con pdfplumber ---
def read_pdf_extract_text(pdf_path: str):
    """Extrae texto del PDF con pdfplumber + limpieza automática."""
    pages = []
    full_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"📖 Procesando {total} páginas...")
        
        for i, page in enumerate(pdf.pages, start=1):
            try:
                raw_text = page.extract_text() or ""
                
                # 🔧 APLICAR LIMPIEZA
                cleaned_text = fix_broken_words(raw_text)
                
                pages.append({"page": i, "text": cleaned_text})
                full_text += f"\n\n--- Página {i} ---\n\n" + cleaned_text
                
                if i % 20 == 0:
                    print(f"  ✓ {i}/{total} páginas")
                    
            except Exception as e:
                print(f"  ⚠ Error página {i}: {e}")
                continue
    
    print(f'✅ PDF procesado: {len(pages)} páginas')
    return {"text": full_text, "pages": pages, "total_pages": total}

print('✅ Función de extracción lista')

# --- CELDA 7: Utilidades ---
def count_tokens_approx(text: str) -> int:
    return max(1, len(text) // 4)

def clean_text(s: str) -> str:
    if not s:
        return s
    s = fix_broken_words(s)
    return re.sub(r'\s+', ' ', s).strip()

print('✅ Utilidades listas')

# --- CELDA 8: Chunking jerárquico ---
def chunk_hierarchical_legal(full_text: str, pages=None, max_tokens=1600):
    """Divide por títulos, capítulos y artículos."""
    lines = full_text.split('\n')
    chunks = []
    current = {'title': None, 'chapter': None, 'article': None, 'text_lines': [], 'page': None}

    title_pattern = re.compile(r'(?i)^(TÍTULO|TITULO)\b')
    chapter_pattern = re.compile(r'(?i)^(CAPÍTULO|CAPITULO)\b')
    article_pattern = re.compile(r'(?i)^(ARTÍCULO|ARTICULO|Artículo|Articulo)\s*\d+')

    def save_current():
        txt = '\n'.join(current['text_lines']).strip()
        if not txt:
            return
        cleaned = clean_text(txt)
        if count_tokens_approx(cleaned) > max_tokens:
            paras = [p.strip() for p in cleaned.split('\n\n') if p.strip()]
            sub = ''
            for p in paras:
                if count_tokens_approx(sub + ' ' + p) > max_tokens:
                    if sub.strip():
                        chunks.append({'text': sub.strip(), 'meta': {k: current.get(k) for k in ('title','chapter','article','page')}})
                    sub = p
                else:
                    sub = (sub + '\n\n' + p).strip()
            if sub.strip():
                chunks.append({'text': sub.strip(), 'meta': {k: current.get(k) for k in ('title','chapter','article','page')}})
        else:
            chunks.append({'text': cleaned, 'meta': {k: current.get(k) for k in ('title','chapter','article','page')}})

    for line in lines:
        s = line.strip()
        if not s:
            current['text_lines'].append('')
            continue
        if title_pattern.match(s):
            save_current()
            current = {'title': s, 'chapter': None, 'article': None, 'text_lines': [s], 'page': None}
            continue
        if chapter_pattern.match(s):
            save_current()
            current['chapter'] = s
            current['text_lines'] = [s]
            continue
        if article_pattern.match(s):
            save_current()
            current['article'] = s
            current['text_lines'] = [s]
            continue
        current['text_lines'].append(s)

    save_current()
    
    for i, c in enumerate(chunks):
        c['meta'].update({
            'chunk_index': i, 
            'ingestion_date': datetime.now(timezone.utc).isoformat()
        })
    
    print(f'✅ Chunking: {len(chunks)} chunks')
    return chunks

print('✅ Chunking listo')

# --- CELDA 9: Modelo de Embeddings ---
EMBEDDINGS_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

print(f'🧠 Cargando modelo: {EMBEDDINGS_MODEL}')
model = SentenceTransformer(EMBEDDINGS_MODEL)
print(f'✅ Modelo cargado — dimensión: {model.get_sentence_embedding_dimension()}')

def make_embeddings(texts: list, batch_size: int = 32):
    embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        arr = model.encode(batch, show_progress_bar=True, convert_to_numpy=True)
        for v in arr:
            embs.append(v.tolist())
    return embs

print('✅ Embeddings listos')

# --- CELDA 10: Verificar tabla ---
def ensure_table_exists(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_schema=%s AND table_name=%s)", 
        (SCHEMA, TABLE)
    )
    if not cur.fetchone()[0]:
        raise RuntimeError(f'❌ Tabla {SCHEMA}.{TABLE} no existe')
    print(f'✅ Tabla {SCHEMA}.{TABLE} OK')
    cur.close()

print('✅ Verificación lista')

# --- CELDA 11: Subir a Supabase ---
def upload_chunks_to_supabase(chunks, conn, batch_size=16):
    cur = conn.cursor()
    
    records = []
    for i, c in enumerate(chunks):
        text = clean_text(c['text'])
        if not text:
            continue
        meta = c.get('meta', {})
        chunk_id = f"{meta.get('file', 'doc')}_{meta.get('chunk_index', i)}"
        records.append((chunk_id, text, json.dumps(meta)))
    
    print(f'📊 Generando embeddings para {len(records)} chunks...')
    all_texts = [r[1] for r in records]
    embeddings = make_embeddings(all_texts, batch_size=batch_size)
    
    print(f'📤 Subiendo a Supabase...')
    insert_sql = f"""
        INSERT INTO {SCHEMA}.{TABLE} (id, vec, text, metadata) 
        VALUES %s 
        ON CONFLICT (id) DO UPDATE SET 
            vec = EXCLUDED.vec, 
            text = EXCLUDED.text, 
            metadata = EXCLUDED.metadata
    """
    
    to_insert = []
    for (rid, txt, meta), emb in zip(records, embeddings):
        vec_literal = '[' + ','.join(map(str, emb)) + ']'
        to_insert.append((rid, vec_literal, txt, meta))
    
    execute_values(cur, insert_sql, to_insert, template="(%s, %s::vector, %s, %s::jsonb)")
    conn.commit()
    
    print(f'✅ Subidos {len(to_insert)} chunks')
    cur.close()

print('✅ Función de subida lista')

# --- CELDA 12: 🚀 PIPELINE PRINCIPAL ---
def process_pdf_pipeline(pdf_path, clear_all=True):
    print('\n' + '='*50)
    print(f'🚀 INGESTA MEJORADA: {pdf_path}')
    print('='*50)
    
    # 1) Extraer
    print('\n📄 Paso 1: Extrayendo texto...')
    data = read_pdf_extract_text(pdf_path)
    
    # 2) Chunks
    print('\n✂️ Paso 2: Generando chunks...')
    chunks = chunk_hierarchical_legal(data['text'])
    
    for i, c in enumerate(chunks):
        if 'meta' not in c:
            c['meta'] = {}
        c['meta'].setdefault('file', Path(pdf_path).name)
        c['meta'].setdefault('chunk_index', i)
    
    # 3) Conectar
    print('\n🔗 Paso 3: Conectando a Supabase...')
    conn = get_connection()
    
    # 4) Limpiar
    if clear_all:
        print('\n🗑️ Paso 4: Limpiando tabla anterior...')
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {SCHEMA}.{TABLE};")
        conn.commit()
        cur.close()
        print('   ✓ Tabla limpiada')
    
    # 5) Verificar
    ensure_table_exists(conn)
    
    # 6) Subir
    print('\n📤 Paso 5: Subiendo chunks...')
    upload_chunks_to_supabase(chunks, conn)
    
    # 7) Verificar muestra
    print('\n🔍 Paso 6: Verificando...')
    cur = conn.cursor()
    cur.execute(f"SELECT id, LEFT(text, 300) FROM {SCHEMA}.{TABLE} LIMIT 2")
    for r in cur.fetchall():
        print(f'\n  ID: {r[0]}')
        print(f'  Texto: {r[1][:150]}...')
    cur.close()
    
    conn.close()
    
    print('\n' + '='*50)
    print('✅ INGESTA COMPLETADA')
    print('='*50)

print('✅ Pipeline listo')

# --- CELDA 13: ▶️ EJECUTAR ---
# ⚠️ Asegúrate de haber subido el PDF antes de ejecutar esta celda

if not os.path.exists(PDF_FILE):
    print(f"❗ No se encuentra: {PDF_FILE}")
    print("   Sube el archivo PDF primero.")
else:
    process_pdf_pipeline(PDF_FILE, clear_all=True)

# --- CELDA 14: Verificación final ---
conn = get_connection()
cur = conn.cursor()
cur.execute(f"SELECT count(*) FROM {SCHEMA}.{TABLE}")
print(f'\n📊 Total chunks en Supabase: {cur.fetchone()[0]}')
cur.close()
conn.close()

# --- CELDA 15: 🧪 TEST - Buscar artículo 52 ---
conn = get_connection()
cur = conn.cursor()
cur.execute(f"""
    SELECT LEFT(text, 600) 
    FROM {SCHEMA}.{TABLE} 
    WHERE text ILIKE '%artículo 52%' 
    LIMIT 1
""")
result = cur.fetchone()
cur.close()
conn.close()

if result:
    print('✅ Artículo 52 encontrado (debe estar SIN palabras cortadas):')
    print(result[0])
else:
    print('⚠️ No se encontró el artículo 52')


