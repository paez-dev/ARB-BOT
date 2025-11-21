# 🔍 Verificar Conexión a Supabase

Si ves el error `Network is unreachable` o problemas de conexión, sigue estos pasos:

## ✅ Paso 1: Verificar Variables en Railway

Ve a Railway → Tu Proyecto → **Variables** y verifica que tengas:

### ⭐ Opción A: Connection Pooler (RECOMENDADO para Railway)

**El pooler funciona mejor desde servidores cloud y evita errores de "Network is unreachable":**

1. Ve a Supabase → **Settings** → **Database**
2. Busca **"Connection pooling"** o **"Connection string"**
3. Selecciona **"Session mode"** o **"Transaction mode"**
4. Copia la connection string del **pooler**

**Formato del pooler:**
```
SUPABASE_DB_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
```

**Ejemplo:**
```
SUPABASE_DB_URL=postgresql://postgres.ympekltzqzlsbdgbzbpz:TU_PASSWORD@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**Diferencias importantes:**
- **Usuario**: `postgres.PROJECT_REF` (con punto, no solo `postgres`)
- **Host**: `aws-0-REGION.pooler.supabase.com` (pooler, no `db.xxxxx.supabase.co`)
- **Puerto**: `6543` (pooler) en lugar de `5432` (directo)

### Opción B: Connection String Directa (Puede fallar)

```
SUPABASE_DB_URL=postgresql://postgres:TU_PASSWORD@db.TU_PROJECT_ID.supabase.co:5432/postgres
```

**⚠️ Nota**: Esta conexión directa puede fallar con "Network is unreachable" desde Railway. Usa el pooler (Opción A).

### Opción C: Variables Separadas

```
SUPABASE_URL=https://ympekltzqzlsbdgbzbpz.supabase.co
SUPABASE_KEY=tu-anon-key
SUPABASE_DB_PASSWORD=tu_password_de_base_de_datos
```

## ✅ Paso 2: Obtener el Password Correcto

1. Ve a Supabase → **Settings** → **Database**
2. Busca **"Database password"**
3. Si no lo ves o no lo conoces:
   - Haz clic en **"Reset database password"**
   - **⚠️ IMPORTANTE**: Copia la nueva contraseña inmediatamente
   - Guárdala en un lugar seguro
   - Actualiza `SUPABASE_DB_PASSWORD` en Railway con esta nueva contraseña

## ✅ Paso 3: Verificar el Formato de la Connection String

La connection string debe tener este formato exacto:

```
postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
```

**Partes importantes:**
- `postgresql://` (no `postgres://`)
- `postgres:` (usuario)
- `[PASSWORD]` (tu password real)
- `@db.` (debe tener `db.` antes del host)
- `[PROJECT_ID].supabase.co` (tu Project ID)
- `:5432` (puerto)
- `/postgres` (base de datos)

## ✅ Paso 4: Verificar Restricciones de Red en Supabase

1. Ve a Supabase → **Settings** → **Database**
2. Busca **"Network Restrictions"**
3. Si hay restricciones:
   - **Opción 1**: Agregar la IP de Railway (puede cambiar)
   - **Opción 2**: Temporalmente permitir todas las IPs para probar
   - **Opción 3**: Desactivar restricciones temporalmente

## ✅ Paso 5: Verificar que pgvector esté Habilitado

1. Ve a Supabase → **SQL Editor**
2. Ejecuta:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Verifica:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

## ✅ Paso 6: Probar la Conexión

Después de configurar, revisa los logs en Railway. Deberías ver:

**✅ Si funciona:**
```
🔧 Inicializando LlamaIndex con Supabase pgvector...
✅ Índice cargado desde Supabase
✅ LlamaIndex inicializado correctamente con Supabase
```

**❌ Si falla:**
```
❌ Error inicializando LlamaIndex con Supabase: ...
💡 Posibles causas:
   1. La connection string está mal formada
   2. El password de la base de datos es incorrecto
   3. Supabase tiene restricciones de red
   4. El host 'db.xxxxx.supabase.co' no es accesible desde Railway
```

## 🔧 Soluciones Comunes

### Error: "Network is unreachable"

**Causas posibles:**
1. La connection string está mal formada
2. El password es incorrecto
3. Restricciones de red en Supabase
4. El formato del host está mal

**Soluciones:**
1. Verifica que la connection string tenga el formato correcto
2. Resetea el password y actualiza Railway
3. Desactiva temporalmente las restricciones de red en Supabase
4. Verifica que el host sea `db.xxxxx.supabase.co` (con `db.` al inicio)

### Error: "authentication failed"

**Causa:** Password incorrecto

**Solución:**
1. Resetea el password en Supabase
2. Actualiza `SUPABASE_DB_PASSWORD` en Railway
3. O usa `SUPABASE_DB_URL` completa con el password correcto

### Error: "extension vector does not exist"

**Causa:** pgvector no está habilitado

**Solución:**
1. Ve a Supabase → SQL Editor
2. Ejecuta: `CREATE EXTENSION IF NOT EXISTS vector;`

## 📋 Checklist de Verificación

- [ ] `SUPABASE_DB_URL` configurada en Railway (o `SUPABASE_DB_PASSWORD`)
- [ ] Password de base de datos es correcto
- [ ] Connection string tiene formato correcto: `postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres`
- [ ] pgvector habilitado en Supabase
- [ ] Restricciones de red verificadas (o desactivadas temporalmente)
- [ ] Logs muestran conexión exitosa

## 💡 Nota Importante

Si después de verificar todo sigue fallando, el sistema funcionará en **memoria** (sin persistencia). Esto significa:
- ✅ Funciona correctamente
- ⚠️ Los vectores se pierden al reiniciar
- ✅ Puedes subir documentos y funcionará normalmente

Para persistencia permanente, necesitas resolver la conexión a Supabase.

