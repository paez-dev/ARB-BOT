# 🧹 Limpiar Archivos Antiguos del Bucket de Supabase

## 📋 Archivos que ya NO se necesitan

Después de migrar a **LlamaIndex con Supabase pgvector**, estos archivos en el bucket `documents` ya **NO se usan**:

- ❌ `rag_index.json` - Índice antiguo (JSON)
- ❌ `rag_index_embeddings.npy` - Embeddings antiguos (NumPy)
- ❌ Cualquier archivo que empiece con `rag_index_*`

## ✅ ¿Por qué ya no se necesitan?

**Antes (FAISS):**
- Los vectores se guardaban en archivos `.json` y `.npy` en el bucket
- Había que guardar/cargar manualmente con `save_index()` y `load_index()`

**Ahora (LlamaIndex + pgvector):**
- Los vectores se guardan **automáticamente** en PostgreSQL (pgvector)
- No se necesitan archivos manuales
- La persistencia es automática y más eficiente

## 🗑️ Cómo Eliminar los Archivos Antiguos

### Opción 1: Desde la Interfaz de Supabase (Recomendado)

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
2. Ve a **Storage** → **documents** (tu bucket)
3. Busca archivos que empiecen con `rag_index`
4. Selecciona los archivos y haz clic en **"Delete"**
5. Confirma la eliminación

### Opción 2: Desde el Código (Script)

Si quieres automatizarlo, puedes usar este script:

```python
from services.storage_service import StorageService

storage = StorageService()
if storage.use_supabase:
    # Eliminar archivos antiguos de índices
    old_files = [
        'rag_index.json',
        'rag_index_embeddings.npy'
    ]
    
    for filename in old_files:
        if storage.file_exists(filename):
            storage.delete_file(filename)
            print(f"✅ Eliminado: {filename}")
        else:
            print(f"ℹ️ No existe: {filename}")
```

## ⚠️ Importante

- **NO elimines los PDFs originales** (ej: `MANUAL_DE_CONVIVENCIA_ESCOLAR_ROLDANISTA_2023.pdf`)
- **Solo elimina** archivos que empiecen con `rag_index`
- Los PDFs se siguen usando y son necesarios

## ✅ Después de Limpiar

Una vez eliminados los archivos antiguos:
- ✅ El bucket solo tendrá los PDFs originales
- ✅ Los vectores estarán en pgvector (PostgreSQL)
- ✅ El sistema funcionará igual o mejor
- ✅ Ahorrarás espacio en el bucket

## 🎯 Verificación

Para verificar que todo está bien:
1. Sube un nuevo documento
2. Haz una pregunta al bot
3. Si funciona correctamente, todo está bien ✅

Los archivos antiguos de índices ya no se necesitan y pueden eliminarse sin problemas.

