# 🏛️ Guía: Chunking Jerárquico para Documentos Legales

## 📋 ¿Qué es el Chunking Jerárquico?

El chunking jerárquico es una técnica optimizada para documentos legales (Manuales de Convivencia, Reglamentos, Leyes) que respeta la estructura legal del documento.

## 🎯 Estructura Detectada

```
TÍTULO → CAPÍTULO → Artículo → Párrafo(s)
```

Cada chunk mantiene la jerarquía completa en metadatos.

## 📊 Metadatos por Chunk

Cada chunk incluye:

- `source`: Nombre del archivo
- `title`: "TÍTULO I", "TÍTULO II", etc.
- `chapter`: "CAPÍTULO I", "CAPÍTULO II", etc.
- `article`: "Artículo 5", "Artículo 52", etc.
- `paragraph`: "Parágrafo 1", "Parágrafo 2", etc. (si aplica)
- `page`: Número de página
- `keywords`: Palabras clave extraídas automáticamente
- `chunk_tokens`: Tamaño en tokens
- `ingestion_date`: Fecha de procesamiento

## 📏 Tamaño de Chunks

- **Ideal:** 800-1800 tokens
- **Overlap:** 150-250 tokens entre chunks relacionados
- **Mínimo:** 200 tokens (para mantener contexto)
- **Máximo:** 2500 tokens (artículos muy largos se dividen automáticamente)

## ✅ Ventajas

1. **Respeta estructura legal** - No mezcla artículos
2. **Búsquedas precisas** - Fácil encontrar "artículo 52"
3. **Citas exactas** - Referencias precisas con metadatos
4. **Búsquedas híbridas** - Vectoriales + simbólicas (por metadata)
5. **Contexto completo** - Cada chunk mantiene contexto jurídico

## 🔍 Ejemplo de Búsqueda

**Usuario pregunta:** "¿Qué dice el artículo 52?"

**El sistema:**
1. Busca en metadata: `article = "Artículo 52"`
2. Si no encuentra, busca vectorialmente
3. Retorna el chunk completo con contexto

**Resultado:** Chunk con metadata completa:
```json
{
  "title": "TÍTULO II",
  "chapter": "CAPÍTULO IV",
  "article": "Artículo 52",
  "page": 45,
  "keywords": ["deberes", "estudiantes", "responsabilidades"]
}
```

## 📚 Uso en Colab

El notebook `INGESTA_DOCUMENTOS_COLAB.ipynb` ya incluye la función `chunk_hierarchical_legal()`.

Solo ejecuta:
```python
chunks = chunk_hierarchical_legal(
    pdf_data['text'],
    file_name,
    pages=pdf_data.get('pages')
)
```

## 🎯 Resultado Esperado

Para un Manual de Convivencia de 193 páginas:
- **~1,000-1,200 chunks** (ideal)
- Cada artículo completo en uno o pocos chunks
- Metadata completa para búsquedas precisas
- Fácil encontrar cualquier artículo específico

