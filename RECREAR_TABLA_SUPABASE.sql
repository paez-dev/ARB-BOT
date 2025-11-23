-- ============================================
-- Script para recrear tabla de Supabase con estructura correcta
-- Ejecutar en Supabase SQL Editor
-- ============================================

-- 1. Eliminar tabla existente (CUIDADO: Esto elimina TODOS los datos)
DROP TABLE IF EXISTS vecs.arbot_documents CASCADE;

-- 2. Crear tabla con estructura correcta según buenas prácticas
-- LlamaIndex espera: id, vec/embedding, document, metadata
CREATE TABLE IF NOT EXISTS vecs.arbot_documents (
    id TEXT PRIMARY KEY,
    vec vector(384),              -- Embedding vector (384 dimensiones para sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
    document TEXT NOT NULL,       -- Texto del documento (COLUMNA REQUERIDA por LlamaIndex)
    metadata JSONB                -- Metadatos adicionales (file_name, page, section, etc.)
);

-- 3. Crear índice para búsquedas vectoriales eficientes
CREATE INDEX IF NOT EXISTS arbot_documents_vec_idx 
ON vecs.arbot_documents 
USING ivfflat (vec vector_cosine_ops)
WITH (lists = 100);

-- 4. Crear índice GIN para búsquedas en metadata JSONB
CREATE INDEX IF NOT EXISTS arbot_documents_metadata_idx 
ON vecs.arbot_documents 
USING GIN (metadata);

-- 5. Crear índice para búsquedas de texto en document
CREATE INDEX IF NOT EXISTS arbot_documents_document_idx 
ON vecs.arbot_documents 
USING gin (to_tsvector('spanish', document));

-- 6. Verificar estructura de la tabla
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND table_name = 'arbot_documents'
ORDER BY ordinal_position;

-- ✅ Tabla recreada correctamente con estructura:
--    - id: TEXT (PRIMARY KEY)
--    - vec: vector(384) (Embedding)
--    - document: TEXT NOT NULL (Texto del documento - REQUERIDO por LlamaIndex)
--    - metadata: JSONB (Metadatos adicionales)

