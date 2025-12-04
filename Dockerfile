# ============================================================
# ARB-BOT — DOCKERFILE PRO PARA RAILWAY (OPTIMIZADO PARA RAM)
# Python 3.11-slim + LlamaIndex + pgvector + RAG
# ============================================================

FROM python:3.11-slim

# -----------------------------
# VARIABLES DE ENTORNO GLOBALES
# -----------------------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# OPTIMIZACIÓN RAM / CPU (muy importante para Railway)
ENV TOKENIZERS_PARALLELISM=false
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV TRANSFORMERS_OFFLINE=1

# -----------------------------
# DEPENDENCIAS DEL SISTEMA
# -----------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libmagic1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# DIRECTORIO DE TRABAJO
# -----------------------------
WORKDIR /app

# -----------------------------
# INSTALAR DEPENDENCIAS PYTHON
# -----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# COPIAR TODO EL PROYECTO
# -----------------------------
COPY . .

# -----------------------------
# CREAR DIRECTORIOS NECESARIOS
# -----------------------------
RUN mkdir -p uploads documents logs

# -----------------------------
# PUERTO DE SALIDA
# -----------------------------
EXPOSE 8080

# -----------------------------
# EJECUCIÓN CON GUNICORN
# Railway asigna el puerto con $PORT
# -----------------------------
CMD gunicorn app:app \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 1 \
    --threads 2 \
    --timeout 300 \
    --graceful-timeout 300 \
    --log-level info
