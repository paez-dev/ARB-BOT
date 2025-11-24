# 🏗️ Arquitectura del Sistema RAG

## 📐 Diagrama de Arquitectura

```
┌─────────────────────────────────┐
│   Google Colab (Backoffice)     │
│   ───────────────────────────  │
│   ✅ Procesar PDFs              │
│   ✅ Chunking jerárquico legal  │
│   ✅ Generar embeddings         │
│   ✅ Subir a Supabase           │
└──────────────┬──────────────────┘
               │ INSERT
               ▼
┌─────────────────────────────────┐
│      Supabase (Base de Datos)    │
│   ───────────────────────────   │
│   ✅ Almacena chunks             │
│   ✅ Almacena embeddings (vec)  │
│   ✅ Almacena metadata (JSONB)   │
│   ✅ Índice vectorial (ivfflat)  │
└──────────────┬──────────────────┘
               │ QUERY
               ▼
┌─────────────────────────────────┐
│   Railway (Bot en Producción)   │
│   ───────────────────────────   │
│   ✅ Recibe preguntas            │
│   ✅ Consulta Supabase           │
│   ✅ Búsqueda híbrida            │
│   ✅ Genera respuestas (Groq)    │
│   ❌ NO procesa documentos       │
└─────────────────────────────────┘
```

## 🔄 Flujo de Datos

### 1. Ingesta (Colab)

1. **Administrador** tiene un nuevo PDF
2. **Abre Colab** → `INGESTA_FINAL_RAG.ipynb`
3. **Procesa el PDF:**
   - Extrae texto
   - Chunking jerárquico legal
   - Genera embeddings
4. **Sube a Supabase** → datos listos

### 2. Consulta (Railway)

1. **Usuario** hace una pregunta
2. **Bot en Railway:**
   - Genera embedding de la pregunta
   - Busca en Supabase (vectorial + metadata)
   - Obtiene chunks relevantes
3. **Genera respuesta** con Groq usando contexto
4. **Retorna respuesta** al usuario

## 📊 Estructura de Datos en Supabase

### Tabla: `vecs.arbot_documents`

```sql
CREATE TABLE vecs.arbot_documents (
    id TEXT PRIMARY KEY,
    vec vector(384),        -- Embedding vector
    text TEXT NOT NULL,     -- Texto del chunk (estándar LlamaIndex)
    metadata JSONB          -- Metadatos completos
);
```

### Metadata JSONB

```json
{
  "file": "MANUAL DE CONVIVENCIA ESCOLAR ROLDANISTA 2023.pdf",
  "title": "TÍTULO II",
  "chapter": "CAPÍTULO IV",
  "article": "Artículo 52",
  "paragraph": "Parágrafo 1",
  "page": 45,
  "keywords": ["deberes", "estudiantes"],
  "chunk_tokens": 850,
  "ingestion_date": "2024-01-15T10:30:00"
}
```

## 🔍 Búsqueda Híbrida

El bot usa búsqueda híbrida:

1. **Búsqueda por metadata** (rápida, precisa)
   - Si pregunta "artículo 52" → busca `metadata->>'article' = 'Artículo 52'`
   
2. **Búsqueda vectorial** (semántica)
   - Si no encuentra por metadata → busca por similitud vectorial
   
3. **Combinación** (mejor resultado)
   - Combina ambos métodos para máxima precisión

## ✅ Separación de Responsabilidades

### Colab (Backoffice)
- ✅ Procesamiento pesado
- ✅ Chunking inteligente
- ✅ Generación de embeddings
- ✅ Subida a Supabase

### Railway (Producción)
- ✅ Solo consultas
- ✅ Búsqueda rápida
- ✅ Generación de respuestas
- ❌ NO procesa documentos

## 🚀 Ventajas de esta Arquitectura

1. **Rendimiento** - Railway no hace procesamiento pesado
2. **Escalabilidad** - Colab puede procesar múltiples documentos
3. **Mantenibilidad** - Separación clara de responsabilidades
4. **Costo** - Railway solo consulta (bajo costo)
5. **Flexibilidad** - Fácil actualizar chunking sin tocar producción

