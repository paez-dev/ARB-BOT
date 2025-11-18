# 🔥 Warmup de Modelos en Render

## ⚠️ Problema: Primera Consulta Lenta

Con **lazy loading** (carga bajo demanda), la **primera consulta** será más lenta porque:
- Debe cargar el modelo de IA (~30-60 segundos)
- Debe cargar el modelo de embeddings (~10-20 segundos)
- Total: **40-80 segundos** en la primera consulta

**Después de la primera carga, las consultas serán rápidas** (2-5 segundos).

---

## ✅ Solución: Endpoint de Warmup

He agregado un endpoint `/api/warmup` que permite pre-cargar los modelos **después** de que Render esté listo.

### Opción 1: Warmup Manual (Recomendado)

Una vez que Render esté desplegado y funcionando:

1. **Abre tu app en Render:** `https://tu-app.onrender.com`
2. **Ve al endpoint de warmup:**
   ```
   https://tu-app.onrender.com/api/warmup
   ```
   O usa curl:
   ```bash
   curl -X POST https://tu-app.onrender.com/api/warmup
   ```
3. **Espera 30-60 segundos** mientras carga los modelos
4. **¡Listo!** Ahora las consultas serán rápidas

### Opción 2: Warmup Automático con Render Health Check

Puedes configurar Render para hacer warmup automático:

1. En Render Dashboard → Tu servicio → Settings
2. Agrega un **Health Check Path:**
   ```
   /api/warmup
   ```
3. Render llamará automáticamente después del deploy

### Opción 3: Script de Warmup (Avanzado)

Crea un script que se ejecute después del deploy:

```bash
# warmup.sh
#!/bin/bash
sleep 10  # Esperar que la app esté lista
curl -X POST https://tu-app.onrender.com/api/warmup
```

---

## 📊 Comparación

### Sin Warmup (Lazy Loading)
- **Primera consulta:** 40-80 segundos ⏱️
- **Consultas siguientes:** 2-5 segundos ⚡
- **Memoria al inicio:** ~50MB 💾

### Con Warmup
- **Primera consulta:** 2-5 segundos ⚡
- **Consultas siguientes:** 2-5 segundos ⚡
- **Memoria al inicio:** ~500MB 💾 (puede causar "out of memory")

---

## 🎯 Recomendación para Render Free Tier

**Mejor estrategia:**
1. Deja lazy loading activado (evita "out of memory")
2. Después del deploy, haz un warmup manual
3. Los modelos se mantendrán cargados mientras la app esté activa
4. Si la app "duerme" (15 min sin uso), el próximo warmup será necesario

---

## 🔧 Cómo Usar el Warmup

### Desde el Navegador:
```
https://tu-app.onrender.com/api/warmup
```
(Haz clic o usa POST request)

### Desde Terminal:
```bash
curl -X POST https://tu-app.onrender.com/api/warmup
```

### Desde JavaScript (en tu app):
```javascript
fetch('/api/warmup', { method: 'POST' })
  .then(res => res.json())
  .then(data => console.log('Modelos cargados:', data));
```

---

## ⚡ Alternativa: Warmup Automático en el Frontend

Puedes agregar esto en `static/js/app.js` para hacer warmup automático cuando alguien abre la app:

```javascript
// Warmup automático al cargar la página (solo una vez)
if (!sessionStorage.getItem('warmup_done')) {
    fetch('/api/warmup', { method: 'POST' })
        .then(() => {
            sessionStorage.setItem('warmup_done', 'true');
            console.log('Modelos pre-cargados');
        })
        .catch(err => console.log('Warmup opcional falló:', err));
}
```

---

**Conclusión:** El lazy loading es necesario para Render Free Tier. Usa el warmup después del deploy para tener la mejor experiencia.

