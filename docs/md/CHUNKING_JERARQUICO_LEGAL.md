# 🏛️ Chunking Jerárquico para Documentos Legales

## 📋 Estructura del Chunking

```
TÍTULO → CAPÍTULO → Artículo → Párrafo(s)
```

Cada chunk mantiene la jerarquía completa en metadatos.

## 🎯 Metadatos por Chunk

- `title`: "TÍTULO I", "TÍTULO II", etc.
- `chapter`: "CAPÍTULO I", "CAPÍTULO II", etc.
- `article`: "Artículo 5", "Artículo 52", etc.
- `paragraph`: Número de párrafo si aplica
- `page`: Número de página
- `keywords`: Palabras clave extraídas
- `source`: Nombre del archivo
- `chunk_tokens`: Tamaño en tokens

## 📊 Tamaño de Chunks

- **Ideal:** 800-1800 tokens
- **Overlap:** 150-250 tokens entre chunks relacionados
- **Mínimo:** 200 tokens (para mantener contexto)
- **Máximo:** 2500 tokens (artículos muy largos se dividen)

## 🔍 Detección de Estructura

### Patrones Detectados:

1. **Títulos:** `TÍTULO I`, `TÍTULO II`, `TÍTULO III`, etc.
2. **Capítulos:** `CAPÍTULO I`, `CAPÍTULO II`, `CAPÍTULO III`, etc.
3. **Artículos:** `Artículo 1`, `Artículo 2`, `Art. 52`, etc.
4. **Párrafos:** `Parágrafo 1.`, `Parágrafo 2.`, etc.

## ✅ Ventajas

- ✅ Respeta estructura legal del documento
- ✅ Mantiene contexto jurídico completo
- ✅ Facilita búsquedas por artículo específico
- ✅ Permite búsquedas vectoriales + simbólicas
- ✅ Citas precisas con referencias exactas

