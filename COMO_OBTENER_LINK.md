# 🔗 Cómo Obtener el Link de tu Aplicación

## 📍 Si Ya Desplegaste en Render

### Opción 1: Desde el Dashboard de Render

1. **Ve a [render.com](https://render.com)**
2. **Inicia sesión** con tu cuenta
3. En el **Dashboard**, verás una lista de tus servicios
4. **Haz clic en tu servicio** (probablemente se llama "arb-bot" o "ARB-BOT")
5. En la parte superior de la página, verás:
   ```
   URL: https://tu-app.onrender.com
   ```
   **Ese es tu link!** 🎉

### Opción 2: Desde la Configuración

1. En el Dashboard de Render, haz clic en tu servicio
2. Ve a la pestaña **"Settings"** (Configuración)
3. Busca la sección **"Service Details"**
4. Ahí verás el **"URL"** de tu aplicación

---

## 🚀 Si AÚN NO Has Desplegado en Render

### Pasos para Desplegar y Obtener el Link:

#### 1. Preparar el Proyecto (Ya está hecho ✅)
- ✅ `render.yaml` - Configuración de Render
- ✅ `Procfile` - Comando de inicio
- ✅ `requirements.txt` - Dependencias
- ✅ Código en GitHub

#### 2. Crear Cuenta en Render

1. Ve a **[render.com](https://render.com)**
2. Haz clic en **"Get Started for Free"** o **"Sign Up"**
3. Puedes registrarte con:
   - GitHub (recomendado - más fácil)
   - Email
   - Google

#### 3. Conectar GitHub

1. En Render, haz clic en **"New +"** → **"Web Service"**
2. Selecciona **"Connect GitHub"** o **"Connect Repository"**
3. Autoriza a Render a acceder a tus repositorios
4. Selecciona el repositorio **"ARB-BOT"** (paez-dev/ARB-BOT)

#### 4. Configurar el Servicio

Render debería detectar automáticamente que es una app Flask, pero verifica:

- **Name:** `arb-bot` (o el nombre que prefieras)
- **Environment:** `Python 3`
- **Region:** Elige el más cercano (ej: `Oregon (US West)`)
- **Branch:** `main`
- **Root Directory:** (déjalo vacío)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 120`

#### 5. Variables de Entorno (Opcional)

En la sección **"Environment Variables"**, puedes agregar:
```
FLASK_ENV=production
PYTHON_VERSION=3.11
```

#### 6. Crear el Servicio

1. Haz clic en **"Create Web Service"**
2. Render comenzará a construir tu aplicación
3. Esto puede tardar **5-15 minutos** la primera vez

#### 7. Obtener el Link

Una vez que el build termine exitosamente:

1. En la página de tu servicio, verás:
   ```
   ✅ Your service is live at:
   https://arb-bot.onrender.com
   ```
   
   **¡Ese es tu link!** 🎉

2. El link será algo como:
   - `https://arb-bot.onrender.com`
   - O `https://arb-bot-xxxx.onrender.com` (si el nombre ya está tomado)

---

## 🔍 Verificar que Funciona

1. **Abre el link** en tu navegador
2. Deberías ver:
   - El header con "🤖 ARB-BOT"
   - El mensaje de bienvenida del bot
   - El input para hacer preguntas

3. Si ves un error o "Application Error":
   - Revisa los **logs** en Render (pestaña "Logs")
   - Espera unos minutos (puede estar iniciando)
   - Verifica que el build fue exitoso

---

## 📝 Notas Importantes

### Sobre el Link de Render:

- **Formato:** `https://[nombre-servicio].onrender.com`
- **HTTPS:** Siempre viene con HTTPS (seguro)
- **Personalizable:** Puedes cambiar el nombre en Settings → Name
- **Gratis:** El link es gratis en el plan free tier

### Si el Nombre Ya Está Tomado:

Si `arb-bot.onrender.com` ya está en uso, Render te asignará:
- `arb-bot-xxxx.onrender.com` (donde xxxx son números aleatorios)
- O puedes elegir otro nombre único

### Primera Carga:

- La **primera vez** que abres el link puede tardar **30-60 segundos**
- Esto es normal en el plan gratuito (el servicio "duerme" después de 15 min de inactividad)
- Las siguientes veces será más rápido

---

## 🎯 Resumen Rápido

1. **Si ya desplegaste:**
   - Ve a render.com → Dashboard → Tu servicio → Ver URL

2. **Si NO has desplegado:**
   - Ve a render.com → Sign Up → New Web Service → Conecta GitHub → Configura → Create
   - Espera 5-15 minutos
   - Tu link aparecerá en la página del servicio

---

## ❓ ¿Necesitas Ayuda?

Si tienes problemas:
1. Revisa los **logs** en Render (pestaña "Logs")
2. Verifica que el **build fue exitoso** (debe decir "Build successful ✅")
3. Asegúrate de que el servicio está **"Live"** (no "Sleeping")

**¿Ya tienes el link o necesitas ayuda para desplegarlo?**

