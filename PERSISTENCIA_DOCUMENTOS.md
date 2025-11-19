# 💾 Persistencia de Documentos en Render

## ⚠️ Problema: Almacenamiento Efímero en Render Free Tier

En Render (plan gratuito), el sistema de archivos es **efímero**, lo que significa:
- ✅ Los documentos se guardan mientras el servicio está activo
- ❌ Si el servicio se reinicia o "duerme" (15 min sin uso), los archivos pueden perderse
- ❌ No hay garantía de persistencia a largo plazo

## ✅ Soluciones Disponibles

### Opción 1: Render Disk (Recomendado - Gratis)

Render ofrece **disco persistente gratuito** para servicios web:

1. **En Render Dashboard:**
   - Ve a tu servicio → Settings
   - Busca "Persistent Disk"
   - Activa "Mount Persistent Disk"
   - Asigna espacio (ej: 1GB - suficiente para documentos)

2. **Configurar en el código:**
   - Los archivos se guardarán en `/persistent` en lugar de `./documents`
   - Necesitamos actualizar las rutas

**Ventajas:**
- ✅ Gratis
- ✅ Persistente (no se pierde al reiniciar)
- ✅ Fácil de configurar

### Opción 2: Base de Datos Externa (Avanzado)

Guardar documentos en una base de datos externa:
- **Supabase** (gratis): PostgreSQL con almacenamiento de archivos
- **MongoDB Atlas** (gratis): Base de datos NoSQL
- **Firebase Storage** (gratis): Almacenamiento de Google

### Opción 3: Servicios de Almacenamiento en la Nube

- **AWS S3** (gratis hasta cierto límite)
- **Google Cloud Storage** (gratis hasta cierto límite)
- **Cloudinary** (gratis para imágenes y documentos)

## 🔧 Implementación Rápida: Render Disk

Si quieres que implemente la opción de Render Disk, puedo:
1. Modificar el código para usar `/persistent` cuando esté disponible
2. Mantener compatibilidad con `./documents` para desarrollo local
3. Agregar detección automática del disco persistente

## 📊 Estado Actual

**Actualmente:**
- ✅ Los documentos se guardan en `documents/`
- ✅ El índice se guarda en `rag_index.json`
- ✅ Se cargan automáticamente al iniciar
- ⚠️ **PERO** pueden perderse si Render reinicia el servicio

**Recomendación:**
- Para desarrollo/testing: Funciona bien
- Para producción: Activar Render Disk o usar almacenamiento externo

## ❓ ¿Quieres que implemente Render Disk?

Puedo modificar el código para usar disco persistente automáticamente cuando esté disponible en Render.

