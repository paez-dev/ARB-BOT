# Solución Definitiva: Corregir Dimensiones sin Eliminar Tabla

## 🔴 Problema Persistente

La tabla `vecs.arbot_documents` tiene 1536 dimensiones pero el modelo genera 384. Aunque intentaste eliminar la tabla, parece que se está recreando o no se eliminó correctamente.

## ✅ Solución Directa: Modificar la Tabla

En lugar de eliminar, vamos a modificar la tabla directamente:

### Paso 1: Eliminar todos los datos existentes

```sql
-- Eliminar todos los datos de la tabla
DELETE FROM vecs.arbot_documents;
```

### Paso 2: Modificar las dimensiones de la columna

```sql
-- Cambiar las dimensiones de vector(1536) a vector(384)
ALTER TABLE vecs.arbot_documents 
ALTER COLUMN vec TYPE vector(384);
```

### Paso 3: Verificar que funcionó

```sql
-- Verificar dimensiones
SELECT 
    (SELECT atttypmod 
     FROM pg_attribute 
     WHERE attrelid = (
         SELECT oid 
         FROM pg_class 
         WHERE relname = 'arbot_documents'
         AND relnamespace = (
             SELECT oid 
             FROM pg_namespace 
             WHERE nspname = 'vecs'
         )
     )
     AND attname = 'vec'
    ) as dimensions;
```

Deberías ver `384`.

## 🔧 Si el ALTER TABLE falla

Si el `ALTER TABLE` falla con un error, intenta esto:

```sql
-- 1. Eliminar datos
DELETE FROM vecs.arbot_documents;

-- 2. Eliminar índices que puedan estar causando problemas
DROP INDEX IF EXISTS vecs.arbot_documents_embedding_idx CASCADE;
DROP INDEX IF EXISTS vecs.arbot_vectors_embedding_idx CASCADE;

-- 3. Modificar dimensiones
ALTER TABLE vecs.arbot_documents 
ALTER COLUMN vec TYPE vector(384);

-- 4. Si aún falla, recrear la columna
ALTER TABLE vecs.arbot_documents DROP COLUMN vec;
ALTER TABLE vecs.arbot_documents ADD COLUMN vec vector(384);
```

## 🎯 Después de Corregir

1. **Reinicia la aplicación** en Railway
2. **Vuelve a subir tu PDF**
3. El sistema debería funcionar correctamente ahora

## 🔍 Verificar que No se Recrea con Dimensiones Incorrectas

Si después de corregir, la tabla se vuelve a crear con 1536 dimensiones, puede ser que LlamaIndex tenga alguna configuración. En ese caso, verifica en Supabase si hay alguna función o trigger que esté recreando la tabla.

```sql
-- Ver si hay funciones o triggers relacionados
SELECT 
    routine_name,
    routine_definition
FROM information_schema.routines
WHERE routine_schema = 'vecs'
AND routine_definition LIKE '%1536%';
```

## 💡 Alternativa: Usar un Modelo con 1536 Dimensiones

Si nada funciona, podrías cambiar el modelo de embeddings a uno que genere 1536 dimensiones, pero esto requeriría cambiar el código. Es mejor corregir la tabla.

