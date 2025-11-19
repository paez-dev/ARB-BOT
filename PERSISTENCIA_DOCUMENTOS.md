# 💾 Persistencia de Documentos en Render

## ⚠️ Problema: Almacenamiento Efímero en Render Free Tier

En Render (plan gratuito), el sistema de archivos es **efímero**, lo que significa:
- ✅ Los documentos se guardan mientras el servicio está activo
- ❌ Si el servicio se reinicia o "duerme" (15 min sin uso), los archivos pueden perderse
- ❌ No hay garantía de persistencia a largo plazo

## ✅ Soluciones Disponibles

### Opción 1: Render Disk (Solo Planes de Pago) ❌

**⚠️ Render Disk NO está disponible en el plan gratuito.** Solo está disponible en planes de pago.

Si actualizas a un plan de pago:
- Los archivos se guardarán en `/persistent` automáticamente
- El código ya está preparado para detectarlo
- Persistencia garantizada

**Costo:** Desde $7/mes aproximadamente

### Opción 2: Supabase Storage (GRATIS - Recomendado) ✅

**Supabase** ofrece almacenamiento de archivos gratuito (hasta 1GB):

**Ventajas:**
- ✅ 100% Gratuito (hasta 1GB)
- ✅ Persistente (no se pierde)
- ✅ Fácil de integrar
- ✅ API REST simple

**Cómo implementar:**
1. Crear cuenta en [supabase.com](https://supabase.com) (gratis)
2. Crear un proyecto
3. Activar Storage
4. Obtener API keys
5. Modificar código para guardar en Supabase

**¿Quieres que implemente Supabase Storage?** Puedo agregarlo fácilmente.

### Opción 3: Cloudinary (GRATIS) ✅

**Cloudinary** ofrece almacenamiento gratuito para documentos:

**Ventajas:**
- ✅ Gratis (hasta 25GB/mes)
- ✅ Persistente
- ✅ CDN incluido
- ✅ Fácil de usar

**Limitación:**
- Principalmente para imágenes, pero acepta PDFs

### Opción 4: Aceptar Limitación del Free Tier

**Para uso en desarrollo/testing:**
- Los documentos se guardan mientras el servicio está activo
- Si el servicio "duerme", se pierden
- **Solución:** Subir documentos nuevamente cuando sea necesario
- **Ventaja:** No requiere configuración adicional

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

