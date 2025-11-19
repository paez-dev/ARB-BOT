# 💾 Persistencia de Documentos en Railway

## ⚠️ Problema: Almacenamiento Efímero en Railway

En Railway (plan gratuito), el sistema de archivos es **efímero**, lo que significa:
- ✅ Los documentos se guardan mientras el servicio está activo
- ❌ Si el servicio se reinicia, los archivos pueden perderse
- ❌ No hay garantía de persistencia a largo plazo

## ✅ Soluciones Disponibles

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

## 🔧 Implementación Rápida: Supabase Storage

Si quieres que implemente la opción de Supabase Storage, puedo:
1. Modificar el código para usar `/persistent` cuando esté disponible
2. Mantener compatibilidad con `./documents` para desarrollo local
3. Agregar detección automática del disco persistente

## 📊 Estado Actual

**Actualmente:**
- ✅ Los documentos se guardan en `documents/`
- ✅ El índice se guarda en `rag_index.json`
- ✅ Se cargan automáticamente al iniciar
- ⚠️ **PERO** pueden perderse si Railway reinicia el servicio

**Recomendación:**
- Para desarrollo/testing: Funciona bien
- Para producción: Usar Supabase Storage (recomendado) o almacenamiento externo

## ❓ ¿Quieres que implemente Supabase Storage?

Puedo modificar el código para usar Supabase Storage automáticamente. Ver guía: [CONFIGURAR_SUPABASE.md](CONFIGURAR_SUPABASE.md)

