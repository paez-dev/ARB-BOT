-- ============================================
-- Script para VERIFICAR si el artículo 52 existe en Supabase
-- Ejecutar en Supabase SQL Editor
-- ============================================

-- 1. Buscar el artículo 52 específicamente
SELECT 
    id,
    LEFT(text, 200) as preview,
    LENGTH(text) as longitud,
    metadata->>'file_name' as archivo,
    metadata->>'article' as articulo_metadata
FROM vecs.arbot_documents
WHERE 
    -- Buscar en el texto
    (
        text ILIKE '%artículo 52%' OR
        text ILIKE '%art. 52%' OR
        text ILIKE '%articulo 52%' OR
        text ILIKE '%Artículo 52%' OR
        text ILIKE '%ARTÍCULO 52%'
    )
    -- O buscar en metadata
    OR (
        metadata->>'article' = '52' OR
        metadata->>'article' = '52'
    )
ORDER BY 
    CASE 
        WHEN content ILIKE 'Artículo 52%' THEN 1
        WHEN content ILIKE 'artículo 52%' THEN 2
        WHEN content ILIKE '%Artículo 52%' THEN 3
        ELSE 4
    END,
    LENGTH(text) DESC
LIMIT 10;

-- 2. Contar cuántos chunks mencionan el artículo 52
SELECT 
    'Chunks que mencionan artículo 52' as tipo,
    COUNT(*) as cantidad
FROM vecs.arbot_documents
WHERE 
    content ILIKE '%artículo 52%' OR
    content ILIKE '%art. 52%' OR
    content ILIKE '%articulo 52%';

-- 3. Buscar artículos cercanos (51, 52, 53) para verificar contexto
SELECT 
    id,
    CASE 
        WHEN content ILIKE '%artículo 51%' THEN 'Artículo 51'
        WHEN content ILIKE '%artículo 52%' THEN 'Artículo 52'
        WHEN content ILIKE '%artículo 53%' THEN 'Artículo 53'
        ELSE 'Otro'
    END as articulo_encontrado,
    LEFT(content, 150) as preview,
    LENGTH(content) as longitud
FROM vecs.arbot_documents
WHERE 
    content ILIKE '%artículo 5%'
ORDER BY 
    CASE 
        WHEN content ILIKE '%artículo 51%' THEN 1
        WHEN content ILIKE '%artículo 52%' THEN 2
        WHEN content ILIKE '%artículo 53%' THEN 3
        ELSE 4
    END,
    id
LIMIT 20;

-- 4. Verificar estructura de artículos en general
SELECT 
    'Total chunks' as metrica,
    COUNT(*) as valor
FROM vecs.arbot_documents
UNION ALL
SELECT 
    'Chunks con "artículo" en texto' as metrica,
    COUNT(*) as valor
FROM vecs.arbot_documents
WHERE content ILIKE '%artículo%'
UNION ALL
SELECT 
    'Chunks con metadata article' as metrica,
    COUNT(*) as valor
FROM vecs.arbot_documents
WHERE metadata->>'article' IS NOT NULL;

-- 5. Mostrar distribución de artículos detectados en metadata
SELECT 
    metadata->>'article' as articulo,
    COUNT(*) as cantidad_chunks
FROM vecs.arbot_documents
WHERE metadata->>'article' IS NOT NULL
GROUP BY metadata->>'article'
ORDER BY 
    CASE 
        WHEN metadata->>'article' ~ '^\d+$' THEN (metadata->>'article')::INTEGER
        ELSE 9999
    END
LIMIT 60;

