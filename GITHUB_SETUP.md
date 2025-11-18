# 🚀 Guía para Subir a GitHub

## ✅ Paso 1: Git Inicializado (YA HECHO)

Tu proyecto ya está inicializado con Git y los archivos están listos para commit.

## 📝 Paso 2: Hacer el Primer Commit

Ejecuta estos comandos:

```bash
git commit -m "Initial commit - ARB-BOT chatbot institucional"
```

## 🌐 Paso 3: Crear Repositorio en GitHub

### Opción A: Desde la Web (Más Fácil)

1. **Ve a [github.com](https://github.com)** e inicia sesión
2. **Haz clic en el botón "+"** (arriba a la derecha) → **"New repository"**
3. **Configura el repositorio:**
   - **Repository name:** `ARB-BOT` (o el nombre que prefieras)
   - **Description:** "Chatbot institucional con IA usando RAG - 100% gratuito"
   - **Visibility:** 
     - ✅ **Public** (recomendado - gratis, otros pueden ver tu código)
     - ⚠️ **Private** (solo tú puedes verlo)
   - **NO marques** "Add a README file" (ya tienes uno)
   - **NO marques** "Add .gitignore" (ya tienes uno)
   - **NO marques** "Choose a license" (opcional)
4. **Haz clic en "Create repository"**

### Opción B: Desde GitHub CLI (Si lo tienes instalado)

```bash
gh repo create ARB-BOT --public --source=. --remote=origin --push
```

## 🔗 Paso 4: Conectar tu Repositorio Local con GitHub

Después de crear el repositorio en GitHub, verás una página con instrucciones. Ejecuta estos comandos:

```bash
# Reemplaza 'tu-usuario' con tu nombre de usuario de GitHub
git remote add origin https://github.com/tu-usuario/ARB-BOT.git

# Cambiar a la rama main (si es necesario)
git branch -M main

# Subir el código
git push -u origin main
```

**Si GitHub te pide autenticación:**
- Usa un **Personal Access Token** (no tu contraseña)
- Cómo crear uno: [GitHub Docs - Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## ✅ Paso 5: Verificar

Ve a tu repositorio en GitHub:
```
https://github.com/tu-usuario/ARB-BOT
```

Deberías ver todos tus archivos allí.

---

## 🚀 Paso 6: Conectar con Render

Una vez que tu código esté en GitHub:

1. **Ve a [render.com](https://render.com)**
2. **Crea una cuenta** (gratis) o inicia sesión
3. **Haz clic en "New +"** → **"Web Service"**
4. **Conecta tu repositorio:**
   - Selecciona "Connect account" si es la primera vez
   - Autoriza a Render a acceder a GitHub
   - Selecciona tu repositorio `ARB-BOT`
5. **Configura el servicio:**
   - **Name:** `arb-bot` (o el nombre que prefieras)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. **Variables de Entorno (opcional pero recomendado):**
   - Haz clic en "Advanced"
   - Agrega estas variables:
     ```
     FLASK_ENV=production
     FLASK_DEBUG=False
     SECRET_KEY=tu_secret_key_segura_aqui
     ```
   - Para generar SECRET_KEY:
     ```python
     import secrets
     print(secrets.token_hex(32))
     ```
7. **Haz clic en "Create Web Service"**
8. **¡Espera 10-15 minutos!** (la primera vez tarda porque descarga los modelos de IA)

---

## 📋 Checklist

- [ ] ✅ Git inicializado
- [ ] ✅ Archivos agregados a Git
- [ ] ✅ Primer commit hecho
- [ ] ✅ Repositorio creado en GitHub
- [ ] ✅ Repositorio local conectado con GitHub
- [ ] ✅ Código subido a GitHub
- [ ] ✅ Cuenta creada en Render
- [ ] ✅ Repositorio conectado en Render
- [ ] ✅ Servicio configurado en Render
- [ ] ✅ Variables de entorno configuradas
- [ ] ✅ Despliegue iniciado

---

## 🆘 Solución de Problemas

### Error: "remote origin already exists"

**Solución:**
```bash
git remote remove origin
git remote add origin https://github.com/tu-usuario/ARB-BOT.git
```

### Error: "authentication failed"

**Solución:**
- Usa un Personal Access Token en lugar de tu contraseña
- O configura SSH keys

### Error al hacer push

**Solución:**
```bash
# Verificar que estás en la rama main
git branch

# Si no estás en main:
git checkout -b main
git push -u origin main
```

---

**¡Listo!** Una vez desplegado, tu chatbot estará disponible en:
```
https://tu-app.onrender.com
```

