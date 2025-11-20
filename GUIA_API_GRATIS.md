# 🚀 Guía: Usar APIs Gratuitas de Modelos Avanzados

Esta guía te muestra cómo configurar el sistema para usar APIs gratuitas de modelos avanzados en lugar de modelos locales.

## ✅ Ventajas de Usar APIs

- **Mejor calidad**: Modelos más avanzados (Llama, Gemini, etc.)
- **Más rápido**: No necesitas cargar modelos localmente
- **Menos memoria**: No consume RAM del servidor
- **Más confiable**: Los modelos están optimizados y funcionan mejor
- **100% Gratis**: Con límites generosos

## 🎯 Opciones de APIs Gratuitas

### 1. **Groq** ⭐⭐⭐⭐⭐ (RECOMENDADO)

**Por qué es el mejor:**
- ✅ **MUY rápido** (hasta 10x más rápido que otros)
- ✅ **Gratis** con límites generosos
- ✅ **Modelos Llama 3.1** (muy avanzados)
- ✅ **Fácil de configurar**

**Cómo obtener API Key:**
1. Ve a https://console.groq.com
2. Crea una cuenta (gratis)
3. Ve a "API Keys" → "Create API Key"
4. Copia la key

**Configuración:**
```env
USE_API_MODEL=true
API_PROVIDER=groq
GROQ_API_KEY=tu-key-aqui
API_MODEL_NAME=llama-3.1-8b-instant  # Opcional
```

**Modelos disponibles:**
- `llama-3.1-8b-instant` (rápido, recomendado)
- `llama-3.1-70b-versatile` (más potente)
- `mixtral-8x7b-32768` (muy bueno)

---

### 2. **Hugging Face Inference API** ⭐⭐⭐⭐

**Por qué es bueno:**
- ✅ **Muchos modelos** disponibles
- ✅ **Gratis** con límites
- ✅ **Fácil de usar**

**Cómo obtener API Key:**
1. Ve a https://huggingface.co
2. Crea una cuenta (gratis)
3. Ve a Settings → Access Tokens
4. Crea un token (tipo "Read")

**Configuración:**
```env
USE_API_MODEL=true
API_PROVIDER=huggingface
HUGGINGFACE_API_KEY=tu-token-aqui
API_MODEL_NAME=microsoft/DialoGPT-medium  # Opcional
```

**Modelos recomendados:**
- `microsoft/DialoGPT-medium`
- `meta-llama/Llama-3.1-8B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.2`

---

### 3. **Google Gemini** ⭐⭐⭐⭐

**Por qué es bueno:**
- ✅ **Muy buena calidad**
- ✅ **Gratis** con límites generosos
- ✅ **Multimodal** (puede procesar imágenes)

**Cómo obtener API Key:**
1. Ve a https://makersuite.google.com/app/apikey
2. Inicia sesión con Google
3. Crea una API key
4. Copia la key

**Configuración:**
```env
USE_API_MODEL=true
API_PROVIDER=gemini
GEMINI_API_KEY=tu-key-aqui
API_MODEL_NAME=gemini-pro  # Opcional
```

**Modelos disponibles:**
- `gemini-pro` (recomendado)
- `gemini-pro-vision` (con soporte de imágenes)

---

## 📝 Configuración en Railway

1. Ve a tu proyecto en Railway
2. Settings → Variables
3. Agrega estas variables:

### Para Groq (Recomendado):
```
USE_API_MODEL=true
API_PROVIDER=groq
GROQ_API_KEY=tu-key-de-groq
```

### Para Hugging Face:
```
USE_API_MODEL=true
API_PROVIDER=huggingface
HUGGINGFACE_API_KEY=tu-token-de-hf
```

### Para Gemini:
```
USE_API_MODEL=true
API_PROVIDER=gemini
GEMINI_API_KEY=tu-key-de-gemini
```

---

## 🔄 Cómo Funciona con RAG

El sistema funciona **exactamente igual** con APIs:

1. **RAG busca** información relevante en tus documentos
2. **Construye el prompt** con el contexto encontrado
3. **Envía a la API** el prompt completo
4. **La API genera** la respuesta basada en el contexto
5. **Retorna** la respuesta al usuario

**Ventaja**: Los modelos avanzados (Llama, Gemini) entienden mejor el contexto y generan respuestas más coherentes.

---

## 🆚 Comparación: Local vs API

| Característica | Modelo Local | API Gratuita |
|---------------|--------------|--------------|
| **Calidad** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Velocidad** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Memoria** | ⭐ (usa RAM) | ⭐⭐⭐⭐⭐ (no usa RAM) |
| **Confiabilidad** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Costo** | Gratis | Gratis |

**Recomendación**: Usa **Groq** con `llama-3.1-8b-instant` para mejor experiencia.

---

## 🐛 Solución de Problemas

### Error: "API key requerida"
- Verifica que agregaste la variable de entorno correcta
- Asegúrate de que `USE_API_MODEL=true`
- Revisa que la key no tenga espacios extra

### Error: "Modelo no encontrado"
- Verifica el nombre del modelo
- Para Groq, usa: `llama-3.1-8b-instant`
- Para Hugging Face, usa el nombre completo: `microsoft/DialoGPT-medium`

### Respuestas lentas
- Prueba con **Groq** (es el más rápido)
- Reduce `MAX_TOKENS` en la configuración
- Verifica tu conexión a internet

---

## 📊 Límites Gratuitos

### Groq
- **30,000 requests/minuto** (más que suficiente)
- Sin límite de tokens diarios
- Gratis para siempre

### Hugging Face
- **1,000 requests/día** (suficiente para demo)
- Puede aumentar con uso

### Gemini
- **60 requests/minuto**
- **1,500 requests/día**
- Gratis para siempre

---

## ✅ Próximos Pasos

1. **Elige un proveedor** (recomendado: Groq)
2. **Obtén tu API key** (gratis, 2 minutos)
3. **Agrega las variables** en Railway
4. **Redeploy** el proyecto
5. **¡Disfruta de respuestas de mejor calidad!**

---

¿Necesitas ayuda? Revisa los logs en Railway para ver qué está pasando.

