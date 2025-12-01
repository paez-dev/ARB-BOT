# 🗄️ Guía: Recrear Tabla en Supabase

## ⚠️ ADVERTENCIA

Este proceso **ELIMINA TODOS los datos** existentes en Supabase. Úsalo solo cuando quieras empezar desde cero con una estructura limpia.

## 📋 Pasos

### 1. Abrir Supabase SQL Editor

1. Ve a tu proyecto en Supabase
2. Navega a **SQL Editor** (menú lateral)
3. Haz clic en **New Query**

### 2. Ejecutar Script SQL

Copia y pega el contenido de `RECREAR_TABLA_SUPABASE.sql` en el editor SQL.

O ejecuta directamente:

```sql
-- Eliminar tabla existente
DROP TABLE IF EXISTS vecs.arbot_documents CASCADE;

-- Crear tabla con estructura correcta
CREATE TABLE IF NOT EXISTS vecs.arbot_documents (
    id TEXT PRIMARY KEY,
    vec vector(384),
    text TEXT NOT NULL,
    metadata JSONB
);

-- Crear índices
CREATE INDEX IF NOT EXISTS arbot_documents_vec_idx 
ON vecs.arbot_documents 
USING ivfflat (vec vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS arbot_documents_metadata_idx 
ON vecs.arbot_documents 
USING GIN (metadata);

CREATE INDEX IF NOT EXISTS arbot_documents_text_idx 
ON vecs.arbot_documents 
USING gin (to_tsvector('spanish', text));
```

### 3. Verificar Estructura

Después de ejecutar, verifica que la tabla tenga la estructura correcta:

```sql
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND table_name = 'arbot_documents'
ORDER BY ordinal_position;
```

**Resultado esperado:**
- `id` (TEXT)
- `vec` (USER-DEFINED, vector)
- `text` (TEXT)
- `metadata` (JSONB)

## ✅ Estructura Final

```
vecs.arbot_documents
├── id (TEXT, PRIMARY KEY)
├── vec (vector(384)) - Embedding vector
├── text (TEXT) - Texto del chunk (estándar LlamaIndex)
└── metadata (JSONB) - Metadatos completos
    ├── source: Nombre del archivo
    ├── title: TÍTULO I, TÍTULO II, etc.
    ├── chapter: CAPÍTULO I, CAPÍTULO II, etc.
    ├── article: Artículo 1, Artículo 52, etc.
    ├── paragraph: Parágrafo 1, etc.
    ├── page: Número de página
    ├── keywords: Lista de palabras clave
    └── chunk_tokens: Tamaño en tokens
```

## 📝 Próximos Pasos

1. ✅ Tabla recreada con estructura correcta
2. 📤 Ejecuta el notebook de Colab (`INGESTA_FINAL_RAG.ipynb`)
3. 🔄 Procesa tus documentos PDF
4. ✅ Los chunks se subirán automáticamente

## 🔍 Verificar que Todo Funciona

Después de procesar un documento, verifica:

```sql
SELECT 
    COUNT(*) as total_chunks,
    COUNT(DISTINCT metadata->>'article') as articulos_unicos,
    AVG(LENGTH(content)) as promedio_caracteres
FROM vecs.arbot_documents;
```

## ⚠️ Si Ya Tienes Datos

Si ya tienes datos y quieres migrarlos:

1. **Opción 1:** Exportar datos antes de eliminar
2. **Opción 2:** Usar `scripts/eliminar_columna_document.sql` si solo necesitas cambiar columnas
3. **Opción 3:** Re-procesar documentos desde Colab (recomendado)

## 📚 Archivos Relacionados

- `RECREAR_TABLA_SUPABASE.sql` - Script SQL completo
- `INGESTA_FINAL_RAG.ipynb` - Notebook para procesar documentos (Colab)
- `GUIA_CHUNKING_JERARQUICO.md` - Guía del chunking

