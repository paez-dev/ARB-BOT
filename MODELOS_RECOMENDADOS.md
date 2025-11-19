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

## 🎯 Recomendación Final

Para tu demo universitaria en español:

**Usa: `microsoft/DialoGPT-medium`**

- Mejor calidad de respuestas
- Entrenado para conversaciones
- Funciona bien con RAG
- Aceptable en español (aunque no esté entrenado específicamente en español)

Si necesitas mejor español, usa: `PlanTL-GOB-ES/gpt2-base-bne`

---

## ⚙️ Configuración Actual

Tu modelo actual es: `distilgpt2` (básico, no recomendado)

Para cambiarlo, agrega en Railway:
```
DEFAULT_MODEL=microsoft/DialoGPT-medium
```

