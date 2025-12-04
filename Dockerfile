# ============================================================
# ARB-BOT — DOCKERFILE PRO PARA RAILWAY (OPTIMIZADO PARA RAM)
# Python 3.11-slim + Sentence-Transformers + pgvector + RAG
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

# Directorio para cache de modelos
ENV HF_HOME=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers

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
# PRE-DESCARGAR MODELO DE EMBEDDINGS
# (Esto lo descarga durante el build, no en runtime)
# -----------------------------
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Ahora sí activamos modo offline para runtime
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

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
