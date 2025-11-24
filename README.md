# 🤖 ARB-BOT - Asistente Institucional con IA

Sistema de chatbot institucional que utiliza RAG (Retrieval Augmented Generation) para responder preguntas sobre documentos legales (Manuales de Convivencia, Reglamentos, etc.) usando IA.

## 🏗️ Arquitectura

El sistema está dividido en tres componentes principales:

1. **Google Colab** (Backoffice) - Procesamiento de documentos
2. **Supabase** (Base de Datos) - Almacenamiento de chunks y embeddings
3. **Railway** (Producción) - Bot en vivo que responde preguntas

Ver [ARQUITECTURA_SISTEMA.md](ARQUITECTURA_SISTEMA.md) para más detalles.

## ✨ Características

- ✅ **Chunking jerárquico legal** - Respeta estructura TÍTULO → CAPÍTULO → Artículo
- ✅ **Búsqueda híbrida** - Vectorial + por metadata (artículos específicos)
- ✅ **Metadatos completos** - title, chapter, article, paragraph, page, keywords
- ✅ **Respuestas precisas** - Citas exactas con referencias al documento
- ✅ **Arquitectura optimizada** - Procesamiento en Colab, consultas en Railway

## 🚀 Inicio Rápido

### 1. Configuración Inicial

1. Clona el repositorio
2. Copia `.env.example` a `.env` y configura:
   - `SUPABASE_DB_URL` - Connection string de Supabase
   - `GROQ_API_KEY` - API key de Groq
   - `EMBEDDINGS_MODEL` - Modelo de embeddings (default: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

### 2. Procesar Documentos (Colab)

1. Abre `INGESTA_DOCUMENTOS_COLAB.ipynb` en Google Colab
2. Configura `SUPABASE_DB_URL` en la celda de configuración
3. Sube tu PDF (Manual de Convivencia, Reglamento, etc.)
4. Ejecuta el procesamiento
5. ¡Listo! Los chunks están en Supabase

Ver [GUIA_CHUNKING_JERARQUICO.md](GUIA_CHUNKING_JERARQUICO.md) para más detalles sobre el chunking.

### 3. Desplegar Bot (Railway)

1. Conecta tu repositorio a Railway
2. Configura las variables de entorno
3. Deploy automático
4. ¡El bot está listo para responder!

Ver [DESPLIEGUE_RAILWAY.md](DESPLIEGUE_RAILWAY.md) para más detalles.

## 📚 Documentación

- [ARQUITECTURA_SISTEMA.md](ARQUITECTURA_SISTEMA.md) - Arquitectura completa del sistema
- [GUIA_CHUNKING_JERARQUICO.md](GUIA_CHUNKING_JERARQUICO.md) - Guía del chunking jerárquico
- [DESPLIEGUE_RAILWAY.md](DESPLIEGUE_RAILWAY.md) - Guía de despliegue en Railway
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Configuración de GitHub

## 🔧 Tecnologías

- **Backend:** Flask (Python)
- **IA:** Groq API (Llama 3.1)
- **RAG:** LlamaIndex + Supabase (pgvector)
- **Embeddings:** HuggingFace (sentence-transformers)
- **Base de Datos:** Supabase (PostgreSQL + pgvector)
- **Despliegue:** Railway

## 📊 Estructura del Proyecto

```
ARB-BOT/
├── app.py                      # Aplicación Flask principal
├── services/
│   ├── rag_service.py         # Servicio RAG (búsquedas)
│   ├── generator.py           # Generador de respuestas
│   └── text_processor.py      # Procesamiento de texto
├── INGESTA_DOCUMENTOS_COLAB.ipynb  # Notebook para procesar documentos
├── scripts/                    # Scripts SQL de utilidad
└── templates/                  # Templates HTML
```

## 🎯 Uso

### Preguntas del Usuario

El bot puede responder preguntas como:
- "¿Qué dice el artículo 52?"
- "¿Cuáles son los deberes de los estudiantes?"
- "¿Qué es una falta grave?"
- "¿Dónde se menciona el ciberbullying?"

### Búsqueda Híbrida

El sistema usa búsqueda híbrida:
1. **Por metadata** - Si pregunta "artículo 52", busca directamente en metadata
2. **Vectorial** - Si no encuentra, busca por similitud semántica
3. **Combinación** - Mejor resultado posible

## ⚠️ Importante

- **NO subas PDFs desde Railway** - Todo el procesamiento se hace en Colab
- **Railway solo consulta** - No procesa documentos (optimización de recursos)
- **Usa Colab para ingesta** - Procesa documentos en el notebook de Colab

## 📝 Licencia

Este proyecto es de uso interno institucional.

## 🤝 Contribuciones

Para contribuir, por favor:
1. Crea un branch para tu feature
2. Haz commit de tus cambios
3. Abre un Pull Request

---

**Desarrollado para instituciones educativas** 🎓
