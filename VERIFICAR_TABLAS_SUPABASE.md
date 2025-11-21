# Verificar Tablas en Supabase

## 🔍 Consultas SQL para Verificar Tablas

### 1. Ver todas las tablas relacionadas con vectores

```sql
-- Ver todas las tablas que contienen 'arbot', 'vector', o 'document'
SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables 
WHERE (table_name LIKE '%arbot%' 
       OR table_name LIKE '%vector%' 
       OR table_name LIKE '%document%')
AND table_type = 'BASE TABLE'
ORDER BY table_schema, table_name;
```

### 2. Ver todas las tablas en todos los schemas

```sql
-- Ver todas las tablas (útil para encontrar tablas ocultas)
SELECT 
    schemaname,
    tablename
FROM pg_tables
WHERE tablename LIKE '%arbot%' 
   OR tablename LIKE '%vector%'
   OR tablename LIKE '%document%'
ORDER BY schemaname, tablename;
```

### 3. Verificar dimensiones de una tabla específica

Si encontraste una tabla (por ejemplo, `arbot_documents` en schema `vecs`):

```sql
-- Ver dimensiones de la columna 'vec'
SELECT 
    table_schema,
    table_name,
    column_name,
    data_type,
    (SELECT atttypmod 
     FROM pg_attribute 
     WHERE attrelid = (
         SELECT oid 
         FROM pg_class 
         WHERE relname = 'arbot_documents'  -- Reemplaza con tu tabla
         AND relnamespace = (
             SELECT oid 
             FROM pg_namespace 
             WHERE nspname = 'vecs'  -- Reemplaza con tu schema
         )
     )
     AND attname = 'vec'
    ) as dimensions
FROM information_schema.columns 
WHERE table_schema = 'vecs'  -- Reemplaza con tu schema
AND table_name = 'arbot_documents'  -- Reemplaza con tu tabla
AND column_name = 'vec';
```

### 4. Ver estructura completa de una tabla

```sql
-- Ver todas las columnas de una tabla
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'vecs'  -- Reemplaza con tu schema
AND table_name = 'arbot_documents'  -- Reemplaza con tu tabla
ORDER BY ordinal_position;
```

## ✅ Interpretación de Resultados

### Si no hay resultados ("No rows returned"):

**Esto es BUENO** ✅ - Significa que:
- Las tablas no existen (fueron eliminadas correctamente)
- O nunca existieron
- Puedes proceder a subir tu documento
- LlamaIndex creará las tablas automáticamente con las dimensiones correctas (384)

### Si encuentras tablas:

1. **Verifica el schema**: Puede ser `vecs`, `public`, o otro
2. **Verifica el nombre**: Puede ser `arbot_documents`, `arbot_vectors`, o variaciones
3. **Verifica las dimensiones**: Debe ser `384` para el modelo actual

### Si las dimensiones son incorrectas (1536 u otro valor):

Ejecuta para eliminar y recrear:

```sql
-- Eliminar tabla con dimensiones incorrectas
DROP TABLE IF EXISTS vecs.arbot_documents CASCADE;
DROP TABLE IF EXISTS vecs.arbot_vectors CASCADE;
DROP TABLE IF EXISTS public.arbot_documents CASCADE;
DROP TABLE IF EXISTS public.arbot_vectors CASCADE;
```

Luego reinicia la aplicación y vuelve a subir el documento.

## 🎯 Próximos Pasos

1. Ejecuta la consulta #1 o #2 para ver qué tablas existen
2. Si no hay tablas → ✅ Listo, puedes subir tu documento
3. Si hay tablas con dimensiones incorrectas → Elimínalas y vuelve a subir
4. Si hay tablas con dimensiones correctas (384) → ✅ Todo está bien

