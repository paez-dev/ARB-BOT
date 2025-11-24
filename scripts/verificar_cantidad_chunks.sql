-- ============================================
-- Script para VERIFICAR cantidad de chunks vs páginas del PDF
-- Ejecutar en Supabase SQL Editor
-- ============================================

-- 1. Contar total de chunks en la base de datos
SELECT 
    'Total chunks en Supabase' as metrica,
    COUNT(*) as valor
FROM vecs.arbot_documents;

-- 2. Contar chunks por archivo
SELECT 
    metadata->>'file_name' as archivo,
    COUNT(*) as cantidad_chunks,
    AVG(LENGTH(content)) as promedio_caracteres,
    MIN(LENGTH(content)) as min_caracteres,
    MAX(LENGTH(content)) as max_caracteres,
    SUM(LENGTH(content)) as total_caracteres
FROM vecs.arbot_documents
WHERE metadata->>'file_name' IS NOT NULL
GROUP BY metadata->>'file_name'
ORDER BY cantidad_chunks DESC;

-- 3. Verificar distribución de tamaños de chunks
SELECT 
    CASE 
        WHEN LENGTH(content) < 100 THEN 'Muy pequeño (<100)'
        WHEN LENGTH(content) < 500 THEN 'Pequeño (100-500)'
        WHEN LENGTH(content) < 1000 THEN 'Mediano (500-1000)'
        WHEN LENGTH(content) < 2000 THEN 'Grande (1000-2000)'
        WHEN LENGTH(content) < 5000 THEN 'Muy grande (2000-5000)'
        ELSE 'Extremo (>5000)'
    END as tamano,
    COUNT(*) as cantidad,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM vecs.arbot_documents), 2) as porcentaje
FROM vecs.arbot_documents
GROUP BY tamano
ORDER BY 
    CASE tamano
        WHEN 'Muy pequeño (<100)' THEN 1
        WHEN 'Pequeño (100-500)' THEN 2
        WHEN 'Mediano (500-1000)' THEN 3
        WHEN 'Grande (1000-2000)' THEN 4
        WHEN 'Muy grande (2000-5000)' THEN 5
        ELSE 6
    END;

-- 4. Verificar si hay chunks vacíos o muy pequeños (posible problema)
SELECT 
    'Chunks vacíos o muy pequeños' as problema,
    COUNT(*) as cantidad
FROM vecs.arbot_documents
WHERE content IS NULL 
   OR content = '' 
   OR LENGTH(content) < 50;

-- 5. Verificar chunks con metadata de página
SELECT 
    'Chunks con metadata page' as tipo,
    COUNT(*) as cantidad
FROM vecs.arbot_documents
WHERE metadata->>'page' IS NOT NULL;

-- 6. Verificar si hay información sobre páginas en metadata
SELECT 
    metadata->>'file_name' as archivo,
    COUNT(DISTINCT metadata->>'page') as paginas_diferentes,
    COUNT(*) as total_chunks
FROM vecs.arbot_documents
WHERE metadata->>'file_name' IS NOT NULL
GROUP BY metadata->>'file_name';

-- 7. Ejemplo de chunks pequeños (posible problema de chunking)
SELECT 
    id,
    LEFT(content, 100) as preview,
    LENGTH(content) as longitud,
    metadata->>'file_name' as archivo,
    metadata->>'page' as pagina,
    metadata->>'chunk_index' as indice
FROM vecs.arbot_documents
WHERE LENGTH(content) < 200
ORDER BY LENGTH(content) ASC
LIMIT 20;

-- 8. Resumen: ¿Hay suficientes chunks?
-- Para un PDF de ~100 páginas, esperarías ~200-500 chunks (dependiendo del tamaño)
SELECT 
    '📊 RESUMEN' as categoria,
    '' as detalle
UNION ALL
SELECT 
    'Total chunks' as categoria,
    COUNT(*)::text as detalle
FROM vecs.arbot_documents
UNION ALL
SELECT 
    'Chunks < 100 caracteres (posible problema)' as categoria,
    COUNT(*)::text as detalle
FROM vecs.arbot_documents
WHERE LENGTH(content) < 100
UNION ALL
SELECT 
    'Chunks > 2000 caracteres (muy grandes)' as categoria,
    COUNT(*)::text as detalle
FROM vecs.arbot_documents
WHERE LENGTH(content) > 2000
UNION ALL
SELECT 
    'Promedio caracteres por chunk' as categoria,
    ROUND(AVG(LENGTH(content)), 0)::text as detalle
FROM vecs.arbot_documents;

-- ⚠️ Si ves muy pocos chunks (< 100 para un PDF grande):
-- 1. El chunking puede estar eliminando contenido
-- 2. Puede haber un error en la subida
-- 3. El PDF puede no haberse procesado completamente

