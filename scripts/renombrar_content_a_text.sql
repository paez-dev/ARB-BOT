-- ============================================
-- Script para RENOMBRAR columna 'content' a 'text'
-- Ejecutar en Supabase SQL Editor
-- ============================================
-- 
-- Este script:
-- 1. Verifica que existe columna 'content'
-- 2. Renombra 'content' a 'text' (estándar LlamaIndex)
-- 3. Actualiza índices
-- 4. Verifica que todo esté correcto
-- ============================================

-- Paso 1: Verificar estructura actual
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND table_name = 'arbot_documents'
ORDER BY ordinal_position;

-- Paso 2: Verificar que existe columna 'content'
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'vecs' 
        AND table_name = 'arbot_documents'
        AND column_name = 'content'
    ) THEN
        RAISE EXCEPTION 'La columna "content" no existe. No hay nada que renombrar.';
    END IF;
END $$;

-- Paso 3: Eliminar índice antiguo si existe
DROP INDEX IF EXISTS vecs.arbot_documents_content_idx;

-- Paso 4: Renombrar columna 'content' a 'text'
ALTER TABLE vecs.arbot_documents 
RENAME COLUMN content TO text;

-- Paso 5: Crear nuevo índice con nombre correcto
CREATE INDEX IF NOT EXISTS arbot_documents_text_idx 
ON vecs.arbot_documents 
USING gin (to_tsvector('spanish', text));

-- Paso 6: Verificar estructura final
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND table_name = 'arbot_documents'
ORDER BY ordinal_position;

-- Paso 7: Verificar índices
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'vecs' 
AND tablename = 'arbot_documents'
AND indexname LIKE '%text%';

-- Paso 8: Verificar datos
SELECT 
    'Verificación' as tipo,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE text IS NOT NULL AND text != '') as con_texto,
    COUNT(*) FILTER (WHERE text IS NULL OR text = '') as sin_texto
FROM vecs.arbot_documents;

-- ✅ Después de ejecutar este script:
-- 1. La columna se llama 'text' (estándar LlamaIndex)
-- 2. Todos los datos están preservados
-- 3. Los índices están actualizados
-- 4. Reinicia el bot en Railway para que los cambios surtan efecto

