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

Supabase no muestra la connection string directamente, pero puedes construirla fácilmente:

### Paso 2.1: Obtener tu Password de Base de Datos

1. Ve a **Settings** → **Database**
2. En la sección **"Database password"**, verás tu contraseña actual
3. **Si no la conoces o no la ves:**
   - Haz clic en **"Reset database password"**
   - **⚠️ IMPORTANTE**: Copia la nueva contraseña inmediatamente (no la podrás ver después)
   - Guárdala en un lugar seguro

### Paso 2.2: Obtener el Host de tu Base de Datos

1. Ve a **Settings** → **API** (en el mismo menú de Settings)
2. Encontrarás tu **Project URL**, por ejemplo:
   ```
   https://abcdefghijklmnop.supabase.co
   ```
3. El **Host de la base de datos** se construye así:
   - Toma el ID de tu proyecto (la parte antes de `.supabase.co`)
   - Agrega `db.` al inicio
   - **Ejemplo**: Si tu Project URL es `https://abcdefghijklmnop.supabase.co`
   - Tu Host DB es: `db.abcdefghijklmnop.supabase.co`

### Paso 2.3: Construir la Connection String

Ahora construye la connection string con este formato:

```
postgresql://postgres:TU_PASSWORD@db.TU_PROJECT_ID.supabase.co:5432/postgres
```

**Reemplaza:**
- `TU_PASSWORD` → Tu contraseña de base de datos (del Paso 2.1)
- `TU_PROJECT_ID` → El ID de tu proyecto (del Paso 2.2, sin el `https://`)

**Ejemplo completo:**
Si tu Project URL es `https://ympekltzqzlsbdgbzbpz.supabase.co` y tu password es `mi_password_123`, entonces:

```
postgresql://postgres:mi_password_123@db.ympekltzqzlsbdgbzbpz.supabase.co:5432/postgres
```

### Paso 2.4: Verificar la Connection String

Tu connection string debe tener este formato:
```
postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
```

✅ **Debe incluir:**
- `postgresql://` al inicio
- `postgres:` (usuario)
- Tu password después de `:`
- `@db.` seguido de tu Project ID
- `.supabase.co:5432/postgres` al final

## 🔧 Paso 3: Configurar Variables de Entorno

Agrega estas variables a tu archivo `.env` o en Railway:

### Opción 1: Connection Pooler (RECOMENDADO para Railway) ⭐

**El Connection Pooler es mejor para conexiones desde servidores cloud como Railway:**

1. Ve a Supabase → **Settings** → **Database**
2. Busca **"Connection pooling"** o **"Connection string"**
3. Selecciona **"Session mode"** o **"Transaction mode"**
4. Copia la connection string del **pooler**, se verá así:

```
postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**O construye manualmente:**
- Formato: `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
- **Puerto**: `6543` (pooler) en lugar de `5432` (directo)
- **Host**: `aws-0-[REGION].pooler.supabase.com` en lugar de `db.xxxxx.supabase.co`

**Ejemplo:**
```
SUPABASE_DB_URL=postgresql://postgres.ympekltzqzlsbdgbzbpz:TU_PASSWORD@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### Opción 2: Connection String Directa (Puede fallar desde Railway)

```bash
SUPABASE_DB_URL=postgresql://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

**⚠️ Nota**: La conexión directa puede fallar con "Network is unreachable" desde Railway debido a restricciones de red. Usa el pooler (Opción 1).

### Opción 3: Password Separada (El sistema construye la URL)

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_DB_PASSWORD=tu_password_de_base_de_datos
```

**Nota**: Si usas la Opción 3, el sistema intentará construir la URL automáticamente desde `SUPABASE_URL` (usará conexión directa).

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

