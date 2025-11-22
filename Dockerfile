# ARB-BOT - Dockerfile para Railway
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p documents

# Exponer puerto (Railway asigna PORT automáticamente)
EXPOSE 8080

# Comando para ejecutar la aplicación
# Usar forma shell de CMD para que Railway pueda expandir $PORT
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 1 --timeout 1800 --graceful-timeout 1800

