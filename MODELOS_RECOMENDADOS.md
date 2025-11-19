# 🤖 Modelos Recomendados para ARB-BOT

## 📊 Comparación de Modelos

| Modelo | Tamaño | Calidad | Español | Conversación | Recomendado |
|--------|--------|---------|---------|--------------|-------------|
| `distilgpt2` | ~250MB | ⭐⭐ | ❌ | ❌ | ❌ No recomendado |
| `gpt2` | ~500MB | ⭐⭐⭐ | ❌ | ❌ | ✅ Sí |
| `microsoft/DialoGPT-small` | ~250MB | ⭐⭐⭐⭐ | ❌ | ✅ | ✅✅ Muy recomendado |
| `microsoft/DialoGPT-medium` | ~500MB | ⭐⭐⭐⭐⭐ | ❌ | ✅ | ✅✅✅ Excelente |
| `facebook/blenderbot-small-90M` | ~350MB | ⭐⭐⭐⭐ | ❌ | ✅ | ✅✅ Muy recomendado |
| `PlanTL-GOB-ES/gpt2-base-bne` | ~500MB | ⭐⭐⭐ | ✅ | ❌ | ✅✅ Para español |
| `microsoft/DialoGPT-large` | ~1.5GB | ⭐⭐⭐⭐⭐ | ❌ | ✅ | ⚠️ Muy pesado |
| `facebook/blenderbot-400M-distill` | ~800MB | ⭐⭐⭐⭐⭐ | ❌ | ✅ | ✅✅ Excelente |
| `EleutherAI/gpt-neo-125M` | ~500MB | ⭐⭐⭐ | ❌ | ❌ | ✅ Alternativa |
| `EleutherAI/gpt-neo-1.3B` | ~5GB | ⭐⭐⭐⭐ | ❌ | ❌ | ⚠️ Muy pesado |
| `bigscience/bloom-560m` | ~1.1GB | ⭐⭐⭐⭐ | ✅ Multilingüe | ❌ | ✅ Para múltiples idiomas |

---

## 🆕 Modelos Adicionales Gratuitos (Hugging Face)

### Modelos Más Grandes y Potentes

**1. `microsoft/DialoGPT-large`** ⭐⭐⭐⭐⭐
- ✅ Mejor calidad que medium
- ✅ Excelente para conversaciones
- ⚠️ ~1.5GB (requiere más RAM)
- ⚠️ Puede ser lento en Railway Hobby (2GB RAM)

**2. `facebook/blenderbot-400M-distill`** ⭐⭐⭐⭐⭐
- ✅ Entrenado específicamente para chatbots
- ✅ Respuestas muy coherentes
- ✅ Mejor que BlenderBot-small
- ⚠️ ~800MB

**3. `EleutherAI/gpt-neo-125M`** ⭐⭐⭐
- ✅ Alternativa a GPT-2
- ✅ Código abierto
- ⚠️ Similar calidad a GPT-2

**4. `EleutherAI/gpt-neo-1.3B`** ⭐⭐⭐⭐
- ✅ Mucho más potente que GPT-2
- ✅ Código abierto
- ⚠️ ~5GB (demasiado pesado para Railway Hobby)

**5. `bigscience/bloom-560m`** ⭐⭐⭐⭐
- ✅ Multilingüe (incluye español)
- ✅ Entrenado en múltiples idiomas
- ⚠️ ~1.1GB

### Modelos Específicos para Español

**1. `dccuchile/bert-base-spanish-wwm-uncased`**
- ✅ BERT en español (para embeddings, no generación)

**2. `mrm8488/distilroberta-finetuned-spanish-squad2`**
- ✅ Modelo de pregunta-respuesta en español

---

## 🏆 Recomendaciones por Caso de Uso

### Para Demo Universitaria (Español)

**Opción 1: `microsoft/DialoGPT-medium`** ⭐⭐⭐⭐⭐
- ✅ Entrenado para conversaciones
- ✅ Mejor calidad de respuestas
- ✅ Funciona bien con contexto RAG
- ⚠️ ~500MB (funciona con 2GB RAM)

