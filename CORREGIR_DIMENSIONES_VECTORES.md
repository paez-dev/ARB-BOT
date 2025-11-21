# Corregir Dimensiones de Vectores en Supabase

## 🔴 Problema

Si ves este error:
```
ValueError: expected 1536 dimensions, not 384
```

Significa que la tabla en Supabase está configurada para 1536 dimensiones (probablemente de OpenAI), pero el modelo actual (`paraphrase-multilingual-MiniLM-L12-v2`) genera 384 dimensiones.

## ✅ Solución

### Opción 1: Eliminar y Recrear la Tabla (RECOMENDADO)

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
2. Abre el **SQL Editor** (menú lateral izquierdo)
3. Ejecuta este SQL para eliminar las tablas existentes:

```sql
-- Eliminar tablas existentes con dimensiones incorrectas
DROP TABLE IF EXISTS vecs.arbot_documents CASCADE;
DROP TABLE IF EXISTS vecs.arbot_vectors CASCADE;

-- También eliminar el schema si existe
DROP SCHEMA IF EXISTS vecs CASCADE;
```

4. **Reinicia tu aplicación** en Railway
5. La próxima vez que subas un documento, LlamaIndex creará automáticamente las tablas con las dimensiones correctas (384)

### Opción 2: Modificar la Tabla Existente

Si prefieres mantener los datos existentes (aunque tendrás que reprocesar los documentos):

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
2. Abre el **SQL Editor**
3. Ejecuta este SQL para modificar la tabla:

```sql
-- Verificar dimensiones actuales
SELECT 
    table_name, 
    column_name,
    (SELECT atttypmod FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = table_name) AND attname = column_name) as dimensions
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND column_name = 'vec';

-- Modificar la columna vec para aceptar 384 dimensiones
ALTER TABLE vecs.arbot_documents 
ALTER COLUMN vec TYPE vector(384);

-- Si existe arbot_vectors, también modificarla
ALTER TABLE vecs.arbot_vectors 
ALTER COLUMN vec TYPE vector(384);
```

**⚠️ Nota**: Si ya tienes datos en la tabla, estos se perderán porque las dimensiones no coinciden. Es mejor usar la Opción 1.

## 🔍 Verificar Dimensiones Correctas

Después de corregir, verifica que las tablas tengan las dimensiones correctas:

```sql
-- Verificar dimensiones de la tabla
SELECT 
    table_name,
    column_name,
    data_type,
    (SELECT atttypmod FROM pg_attribute 
     WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = table_name) 
     AND attname = column_name) as dimensions
FROM information_schema.columns 
WHERE table_schema = 'vecs' 
AND column_name = 'vec';
```

Deberías ver `384` en la columna `dimensions`.

## 📊 Modelos y sus Dimensiones

| Modelo | Dimensiones |
|--------|--------------|
| `paraphrase-multilingual-MiniLM-L12-v2` (actual) | 384 |
| `text-embedding-ada-002` (OpenAI) | 1536 |
| `text-embedding-3-small` (OpenAI) | 1536 |
| `text-embedding-3-large` (OpenAI) | 3072 |

## 🎯 Después de Corregir

1. **Elimina cualquier documento procesado anteriormente** (si usaste la Opción 1)
2. **Vuelve a subir tu PDF** para que se procese con las dimensiones correctas
3. El sistema debería funcionar correctamente sin errores de dimensiones

## 💡 Prevención Futura

Si cambias de modelo de embeddings en el futuro:
- Asegúrate de que las dimensiones coincidan
- O elimina y recrea las tablas antes de usar el nuevo modelo

