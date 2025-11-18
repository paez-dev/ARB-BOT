# ARB-BOT - Guía de Despliegue en la Nube (Gratuito)

## 🌐 Opciones de Despliegue Gratuito

Puedes desplegar ARB-BOT en varios servicios gratuitos para que sea accesible desde internet. Aquí están las mejores opciones:

---

## 🚀 Opción 1: Render (RECOMENDADO - Más Fácil)

**Render** es la opción más fácil y gratuita. Ofrece hosting gratuito para aplicaciones Flask.

### Ventajas:
- ✅ **100% Gratuito** (con límites razonables)
- ✅ **Muy fácil de configurar**
- ✅ **Despliegue automático desde GitHub**
- ✅ **HTTPS incluido**
- ✅ **Sin tarjeta de crédito requerida**

### Pasos para Desplegar:

#### 1. Preparar el Proyecto

Crea un archivo `render.yaml` en la raíz del proyecto:

```yaml
services:
  - type: web
    name: arb-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PYTHON_VERSION
        value: 3.11.0
```

Crea un archivo `Procfile`:

```
web: gunicorn app:app
```

Actualiza `requirements.txt` para incluir gunicorn:

```
gunicorn==21.2.0
```

#### 2. Subir a GitHub

```bash
# Si no tienes Git inicializado
git init
git add .
git commit -m "Initial commit"

# Crea un repositorio en GitHub y luego:
git remote add origin https://github.com/tu-usuario/ARB-BOT.git
git push -u origin main
```

#### 3. Desplegar en Render

1. Ve a [render.com](https://render.com)
2. Crea una cuenta (gratis)
3. Haz clic en "New +" → "Web Service"
4. Conecta tu repositorio de GitHub
5. Render detectará automáticamente que es Flask
6. Configura:
   - **Name:** arb-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
7. Haz clic en "Create Web Service"
8. ¡Espera 5-10 minutos y tu app estará online!

**URL resultante:** `https://arb-bot.onrender.com` (o el nombre que elijas)

### ⚠️ Notas Importantes para Render:

- **Primera carga:** Puede tardar 1-2 minutos (free tier)
- **Inactividad:** Si no se usa por 15 minutos, se "duerme" (free tier)
- **Límites:** 750 horas/mes gratis (suficiente para uso moderado)
- **Documentos:** Los documentos se guardan en el sistema de archivos (persisten)

---

## 🚂 Opción 2: Railway

**Railway** es otra excelente opción gratuita.

### Ventajas:
- ✅ **$5 gratis al mes** (suficiente para uso moderado)
- ✅ **Muy fácil de usar**
- ✅ **Despliegue automático**

### Pasos:

1. Ve a [railway.app](https://railway.app)
2. Crea cuenta con GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecciona tu repositorio
5. Railway detectará Flask automáticamente
6. ¡Listo! Tu app estará online

**URL:** `https://tu-proyecto.up.railway.app`

---

## 🐍 Opción 3: PythonAnywhere

**PythonAnywhere** es específico para Python.

### Ventajas:
- ✅ **Gratis** (con límites)
- ✅ **Específico para Python**
- ✅ **Fácil de usar**

### Pasos:

1. Ve a [pythonanywhere.com](https://www.pythonanywhere.com)
2. Crea cuenta gratuita
3. Sube tu código (vía Git o manualmente)
4. Configura la aplicación web
5. ¡Listo!

**URL:** `https://tu-usuario.pythonanywhere.com`

---

## 🛠️ Configuración Necesaria para Producción

### 1. Actualizar `app.py` para Producción

Asegúrate de que el final de `app.py` sea así:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # IMPORTANTE: False en producción
    )
```

### 2. Agregar Gunicorn

Agrega a `requirements.txt`:

```
gunicorn==21.2.0
```

### 3. Variables de Entorno

En el panel de Render/Railway, configura:

```
FLASK_ENV=production
SECRET_KEY=tu_secret_key_segura_aqui
```

### 4. Archivos Necesarios

Crea `Procfile` (para Heroku/Railway):

```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

O `runtime.txt` (para especificar versión de Python):

```
python-3.11.0
```

---

## 📝 Checklist de Despliegue

Antes de desplegar, verifica:

- [ ] ✅ `requirements.txt` incluye todas las dependencias
- [ ] ✅ `gunicorn` está en requirements.txt
- [ ] ✅ `Procfile` creado (si es necesario)
- [ ] ✅ `FLASK_DEBUG=False` en producción
- [ ] ✅ Código subido a GitHub
- [ ] ✅ `.env` NO está en el repositorio (usar variables de entorno del servicio)
- [ ] ✅ `SECRET_KEY` configurada en el servicio

---

## 🔒 Seguridad en Producción

### Variables de Entorno Importantes:

```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=genera_una_clave_segura_aqui
```

### Generar SECRET_KEY segura:

```python
import secrets
print(secrets.token_hex(32))
```

---

## 📊 Comparación de Opciones

| Característica | Render | Railway | PythonAnywhere |
|---------------|--------|---------|----------------|
| **Gratis** | ✅ Sí | ✅ $5/mes | ✅ Sí |
| **Facilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **HTTPS** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Base de datos** | ✅ Incluida | ✅ Incluida | ✅ Incluida |
| **Despliegue automático** | ✅ Sí | ✅ Sí | ⚠️ Manual |
| **Sleep después inactividad** | ⚠️ Sí (15 min) | ❌ No | ⚠️ Sí |

---

## 🎯 Recomendación Final

**Para empezar rápido:** Usa **Render**
- Más fácil de configurar
- Despliegue automático desde GitHub
- Gratis y suficiente para empezar

**Para uso más intensivo:** Usa **Railway**
- No se duerme
- $5 gratis al mes
- Mejor rendimiento

---

## 🆘 Solución de Problemas

### Error: "Application failed to respond"

**Solución:**
- Verifica que el `startCommand` sea correcto
- Asegúrate de que el puerto sea dinámico: `$PORT`

### Error: "Module not found"

**Solución:**
- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa los logs de build en Render/Railway

### La app se "duerme" en Render

**Solución:**
- Es normal en el tier gratuito
- La primera petición después de dormir tarda ~30 segundos
- Considera Railway si necesitas que esté siempre activo

### Documentos no persisten

**Solución:**
- En Render/Railway, los archivos en el sistema de archivos persisten
- Asegúrate de que la carpeta `documents/` esté creada
- Los índices RAG también persisten

---

## 📚 Recursos Adicionales

- [Documentación de Render](https://render.com/docs)
- [Documentación de Railway](https://docs.railway.app)
- [Documentación de PythonAnywhere](https://help.pythonanywhere.com)

---

**¡Tu chatbot institucional estará online en minutos!** 🚀

Una vez desplegado, podrás compartir la URL con padres de familia, estudiantes y personal de la institución.

