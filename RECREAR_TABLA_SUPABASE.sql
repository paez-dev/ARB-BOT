-- ============================================
-- Script para RECREAR tabla de Supabase con estructura correcta
-- Ejecutar en Supabase SQL Editor
-- ============================================
-- 
-- ⚠️ ADVERTENCIA: Este script ELIMINA TODOS los datos existentes
-- Úsalo solo cuando quieras empezar desde cero con estructura limpia
-- ============================================

-- Paso 1: Eliminar tabla existente (CUIDADO: Esto elimina TODOS los datos)
DROP TABLE IF EXISTS vecs.arbot_documents CASCADE;

-- Paso 2: Crear tabla con estructura correcta
-- Estructura optimizada: id, vec, content, metadata
CREATE TABLE IF NOT EXISTS vecs.arbot_documents (
    id TEXT PRIMARY KEY,
    vec vector(384),              -- Embedding vector (384 dimensiones)
    content TEXT NOT NULL,         -- Texto del chunk (COLUMNA ESTÁNDAR)
    metadata JSONB                 -- Metadatos (title, chapter, article, page, keywords, etc.)
);

-- Paso 3: Crear índice vectorial para búsquedas eficientes (ivfflat)
CREATE INDEX IF NOT EXISTS arbot_documents_vec_idx 
ON vecs.arbot_documents 
USING ivfflat (vec vector_cosine_ops)
WITH (lists = 100);

-- Paso 4: Crear índice GIN para búsquedas en metadata JSONB
CREATE INDEX IF NOT EXISTS arbot_documents_metadata_idx 
ON vecs.arbot_documents 
USING GIN (metadata);

-- Paso 5: Crear índice para búsquedas de texto en content (opcional, mejora búsquedas híbridas)
CREATE INDEX IF NOT EXISTS arbot_documents_content_idx 
ON vecs.arbot_documents 
USING gin (to_tsvector('spanish', content));

-- Paso 6: Verificar estructura de la tabla
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND table_name = 'arbot_documents'
ORDER BY ordinal_position;

-- Paso 7: Verificar índices creados
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'vecs' 
AND tablename = 'arbot_documents';

-- ✅ Tabla recreada correctamente con estructura:
--    - id: TEXT (PRIMARY KEY)
--    - vec: vector(384) (Embedding vector)
--    - content: TEXT NOT NULL (Texto del chunk - ESTÁNDAR)
--    - metadata: JSONB (Metadatos: title, chapter, article, page, keywords, etc.)
--
-- ✅ Índices creados:
--    - Vectorial (ivfflat) para búsquedas por similitud
--    - GIN en metadata para búsquedas por artículo/título/capítulo
--    - GIN en content para búsquedas de texto completo
--
-- 📝 Próximos pasos:
--    1. Ejecuta el notebook de Colab para procesar documentos
--    2. Los chunks se subirán automáticamente con esta estructura

