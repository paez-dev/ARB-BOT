# ARB-BOT - Chatbot Institucional con IA

## 📋 Descripción del Proyecto

ARB-BOT es un **chatbot institucional inteligente** desarrollado **100% con herramientas gratuitas**. Permite a padres de familia, estudiantes y personal de la institución hacer preguntas sobre:
- Manual de convivencia
- Reglamentos institucionales
- Políticas y procedimientos
- Información general de la institución

El sistema utiliza **RAG (Retrieval Augmented Generation)** para buscar información relevante en los documentos cargados y generar respuestas precisas basadas en ellos.

## 🎯 Características Principales

- ✅ **Carga de Documentos Institucionales** - Sube PDF, DOCX, TXT (manual de convivencia, reglamentos, etc.)
- ✅ **Búsqueda Semántica (RAG)** - Encuentra información relevante en los documentos
- ✅ **Respuestas Basadas en Documentos** - El bot responde usando solo la información cargada
- ✅ **Múltiples Modelos de IA** - DistilGPT-2, GPT-2 (gratuitos)
- ✅ **Interfaz Web Moderna** - Fácil de usar para padres, estudiantes y personal
- ✅ **Historial de Conversaciones** - Guarda todas las interacciones
- ✅ **Base de Datos Vectorial** - Búsqueda rápida y eficiente
- ✅ **100% Gratuito** - Sin costos ocultos, todo open source

## 🛠️ Stack Tecnológico (100% Gratuito)

### Backend
- **Python 3.9+** - Lenguaje principal
- **Flask** - Framework web ligero y gratuito
- **Hugging Face Transformers** - Modelos de IA gratuitos
- **LangChain** - Framework para aplicaciones con LLM (versión gratuita)

### Frontend
- **HTML5/CSS3/JavaScript** - Tecnologías web estándar
- **Bootstrap 5** - Framework CSS gratuito
- **Chart.js** - Librería de gráficos gratuita

### IA y Procesamiento
- **Hugging Face Transformers** - Modelos de IA gratuitos
- **Sentence Transformers** - Embeddings para búsqueda semántica (gratuito)
- **FAISS** - Base de datos vectorial para búsqueda rápida (gratuito)
- **RAG (Retrieval Augmented Generation)** - Sistema de recuperación de información

### Almacenamiento
- **SQLite** - Base de datos para historial (gratuita)
- **FAISS/Vector DB** - Base de datos vectorial para documentos (gratuita)
- **File System** - Almacenamiento de documentos cargados

### Deployment
- **DigitalOcean** - $200 crédito gratis (60 días) - Ver `DESPLIEGUE_DIGITALOCEAN.md`
- **Railway** - $5 crédito gratis (30 días) - Ver `DESPLIEGUE_RAILWAY.md` - Más fácil
- **Docker** - Containerización para fácil despliegue
- **GitHub** - Control de versiones gratuito

## 📁 Estructura del Proyecto

```
ARB-BOT/
├── README.md
├── requirements.txt
├── .env.example
├── app.py                 # Aplicación Flask principal
├── config.py              # Configuración del sistema
├── models/
│   ├── __init__.py
│   └── ai_model.py        # Lógica de modelos de IA
├── services/
│   ├── __init__.py
│   ├── text_processor.py  # Procesamiento de texto
│   └── generator.py       # Generación de contenido
├── utils/
│   ├── __init__.py
│   └── helpers.py         # Funciones auxiliares
├── database/
│   └── db.py             # Configuración de base de datos
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
    ├── index.html
    └── results.html
```

## 🚀 Instalación y Uso

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd ARB-BOT
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus API keys (opcional para prototipo básico)
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

6. **Acceder a la aplicación**
   - Abrir navegador en: `http://localhost:5000`

## 🌐 Desplegar en la Nube (Gratis)

¿Quieres que tu chatbot esté disponible en internet? 

### 🏆 Recomendado: Railway (Más fácil y mejor que Render)
- ✅ $5 crédito gratis (30 días) + $1/mes crédito después
- ✅ No se suspende por inactividad (a diferencia de Render)
- ✅ Auto-deploy desde GitHub
- ✅ HTTPS automático
- 📖 Ver guía: **[DESPLIEGUE_RAILWAY.md](DESPLIEGUE_RAILWAY.md)**

