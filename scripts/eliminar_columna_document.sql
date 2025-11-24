-- ============================================
-- Script para ELIMINAR columna 'document' y usar solo 'content'
-- Ejecutar en Supabase SQL Editor
-- ============================================
-- 
-- ⚠️ IMPORTANTE: Este script:
-- 1. Verifica que todos los datos estén en 'content'
-- 2. Elimina la columna 'document' si existe
-- 3. Verifica que todo esté correcto
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

-- Paso 2: Verificar que todos los datos estén en 'content'
SELECT 
    'Verificación de datos' as tipo,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE content IS NOT NULL AND content != '') as con_content,
    COUNT(*) FILTER (WHERE document IS NOT NULL AND document != '') as con_document,
    COUNT(*) FILTER (WHERE (content IS NULL OR content = '') AND (document IS NOT NULL AND document != '')) as solo_en_document
FROM vecs.arbot_documents;

-- Paso 3: Si hay datos solo en 'document', copiarlos a 'content' primero
UPDATE vecs.arbot_documents
SET content = document
WHERE (content IS NULL OR content = '')
  AND (document IS NOT NULL AND document != '');

-- Paso 4: Verificar que todos tienen 'content' ahora
SELECT 
    'Verificación post-copia' as tipo,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE content IS NOT NULL AND content != '') as con_content,
    COUNT(*) FILTER (WHERE (content IS NULL OR content = '') AND (document IS NOT NULL AND document != '')) as solo_en_document
FROM vecs.arbot_documents;

-- Paso 5: Eliminar columna 'document' si existe
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'vecs' 
        AND table_name = 'arbot_documents'
        AND column_name = 'document'
    ) THEN
        ALTER TABLE vecs.arbot_documents 
        DROP COLUMN document;
        
        RAISE NOTICE '✅ Columna "document" eliminada';
    ELSE
        RAISE NOTICE 'ℹ️ Columna "document" no existe';
    END IF;
END $$;

-- Paso 6: Verificar estructura final
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND table_name = 'arbot_documents'
ORDER BY ordinal_position;

-- Paso 7: Resumen final
SELECT 
    '📊 RESUMEN FINAL' as categoria,
    '' as detalle
UNION ALL
SELECT 
    'Total documentos' as categoria,
    COUNT(*)::text as detalle
FROM vecs.arbot_documents
UNION ALL
SELECT 
    'Con content válido' as categoria,
    COUNT(*)::text as detalle
FROM vecs.arbot_documents
WHERE content IS NOT NULL AND content != ''
UNION ALL
SELECT 
    'Estructura final' as categoria,
    'id, vec, content, metadata' as detalle;

-- ✅ Después de ejecutar este script:
-- 1. La tabla solo tendrá la columna 'content'
-- 2. Todos los datos estarán en 'content'
-- 3. El código del bot usará solo 'content'
-- 4. Reinicia la aplicación para que los cambios surtan efecto

