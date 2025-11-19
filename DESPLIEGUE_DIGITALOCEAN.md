# 🚀 Desplegar ARB-BOT en DigitalOcean (Gratis con $200 crédito)

## 📋 Requisitos Previos

1. **Cuenta en DigitalOcean** (nueva, para obtener $200 crédito)
   - Regístrate en: https://www.digitalocean.com/go/free-credit-200
   - Verifica tu tarjeta (solo verificación, no se cobra durante el crédito)

2. **GitHub** con tu código subido

---

## 🎯 Paso 1: Crear Droplet en DigitalOcean

1. Ve a **DigitalOcean Dashboard** → **Create** → **Droplets**

2. Configura:
   - **Image:** Ubuntu 22.04 (LTS)
   - **Plan:** 
     - **Basic** → **Regular** → **$6/mes** (1GB RAM, 1 vCPU) ← **Recomendado**
     - O **$12/mes** (2GB RAM) si quieres más margen
   - **Datacenter region:** Elige la más cercana (ej: New York, San Francisco)
   - **Authentication:** 
     - ✅ **SSH keys** (recomendado) - Agrega tu clave pública
     - O **Password** (más simple pero menos seguro)

3. **Additional options:**
   - ✅ **Monitoring** (gratis)
   - ✅ **IPv6** (opcional)

4. **Finalize:**
   - **Hostname:** `arb-bot` (o el que prefieras)
   - Haz clic en **Create Droplet**

5. Espera 1-2 minutos mientras se crea el servidor

---

## 🔧 Paso 2: Conectarte al Servidor

### Opción A: Desde Windows (PowerShell o CMD)

```powershell
# Reemplaza TU_IP con la IP de tu droplet (la verás en DigitalOcean)
ssh root@TU_IP
```

### Opción B: Desde Git Bash o Terminal

```bash
ssh root@TU_IP
```

Si usaste contraseña, te pedirá la contraseña que configuraste.

---

## 📦 Paso 3: Instalar Docker en el Servidor

Una vez conectado, ejecuta estos comandos:

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Agregar usuario actual a grupo docker (opcional, si no usas root)
# usermod -aG docker $USER

# Verificar instalación
docker --version
```

---

## 🐳 Paso 4: Configurar la Aplicación

```bash
# Crear directorio para la app
mkdir -p /opt/arb-bot
cd /opt/arb-bot

# Clonar tu repositorio (reemplaza con tu URL de GitHub)
git clone https://github.com/TU_USUARIO/ARB-BOT.git .

# O si prefieres, crear los archivos manualmente:
# (ver siguiente paso)
```

---

## ⚙️ Paso 5: Configurar Variables de Entorno

```bash
# Crear archivo .env
nano .env
```

Pega esto (ajusta los valores):

```env
FLASK_ENV=production
SECRET_KEY=tu-secret-key-muy-segura-aqui
DATABASE_URL=sqlite:///arbot.db

# Supabase (si lo usas)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
SUPABASE_BUCKET=documents
```

Guarda con `Ctrl+O`, Enter, `Ctrl+X`

---

## 🚀 Paso 6: Construir y Ejecutar con Docker

```bash
cd /opt/arb-bot

# Construir imagen Docker
docker build -t arb-bot .

# Ejecutar contenedor
docker run -d \
  --name arb-bot \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/documents:/app/documents \
  arb-bot
```

---

## 🌐 Paso 7: Configurar Nginx (Proxy Reverso)

```bash
# Instalar Nginx
apt install nginx -y

# Crear configuración
nano /etc/nginx/sites-available/arb-bot
```

Pega esta configuración:

```nginx
server {
    listen 80;
    server_name TU_IP_O_DOMINIO;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts para procesamiento largo
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
    }
}
```

```bash
# Activar sitio
ln -s /etc/nginx/sites-available/arb-bot /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # Remover default si existe

# Reiniciar Nginx
systemctl restart nginx
```

---

## 🔒 Paso 8: Configurar Firewall (Opcional pero Recomendado)

```bash
# Permitir SSH, HTTP y HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## ✅ Paso 9: Verificar que Funciona

1. Abre tu navegador y ve a: `http://TU_IP`
2. Deberías ver la interfaz de ARB-BOT

---

## 🔄 Actualizar la Aplicación (Cuando hagas cambios)

```bash
cd /opt/arb-bot

# Detener contenedor actual
docker stop arb-bot
docker rm arb-bot

# Actualizar código
git pull

# Reconstruir y ejecutar
docker build -t arb-bot .
docker run -d \
  --name arb-bot \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/documents:/app/documents \
  arb-bot
```

---

## 📊 Monitoreo y Logs

```bash
# Ver logs de la aplicación
docker logs -f arb-bot

# Ver uso de recursos
docker stats arb-bot

# Ver procesos
htop
```

---

## 💰 Costos

- **Droplet 1GB:** $6/mes
- **Con $200 crédito:** ~33 meses gratis
- **Para demo universidad:** Gratis por 60 días (crédito) + lo que quieras usar después

---

## 🆘 Solución de Problemas

### La app no carga
```bash
# Verificar que Docker está corriendo
docker ps

# Ver logs
docker logs arb-bot

# Verificar Nginx
systemctl status nginx
```

### Error de memoria
- Si ves "Out of memory", considera:
  - Droplet de 2GB ($12/mes)
  - O usar las optimizaciones ya implementadas

### Reiniciar todo
```bash
docker restart arb-bot
systemctl restart nginx
```

---

## 🎓 Para la Demo de la Universidad

1. ✅ Tu app estará disponible en `http://TU_IP`
2. ✅ Puedes subir documentos y probar el RAG
3. ✅ Todo funciona igual que en Render, pero con más RAM
4. ✅ Gratis durante 60 días (más que suficiente para la demo)

---

## 📝 Notas Finales

- **Backup:** Los documentos se guardan en `/opt/arb-bot/documents` (persistente)
- **Dominio:** Si tienes un dominio, puedes configurarlo en DigitalOcean DNS
- **SSL:** Puedes usar Let's Encrypt con Certbot (gratis) para HTTPS

---

¡Listo! Tu ARB-BOT estará funcionando en DigitalOcean. 🚀