**Opción 2: `PlanTL-GOB-ES/gpt2-base-bne`** ⭐⭐⭐⭐
- ✅ Entrenado específicamente en español
- ✅ Mejor comprensión de español
- ✅ Funciona bien con contexto
- ⚠️ ~500MB

**Opción 3: `microsoft/DialoGPT-small`** ⭐⭐⭐⭐
- ✅ Entrenado para conversaciones
- ✅ Más ligero (~250MB)
- ✅ Buena calidad
- ✅ Funciona con menos RAM

---

## 🚀 Cómo Cambiar el Modelo

### Opción 1: Variable de Entorno (Recomendado)

En Railway → Settings → Variables, agrega:

```env
DEFAULT_MODEL=microsoft/DialoGPT-medium
```

O para español:

```env
DEFAULT_MODEL=PlanTL-GOB-ES/gpt2-base-bne
```

### Opción 2: Archivo .env

Edita `env.example` y renómbralo a `.env`:

```env
DEFAULT_MODEL=microsoft/DialoGPT-medium
```

---

## 📝 Notas Importantes

1. **Primera carga:** Los modelos más grandes tardan más en cargar (30-60 segundos)
2. **Memoria:** Con 2GB RAM en Railway Hobby, todos estos modelos funcionan
3. **Calidad:** DialoGPT y BlenderBot dan respuestas más coherentes
4. **Español:** `PlanTL-GOB-ES/gpt2-base-bne` es el mejor para español puro

---

## 🎯 Recomendación Final para Usuarios que Solo Hablan Español

**Para usuarios que SOLO hablan español, usa: `PlanTL-GOB-ES/gpt2-base-bne`** ⭐⭐⭐⭐

**Razones:**
- ✅ **Entrenado específicamente en español** - No responderá en inglés
- ✅ **Funciona bien con RAG** - Usa el contexto proporcionado
- ✅ **Mejor comprensión de español** - Entiende mejor las preguntas en español
- ✅ **Respuestas en español** - Garantiza que siempre responda en español
- ⚠️ No está optimizado para conversaciones (pero con RAG funciona bien)

**Alternativa si necesitas mejor calidad conversacional:**
- `microsoft/DialoGPT-medium` + Prompt en español (el código ya fuerza español)
- Mejor para conversaciones pero puede mezclar idiomas ocasionalmente

---

## ⚙️ Configuración Actual

**Modelo por defecto:** `microsoft/DialoGPT-medium` ⭐⭐⭐⭐⭐

Este es el mejor modelo para conversaciones y funciona muy bien con RAG. Si necesitas cambiarlo, agrega en Railway:
```
DEFAULT_MODEL=microsoft/DialoGPT-medium
```

O para español puro:
```
DEFAULT_MODEL=PlanTL-GOB-ES/gpt2-base-bne
```

O para mejor calidad (más pesado):
```
DEFAULT_MODEL=microsoft/DialoGPT-large
```

O para chatbots (muy buena calidad):
```
DEFAULT_MODEL=facebook/blenderbot-400M-distill
```

---

## ⚠️ Limitaciones de Railway Hobby (2GB RAM)

**Modelos que funcionan bien:**
- ✅ `microsoft/DialoGPT-medium` (~500MB) - **RECOMENDADO**
- ✅ `microsoft/DialoGPT-small` (~250MB)
- ✅ `gpt2` (~500MB)
- ✅ `facebook/blenderbot-small-90M` (~350MB)
- ✅ `PlanTL-GOB-ES/gpt2-base-bne` (~500MB)

**Modelos que pueden funcionar (con cuidado):**
- ⚠️ `microsoft/DialoGPT-large` (~1.5GB) - Puede ser lento
- ⚠️ `facebook/blenderbot-400M-distill` (~800MB) - Puede funcionar
- ⚠️ `bigscience/bloom-560m` (~1.1GB) - Puede funcionar

**Modelos demasiado pesados:**
- ❌ `EleutherAI/gpt-neo-1.3B` (~5GB) - No cabe en 2GB RAM
- ❌ Modelos más grandes de GPT-Neo/GPT-J

