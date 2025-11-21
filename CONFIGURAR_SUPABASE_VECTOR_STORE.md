# Configurar Supabase como Vector Store (pgvector)

Esta guía te ayudará a configurar Supabase con pgvector para usar LlamaIndex como vector store persistente.

## ✅ Ventajas de usar Supabase pgvector

- **Persistencia automática**: Los vectores se guardan automáticamente en PostgreSQL
- **Sin archivos manuales**: No necesitas guardar/cargar índices manualmente
- **Escalable**: Supabase maneja el almacenamiento y búsqueda eficientemente
- **Gratis**: El plan gratuito de Supabase es suficiente para proyectos pequeños/medianos

## 📋 Requisitos Previos

1. Tener un proyecto en Supabase (gratis): https://supabase.com
2. Tener las credenciales de tu proyecto

## 🔧 Paso 1: Habilitar pgvector en Supabase

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
2. Abre el **SQL Editor** (menú lateral izquierdo)
3. Ejecuta este SQL para habilitar la extensión pgvector:

```sql
-- Habilitar extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;
```

4. Verifica que se creó correctamente:

```sql
-- Verificar extensión
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 🔧 Paso 2: Obtener Connection String de PostgreSQL

Hay varias formas de obtener la connection string. Prueba estas opciones:

### Opción A: Desde Settings → Database

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
2. En el menú lateral, ve a **Settings** (⚙️) → **Database**
3. Busca la sección **"Connection string"** o **"Connection pooling"**
4. Si ves **"URI"** o **"Connection string"**, cópiala
5. Si no la ves, ve a la **Opción B** o **C** abajo

### Opción B: Construir la Connection String Manualmente

Si no encuentras la connection string lista, puedes construirla:

1. Ve a **Settings** → **Database**
2. Busca **"Connection info"** o **"Database settings"**
3. Necesitarás estos datos:
   - **Host**: `db.xxxxx.supabase.co` (reemplaza `xxxxx` con tu ID de proyecto)
   - **Port**: `5432` (siempre)
   - **Database**: `postgres` (siempre)
   - **User**: `postgres` (siempre)
   - **Password**: Tu contraseña de base de datos

4. La connection string se construye así:
   ```
   postgresql://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres
   ```

### Opción C: Obtener Password y Construir URL

1. Ve a **Settings** → **Database**
2. Busca **"Database password"** o **"Reset database password"**
3. Si no conoces tu password:
   - Haz clic en **"Reset database password"**
   - Copia la nueva contraseña (guárdala bien)
4. Para obtener el **Host**:
   - Ve a **Settings** → **API**
   - Tu **Project URL** es: `https://xxxxx.supabase.co`
   - El **Host** de la DB es: `db.xxxxx.supabase.co` (agrega `db.` al inicio)

5. Construye la connection string:
   ```
   postgresql://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres
   ```

**Ejemplo completo:**
```
postgresql://postgres:mi_password_segura@db.abcdefghijklmnop.supabase.co:5432/postgres
```

## 🔧 Paso 3: Configurar Variables de Entorno

Agrega estas variables a tu archivo `.env` o en Railway:

### Opción 1: Connection String Completa (Recomendado)

```bash
SUPABASE_DB_URL=postgresql://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

### Opción 2: Password Separada (El sistema construye la URL)

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_DB_PASSWORD=tu_password_de_base_de_datos
```

**Nota**: Si usas la Opción 2, el sistema intentará construir la URL automáticamente desde `SUPABASE_URL`.

## 🔧 Paso 4: Verificar Configuración

Una vez configurado, cuando inicies la aplicación:

1. Deberías ver en los logs:
   ```
   🔧 Inicializando LlamaIndex con Supabase pgvector...
   ✅ Índice cargado desde Supabase
   ✅ LlamaIndex inicializado correctamente con Supabase
   ```

2. Si hay errores, verás:
   ```
   ⚠️ Fallback a almacenamiento en memoria...
   ```

## 🐛 Solución de Problemas

### Error: "extension 'vector' does not exist"

**Solución**: Ejecuta el SQL para habilitar pgvector (Paso 1).

### Error: "connection refused" o "authentication failed"

**Solución**: 
- Verifica que `SUPABASE_DB_URL` tenga el formato correcto
- Verifica que la contraseña sea correcta
- Asegúrate de usar la connection string de **URI** (no Session mode)

### Error: "relation does not exist"

**Solución**: Esto es normal la primera vez. LlamaIndex creará las tablas automáticamente cuando agregues el primer documento.

### El sistema usa "almacenamiento en memoria"

**Solución**: 
- Verifica que `SUPABASE_DB_URL` o `SUPABASE_DB_PASSWORD` estén configurados
- Revisa los logs para ver el error específico
- Asegúrate de que pgvector esté habilitado en Supabase

## 📊 Estructura de Tablas

LlamaIndex creará automáticamente estas tablas en Supabase:

- `arbot_vectors`: Almacena los vectores y metadatos
- `arbot_documents`: Almacena los documentos (si se usa)

No necesitas crearlas manualmente.

## 🔄 Migración desde FAISS

Si ya tenías documentos procesados con FAISS:

1. **No necesitas hacer nada especial**: Los nuevos documentos se agregarán a Supabase automáticamente
2. **Los documentos antiguos**: Si quieres migrarlos, simplemente vuelve a subir el PDF y se procesará con LlamaIndex

## 💡 Notas Importantes

- **Primera vez**: La primera vez que agregues documentos, puede tardar un poco más mientras se crean las tablas
- **Persistencia**: Los vectores se guardan automáticamente, no necesitas llamar `save_index()` manualmente
- **Carga automática**: Al iniciar la app, LlamaIndex carga automáticamente los vectores desde Supabase
- **Sin límites**: El plan gratuito de Supabase permite suficiente espacio para documentos medianos

## 🎉 ¡Listo!

Una vez configurado, tu sistema RAG usará Supabase pgvector automáticamente. Los documentos se guardarán y cargarán automáticamente sin necesidad de archivos manuales.

