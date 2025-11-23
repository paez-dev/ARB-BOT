-- ============================================
-- Script para renombrar columna document a content
-- SIN PERDER DATOS - Solo renombra la columna
-- ============================================
-- 
-- IMPORTANTE: Este script NO elimina datos
-- Solo renombra la columna 'document' a 'content'
-- para que LlamaIndex la reconozca correctamente
--
-- Pasos:
-- 1. Conectarte a Supabase SQL Editor
-- 2. Ejecutar este script completo
-- 3. Verificar que la columna se renombró correctamente
-- ============================================

-- Verificar que la columna document existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'vecs' 
        AND table_name = 'arbot_documents' 
        AND column_name = 'document'
    ) THEN
        RAISE EXCEPTION 'La columna "document" no existe. Verifica que la tabla tenga la estructura correcta.';
    END IF;
END $$;

-- Renombrar columna document a content (sin perder datos)
ALTER TABLE vecs.arbot_documents 
RENAME COLUMN document TO content;

-- Actualizar comentario de la columna
COMMENT ON COLUMN vecs.arbot_documents.content IS 'Texto del documento (REQUERIDO por LlamaIndex)';

-- Actualizar índice de texto completo si existe (usar content en lugar de document)
DROP INDEX IF EXISTS vecs.arbot_documents_document_idx;
CREATE INDEX IF NOT EXISTS arbot_documents_content_idx 
ON vecs.arbot_documents 
USING gin (to_tsvector('spanish', content));

-- Verificar que el cambio se aplicó correctamente
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
    RAISE NOTICE '✅ Columna renombrada correctamente: document → content';
    RAISE NOTICE '📋 Estructura actual: id, vec, content, metadata';
    RAISE NOTICE '🔍 LlamaIndex ahora debería leer el texto correctamente';
END $$;

