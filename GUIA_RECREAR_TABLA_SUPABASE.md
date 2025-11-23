# 🔄 Guía: Recrear Tabla en Supabase con Estructura Correcta

Esta guía te ayudará a recrear la tabla `arbot_documents` en Supabase con la estructura correcta que espera LlamaIndex.

## 📋 ¿Por qué hacer esto?

LlamaIndex `SupabaseVectorStore` espera que el texto del documento esté en una columna `document` dedicada, no solo en `metadata`. La estructura correcta es:

- `id`: Identificador único del chunk
- `vec`: Vector de embeddings (384 dimensiones)
- `document`: **Texto del chunk (REQUERIDO por LlamaIndex)**
- `metadata`: Metadatos adicionales en JSONB

## ⚠️ ADVERTENCIA

**Este proceso ELIMINARÁ todos los datos existentes en la tabla.** Asegúrate de:
1. Haber procesado y subido tus documentos desde Colab después de recrear la tabla
2. Tener un backup si es necesario

## 🚀 Pasos para Recrear la Tabla

### 1. Conectarte a Supabase SQL Editor

1. Ve a tu proyecto en [Supabase Dashboard](https://app.supabase.com)
2. Navega a **SQL Editor** en el menú lateral
3. Haz clic en **New Query**

### 2. Ejecutar el Script SQL

1. Abre el archivo `scripts/recrear_tabla_supabase.sql` en este repositorio
2. Copia todo el contenido del script
3. Pégalo en el SQL Editor de Supabase
4. Haz clic en **Run** o presiona `Ctrl+Enter` (o `Cmd+Enter` en Mac)

### 3. Verificar que se Creó Correctamente

El script incluye una verificación automática al final. Deberías ver:

```
✅ Tabla vecs.arbot_documents recreada correctamente con estructura para LlamaIndex
📋 Columnas: id, vec, document, metadata
🔍 Índices creados: vectorial, metadata GIN, texto full-text
```

También puedes verificar manualmente ejecutando:

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

Deberías ver 4 columnas:
- `id` (text)
- `vec` (USER-DEFINED - vector)
- `document` (text)
- `metadata` (jsonb)

## 📤 Procesar Documentos desde Colab

Después de recrear la tabla:

1. **Abre el notebook** `INGESTA_DOCUMENTOS_COLAB.ipynb` en Google Colab
2. **Ejecuta todas las celdas** de configuración
3. **Sube tus PDFs** y procesa los documentos
4. El notebook ahora insertará el texto en la columna `document` correctamente

## ✅ Verificar que Funciona

1. **Desde Colab**: Ejecuta la función de verificación:
   ```python
   verify_embeddings_uploaded("nombre_archivo.pdf")
   ```

2. **Desde Supabase SQL Editor**:
   ```sql
   SELECT 
       COUNT(*) as total_chunks,
       COUNT(DISTINCT metadata->>'file_name') as documentos,
       AVG(LENGTH(document)) as avg_text_length
   FROM vecs.arbot_documents;
   ```

3. **Desde el Bot**: Prueba hacer una pregunta que debería encontrar contexto en tus documentos

## 🔍 Estructura Final de la Tabla

```sql
CREATE TABLE vecs.arbot_documents (
    id TEXT PRIMARY KEY,
    vec vector(384),              -- Vector de embeddings
    document TEXT NOT NULL,       -- Texto del documento (REQUERIDO)
    metadata JSONB                -- Metadatos adicionales
);
```

## 📝 Notas

- La columna `document` es **NOT NULL** para asegurar que siempre haya texto
- Los índices creados optimizan:
  - Búsquedas vectoriales (índice ivfflat)
  - Búsquedas en metadata (índice GIN)
  - Búsquedas de texto completo (índice GIN con to_tsvector)

## 🆘 Solución de Problemas

### Error: "column document does not exist"
- Asegúrate de haber ejecutado el script SQL completo
- Verifica que la tabla se creó en el schema `vecs`

### Error: "La tabla no tiene la columna 'document'"
- El notebook detectará automáticamente si falta la columna
- Ejecuta el script SQL nuevamente

### Los documentos no se encuentran
- Verifica que hayas procesado los documentos DESPUÉS de recrear la tabla
- Revisa que el texto se esté insertando en la columna `document`

## 🎯 Próximos Pasos

1. ✅ Recrear la tabla con el script SQL
2. ✅ Procesar documentos desde Colab
3. ✅ Verificar que el bot encuentra el contexto correctamente

¡Listo! Tu sistema RAG ahora usa la estructura correcta que espera LlamaIndex.

