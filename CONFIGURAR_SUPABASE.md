# 🚀 Configurar Supabase Storage (Gratis)

## 📋 Pasos para Configurar Supabase

### Paso 1: Crear Cuenta en Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Haz clic en **"Start your project"** o **"Sign Up"**
3. Regístrate con GitHub, Google o Email (gratis)

### Paso 2: Crear un Proyecto

1. Una vez dentro, haz clic en **"New Project"**
2. Completa:
   - **Name:** `arb-bot` (o el nombre que prefieras)
   - **Database Password:** Crea una contraseña segura (guárdala)
   - **Region:** Elige la más cercana (ej: `South America (São Paulo)`)
3. Haz clic en **"Create new project"**
4. Espera 1-2 minutos mientras se crea el proyecto

### Paso 3: Crear Bucket de Storage

1. En el menú lateral, ve a **"Storage"**
2. Haz clic en **"New bucket"**
3. Configura:
   - **Name:** `documents`
   - **Public bucket:** ✅ **SÍ** (marcar como público)
   - **File size limit:** 50 MB (o el que prefieras)
   - **Allowed MIME types:** `application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain`
4. Haz clic en **"Create bucket"**

### Paso 4: Obtener API Keys

1. Ve a **Settings** (⚙️) → **API**
2. Encontrarás:
   - **Project URL:** `https://xxxxx.supabase.co` ← Este es `SUPABASE_URL`
   - **anon public key:** `eyJhbGc...` ← Este es `SUPABASE_KEY`
3. **Copia ambos valores**

### Paso 5: Configurar en Railway

1. Ve a tu proyecto en Railway → **Settings** → **Variables**
2. Agrega estas variables:

```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
   




```

3. Haz clic en **"Add"** para cada variable
4. Railway desplegará automáticamente con las nuevas variables

### Paso 6: Verificar

1. Una vez que Railway despliegue, sube un documento
2. Ve a Supabase → Storage → `documents`
3. Deberías ver tu archivo ahí
4. ✅ **¡Listo!** Los documentos ahora son persistentes

---

## 🔒 Seguridad

**¿Es seguro usar la "anon key"?**
- ✅ Sí, para storage público es suficiente
- ✅ Solo permite leer/escribir en el bucket `documents`
- ✅ No tiene acceso a la base de datos
- ✅ Puedes crear políticas más restrictivas si quieres

---

## 📊 Límites Gratuitos de Supabase

- **Storage:** 1 GB gratis
- **Bandwidth:** 2 GB/mes gratis
- **Suficiente para:** Cientos de documentos PDF

---

## ❓ Problemas Comunes

### Error: "Bucket not found"
- Verifica que el bucket se llama exactamente `documents`
- Verifica que el bucket está marcado como **público**

### Error: "Invalid API key"
- Verifica que copiaste la **anon key** (no la service_role key)
- Verifica que no hay espacios extra en las variables de entorno

### Error: "Permission denied"
- Ve a Storage → Policies
- Crea una política que permita lectura/escritura pública

### Limpiar archivos de índices antiguos (RAG)
- **Nota:** Si migraste de FAISS a LlamaIndex, puedes eliminar estos archivos del bucket:
  - `rag_index.json` (ya no se usa)
  - `rag_index_embeddings.npy` (ya no se usa)
- **Cómo eliminarlos:**
  1. Ve a Supabase → Storage → `documents`
  2. Busca archivos que empiecen con `rag_index`
  3. Elimínalos manualmente (ya no se necesitan)
  4. **Los vectores ahora se guardan en pgvector (PostgreSQL), no en archivos**

---

## 🎯 ¿Listo?

Una vez configurado, los documentos se guardarán automáticamente en Supabase y **nunca se perderán**, incluso si Railway reinicia el servicio.

