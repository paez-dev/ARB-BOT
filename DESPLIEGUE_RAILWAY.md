# 🚂 Desplegar ARB-BOT en Railway

## 📋 Información sobre Railway

**Railway** es una plataforma de hosting muy fácil de usar, similar a Render pero con mejor experiencia.

### 💰 Planes y Precios (2025)

- **Plan Gratuito:**
  - $5 crédito gratis los primeros 30 días
  - Luego $1/mes crédito no acumulable (suficiente para apps pequeñas)
  - 0.5GB RAM por servicio
  - **No se suspende por inactividad** ✅ (a diferencia de Render)
  
- **Plan Hobby:** $5/mes
  - Hasta 8GB RAM por servicio
  - $5 crédito mensual incluido
  - Ideal si necesitas más recursos

- **Características:**
  - Auto-deploy desde GitHub ✅
  - HTTPS incluido ✅
  - Sin configuración manual ✅
  - Logs en tiempo real ✅

---

## 🎯 Paso 1: Crear Cuenta en Railway

1. Ve a [railway.app](https://railway.app)
2. Haz clic en **"Start a New Project"**
3. Regístrate con **GitHub** (recomendado) o Email
4. Verifica tu email si es necesario

---

## 🚀 Paso 2: Conectar GitHub y Desplegar

### Opción A: Desde el Dashboard de Railway

1. En Railway, haz clic en **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Autoriza Railway a acceder a tu GitHub (si es la primera vez)
4. Selecciona tu repositorio **ARB-BOT**
5. Railway detectará automáticamente que es una app Python

### Opción B: Usando Railway CLI (Opcional)

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Desplegar
railway up
```

---

## ⚙️ Paso 3: Configurar Variables de Entorno

1. En tu proyecto de Railway, ve a **Settings** → **Variables**
2. Agrega estas variables:

```env
FLASK_ENV=production
SECRET_KEY=tu-secret-key-muy-segura-aqui-genera-una-nueva
DATABASE_URL=sqlite:///arbot.db

# Supabase (si lo usas)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
SUPABASE_BUCKET=documents
```

3. Haz clic en **"Add"** para cada variable

---

## 🐳 Paso 4: Configurar Docker (Opcional pero Recomendado)

Railway puede detectar automáticamente tu `Dockerfile`. Si ya lo tienes, Railway lo usará automáticamente.

Si prefieres que Railway construya sin Docker:

1. Ve a **Settings** → **Build & Deploy**
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 600`

---

## 📊 Paso 5: Configurar Recursos (RAM)

1. Ve a **Settings** → **Resources**
2. **Memory:** 
   - Plan Gratuito: Máximo 0.5GB (puede ser insuficiente)
   - Plan Hobby ($5/mes): Hasta 2GB (recomendado para tu app)

**Nota:** Con 0.5GB puede tener problemas de memoria. Si es para demo, considera el plan Hobby ($5/mes) o usa DigitalOcean.

---

## 🌐 Paso 6: Obtener URL Pública

1. Ve a **Settings** → **Networking**
2. Haz clic en **"Generate Domain"**
3. Railway te dará una URL como: `arb-bot-production.up.railway.app`
4. ✅ **HTTPS está incluido automáticamente**

---

## 🔄 Paso 7: Auto-Deploy (Ya está configurado)

Railway despliega automáticamente cada vez que haces `git push` a tu repositorio.

Para desplegar manualmente:
1. Ve a **Deployments**
2. Haz clic en **"Redeploy"**

---

## ✅ Verificar que Funciona

1. Abre tu URL de Railway en el navegador
2. Deberías ver la interfaz de ARB-BOT
3. Prueba subir un documento y hacer una pregunta

---

## 📊 Monitoreo y Logs

1. Ve a **Deployments** → Selecciona el deployment más reciente
2. Verás los logs en tiempo real
3. También puedes ver métricas de CPU y memoria

---

## 💰 Costos

### Plan Gratuito (30 días)
- $5 crédito gratis
- 0.5GB RAM máximo
- **Problema:** Puede ser insuficiente para tu app con Torch + RAG

### Plan Hobby ($5/mes)
- Hasta 2GB RAM
- Suficiente para tu aplicación
- **Recomendado** para demo universidad

---

## 🆘 Solución de Problemas

### Error: "Out of memory"
- **Solución:** Aumenta RAM en Settings → Resources
- O cambia a plan Hobby ($5/mes)

### La app no carga
- Verifica los logs en Railway
- Revisa que las variables de entorno estén correctas
- Verifica que el puerto sea `$PORT` (Railway lo asigna automáticamente)

### Error al desplegar
- Verifica que `requirements.txt` esté correcto
- Revisa los logs de build
- Asegúrate de que `Dockerfile` esté en la raíz (si usas Docker)

---

## 🎓 Para la Demo de la Universidad

1. ✅ Tu app estará en una URL pública de Railway
2. ✅ HTTPS incluido (más profesional)
3. ✅ Auto-deploy desde GitHub (muy fácil de actualizar)
4. ✅ Logs y monitoreo incluidos

---

## 🔄 Actualizar la Aplicación

Simplemente haz `git push` a tu repositorio y Railway desplegará automáticamente:

```bash
git add .
git commit -m "Actualización"
git push
```

Railway detectará el cambio y desplegará automáticamente.

---

## 📝 Comparación: Railway vs DigitalOcean

| Característica | Railway | DigitalOcean |
|---------------|---------|--------------|
| **Facilidad** | ⭐⭐⭐⭐⭐ Muy fácil | ⭐⭐⭐ Requiere configuración |
| **Auto-deploy** | ✅ Sí | ❌ Manual |
| **HTTPS** | ✅ Automático | ⚙️ Requiere configuración |
| **Costo gratis** | $5 crédito (30 días) | $200 crédito (60 días) |
| **RAM gratis** | 0.5GB (limitado) | 1GB ($6/mes con crédito) |
| **RAM recomendada** | 2GB ($5/mes) | 1GB ($6/mes) |
| **Control** | ⚙️ Limitado | ⭐⭐⭐⭐⭐ Total |

**Recomendación:**
- **Railway:** Si quieres simplicidad y $5/mes no es problema
- **DigitalOcean:** Si quieres máximo tiempo gratis y control total

---

¡Listo! Tu ARB-BOT estará funcionando en Railway. 🚂

