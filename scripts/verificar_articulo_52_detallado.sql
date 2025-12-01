-- ============================================
-- Script DETALLADO para verificar artículo 52
-- Ejecutar en Supabase SQL Editor
-- ============================================

-- 1. Buscar TODAS las menciones del artículo 52
SELECT 
    id,
    LEFT(text, 300) as preview,
    LENGTH(text) as longitud,
    CASE 
        WHEN text ILIKE 'Artículo 52%' THEN '✅ Empieza con Artículo 52'
        WHEN text ILIKE '%Artículo 52%' THEN '✅ Contiene Artículo 52'
        WHEN text ILIKE '%art. 52%' THEN '✅ Contiene art. 52'
        ELSE '⚠️ Menciona 52'
    END as tipo_mencio,
    metadata->>'file_name' as archivo
FROM vecs.arbot_documents
WHERE 
    text ILIKE '%52%' AND (
        text ILIKE '%artículo 52%' OR
        text ILIKE '%art. 52%' OR
        text ILIKE '%articulo 52%' OR
        text ILIKE '%Artículo 52%' OR
        text ILIKE '%ARTÍCULO 52%' OR
        text ILIKE '%Art. 52%'
    )
ORDER BY 
    CASE 
        WHEN text ILIKE 'Artículo 52%' THEN 1
        WHEN text ILIKE '%Artículo 52%' THEN 2
        WHEN text ILIKE '%art. 52%' THEN 3
        ELSE 4
    END,
    LENGTH(content) DESC;

-- 2. Ver si hay chunks que empiezan con "Artículo" (cualquier número)
SELECT 
    'Chunks que empiezan con "Artículo"' as tipo,
    COUNT(*) as cantidad
FROM vecs.arbot_documents
WHERE content ~* '^Artículo\s+\d+';

-- 3. Ver distribución de artículos mencionados (extraer números)
-- Usar subconsulta para simplificar
SELECT 
    numero_articulo,
    COUNT(*) as cantidad_chunks
FROM (
    SELECT 
        CASE 
            WHEN text ~* 'Artículo\s+(\d+)' THEN 
                (regexp_match(text, 'Artículo\s+(\d+)', 'i'))[1]
            ELSE 'No detectado'
        END as numero_articulo
    FROM vecs.arbot_documents
    WHERE content ILIKE '%artículo%'
) subquery
GROUP BY numero_articulo
ORDER BY 
    CASE 
        WHEN numero_articulo ~ '^\d+$' THEN numero_articulo::INTEGER
        ELSE 9999
    END
LIMIT 60;

-- 4. Ver chunks que deberían tener metadata article pero no la tienen
SELECT 
    id,
    LEFT(text, 200) as preview,
    CASE 
        WHEN content ~* '^Artículo\s+(\d+)' THEN 
            (regexp_match(content, '^Artículo\s+(\d+)', 'i'))[1]
        WHEN content ~* 'Artículo\s+(\d+)' THEN 
            (regexp_match(content, 'Artículo\s+(\d+)', 'i'))[1]
        ELSE NULL
    END as articulo_detectado,
    metadata->>'article' as articulo_metadata,
    CASE 
        WHEN metadata->>'article' IS NULL THEN '❌ Sin metadata'
        ELSE '✅ Con metadata'
    END as estado_metadata
FROM vecs.arbot_documents
WHERE content ILIKE '%artículo%'
LIMIT 20;

-- 5. Resumen: ¿Por qué no se encuentra el artículo 52?
SELECT 
    '¿Existe artículo 52 en texto?' as pregunta,
    CASE 
        WHEN COUNT(*) > 0 THEN CONCAT('✅ SÍ (', COUNT(*), ' chunks)')
        ELSE '❌ NO'
    END as respuesta
FROM vecs.arbot_documents
WHERE content ILIKE '%artículo 52%' OR content ILIKE '%art. 52%'
UNION ALL
SELECT 
    '¿Hay metadata article para artículo 52?' as pregunta,
    CASE 
        WHEN COUNT(*) > 0 THEN CONCAT('✅ SÍ (', COUNT(*), ' chunks)')
        ELSE '❌ NO'
    END as respuesta
FROM vecs.arbot_documents
WHERE metadata->>'article' = '52';