### 🐳 Alternativa: DigitalOcean (Más tiempo gratis)
- ✅ $200 crédito gratis (60 días)
- ✅ Control total del servidor
- ✅ 1GB RAM ($6/mes con crédito)
- 📖 Ver guía: **[DESPLIEGUE_DIGITALOCEAN.md](DESPLIEGUE_DIGITALOCEAN.md)**

**📊 ¿No sabes cuál elegir?** Ver comparación completa: **[COMPARACION_HOSTING.md](COMPARACION_HOSTING.md)**

**Recomendación para demo universidad:**
- **Railway** ⭐ - Más fácil, no se suspende, casi gratis ($1/mes crédito)
- **DigitalOcean** - Si quieres máximo tiempo gratis con el crédito

## 🔧 Configuración

### Variables de Entorno

El archivo `.env` puede contener las siguientes variables (todas opcionales para el prototipo básico):

```env
# API Keys (opcionales - el sistema funciona sin ellas en modo demo)
HUGGINGFACE_API_KEY=tu_api_key_aqui
OPENAI_API_KEY=tu_api_key_aqui

# Configuración de la aplicación
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu_secret_key_aqui
```

## 📊 Funcionalidades Completas

### 1. Sistema RAG (Retrieval Augmented Generation)
- ✅ **Carga de Documentos** - Sube manual de convivencia, reglamentos, PDFs, DOCX
- ✅ **Procesamiento Automático** - Extrae y divide texto en chunks
- ✅ **Embeddings** - Convierte documentos en vectores para búsqueda semántica
- ✅ **Búsqueda Inteligente** - Encuentra información relevante para cada pregunta
- ✅ **Respuestas Contextuales** - Genera respuestas basadas en documentos cargados

### 2. Chatbot Institucional
- ✅ **Preguntas y Respuestas** - Padres y estudiantes pueden hacer preguntas
- ✅ **Respuestas Precisas** - Basadas únicamente en documentos institucionales
- ✅ **Múltiples Documentos** - Soporta varios documentos simultáneamente
- ✅ **Fuentes Citadas** - Muestra de dónde viene la información

### 2. Sistema de Conversaciones
- ✅ Historial completo de interacciones
- ✅ Gestión de múltiples conversaciones
- ✅ Búsqueda en historial
- ✅ Exportación de conversaciones

### 3. Interfaz de Usuario
- ✅ Dashboard interactivo y moderno
- ✅ Visualización en tiempo real
- ✅ Diseño responsive (móvil y desktop)
- ✅ Modo oscuro/claro
- ✅ Estadísticas visuales

### 4. Gestión de Modelos
- ✅ Selección de modelo en tiempo real
- ✅ Información de cada modelo
- ✅ Cambio dinámico de modelo
- ✅ Comparación de resultados

### 5. Base de Datos
- ✅ Almacenamiento persistente
- ✅ Historial de conversaciones
- ✅ Métricas y estadísticas
- ✅ Backup automático

## 🧠 Lógica del Sistema

### Flujo Principal

1. **Recepción de Input**
   - Usuario ingresa texto/pregunta
   - Validación y sanitización

2. **Procesamiento**
   - Análisis semántico
   - Extracción de intención
   - Preparación de contexto

3. **Generación**
   - Consulta a modelo de IA
   - Generación de respuesta
   - Post-procesamiento

4. **Respuesta**
   - Formateo de salida
   - Presentación al usuario
   - Almacenamiento en BD

## 🔐 Seguridad y Privacidad

- Validación de inputs
- Sanitización de datos
- Manejo seguro de API keys
- No almacenamiento de información sensible

## 📝 Notas Importantes

- ✅ **Sistema completamente funcional** - Listo para usar
- ✅ **100% Gratuito** - Sin costos ocultos
- ✅ **Código abierto** - Todas las herramientas son open source
- ✅ **Sin límites estrictos** - Los modelos se ejecutan localmente
- ✅ **Privacidad total** - Todo se procesa localmente
- ✅ **Escalable** - Fácil de expandir con más funcionalidades

## 🤝 Contribuciones

Este es un prototipo académico. Las mejoras y sugerencias son bienvenidas.

## 📄 Licencia

Este proyecto es de uso educativo y demostrativo.

## 👨‍💻 Autor

Jean Carlos Páez Ramírez

---

**Nota**: Este prototipo demuestra cómo se puede construir un sistema de IA generativa utilizando únicamente herramientas gratuitas, manteniendo la funcionalidad y demostrando la tecnología subyacente.

