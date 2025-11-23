-- ============================================
-- Script para recrear tabla arbot_documents
-- con la estructura correcta para LlamaIndex
-- ============================================
-- 
-- IMPORTANTE: Este script ELIMINA todos los datos existentes
-- Ejecutar solo si estás seguro de querer empezar de cero
--
-- Pasos:
-- 1. Conectarte a Supabase SQL Editor
-- 2. Ejecutar este script completo
-- 3. Verificar que la tabla se creó correctamente
-- ============================================

-- Eliminar tabla existente (CUIDADO: esto borra todos los datos)
DROP TABLE IF EXISTS vecs.arbot_documents CASCADE;

-- Crear tabla con estructura correcta para LlamaIndex
-- LlamaIndex SupabaseVectorStore espera:
-- - id: Identificador único
-- - vec/embedding: Vector de embeddings
-- - document: Texto del documento (COLUMNA CRÍTICA)
-- - metadata: Metadatos adicionales en JSONB
CREATE TABLE vecs.arbot_documents (
    id TEXT PRIMARY KEY,
    vec vector(384),              -- Vector de embeddings (384 dimensiones para sentence-transformers)
    document TEXT NOT NULL,       -- Texto del documento (REQUERIDO por LlamaIndex)
    metadata JSONB                -- Metadatos adicionales (file_name, page, etc.)
);

-- Crear índice para búsquedas vectoriales eficientes
CREATE INDEX IF NOT EXISTS arbot_documents_vec_idx 
ON vecs.arbot_documents 
USING ivfflat (vec vector_cosine_ops)
WITH (lists = 100);

-- Crear índice GIN para búsquedas en metadata JSONB
CREATE INDEX IF NOT EXISTS arbot_documents_metadata_idx 
ON vecs.arbot_documents 
USING GIN (metadata);

-- Crear índice para búsquedas por texto (opcional, pero útil)
CREATE INDEX IF NOT EXISTS arbot_documents_document_idx 
ON vecs.arbot_documents 
USING gin (to_tsvector('spanish', document));

-- Comentarios en la tabla y columnas
COMMENT ON TABLE vecs.arbot_documents IS 'Tabla para almacenar documentos vectorizados para RAG con LlamaIndex';
COMMENT ON COLUMN vecs.arbot_documents.id IS 'Identificador único del chunk (formato: nombre_archivo_chunk_index)';
COMMENT ON COLUMN vecs.arbot_documents.vec IS 'Vector de embeddings de 384 dimensiones (sentence-transformers)';
COMMENT ON COLUMN vecs.arbot_documents.document IS 'Texto completo del chunk (REQUERIDO por LlamaIndex)';
COMMENT ON COLUMN vecs.arbot_documents.metadata IS 'Metadatos adicionales: file_name, page, chunk_index, etc.';

-- Verificar que la tabla se creó correctamente
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND table_name = 'arbot_documents'
ORDER BY ordinal_position;

-- Mostrar mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE '✅ Tabla vecs.arbot_documents recreada correctamente con estructura para LlamaIndex';
    RAISE NOTICE '📋 Columnas: id, vec, document, metadata';
    RAISE NOTICE '🔍 Índices creados: vectorial, metadata GIN, texto full-text';
END $$;

