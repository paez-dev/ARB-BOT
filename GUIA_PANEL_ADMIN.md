# 🔧 Guía del Panel de Administración

## 📍 Cómo Acceder al Panel de Administración

### Paso 1: Abrir el Panel
1. En la parte superior derecha del chat, verás dos botones:
   - **⚙️ (Engranaje)**: Panel de administración
   - **🕐 (Reloj)**: Historial de conversaciones

2. **Haz clic en el botón del engranaje (⚙️)** para abrir el panel de administración

3. El panel se desplegará justo debajo del header, mostrando dos secciones:
   - **📚 Subir Documentos Institucionales** (izquierda)
   - **⚙️ Configuración** (derecha)

### Paso 2: Cerrar el Panel
- **Haz clic nuevamente en el botón del engranaje (⚙️)** para cerrarlo
- O simplemente haz clic fuera del panel

---

## 📚 Subir Documentos Institucionales

### ¿Para qué sirve?
Permite cargar documentos (manual de convivencia, reglamentos, etc.) para que el chatbot pueda responder preguntas basándose en ellos.

### Cómo subir un documento:

1. **Abre el panel de administración** (botón ⚙️)

2. En la sección **"📚 Subir Documentos Institucionales"**:
   - Haz clic en **"Seleccionar documento"**
   - Elige un archivo desde tu computadora
   - Formatos permitidos: **PDF, DOCX, TXT**

3. Haz clic en **"📤 Subir y Procesar"**

4. Espera a que se procese (puede tardar unos segundos)

5. Verás un mensaje de confirmación y el número de documentos cargados

### Ver documentos cargados:
- En la parte inferior de la sección de documentos, verás:
  - **"Documentos cargados: X documentos"**
  - Lista de fuentes (nombres de archivos)

### Ejemplo de uso:
```
1. Abres el panel admin (⚙️)
2. Seleccionas "manual_convivencia.pdf"
3. Clic en "Subir y Procesar"
4. Esperas 10-30 segundos
5. ✅ "Documento procesado exitosamente"
6. Ahora el chatbot puede responder preguntas sobre el manual
```

---

## ⚙️ Configuración

### Cambiar el Modelo de IA:

1. En el panel de administración, sección **"⚙️ Configuración"**

2. En el menú desplegable **"Modelo de IA"**, elige:
   - **DistilGPT-2 (Rápido)**: Más rápido, menos recursos
   - **GPT-2 (Mejor Calidad)**: Mejor calidad de respuestas, más lento

3. El cambio se aplica automáticamente

### Ver Estadísticas:

En la misma sección de configuración, verás:
- **Interacciones**: Total de preguntas realizadas
- **Modelo**: Modelo actualmente activo
- **Estado**: Estado del sistema (✓ = Operativo)

---

## 🕐 Historial de Conversaciones

### Cómo acceder:
1. Haz clic en el botón **🕐 (Reloj)** en el header
2. Se abrirá un panel con todas las conversaciones guardadas
3. Verás:
   - Pregunta del usuario
   - Respuesta del bot
   - Fecha y hora
   - Modelo utilizado

### Cerrar historial:
- Haz clic nuevamente en el botón 🕐
- O haz clic en la **X** dentro del panel

---

## 💡 Consejos de Uso

### Para Administradores:

1. **Primera vez usando el sistema:**
   - Abre el panel admin (⚙️)
   - Sube el manual de convivencia
   - Sube otros documentos importantes (reglamentos, políticas, etc.)
   - Cierra el panel admin

2. **Cuando quieras actualizar documentos:**
   - Abre el panel admin
   - Sube el nuevo documento
   - El sistema lo procesará y agregará a la base de conocimiento

3. **Para cambiar el modelo:**
   - Si las respuestas son muy lentas → Usa **DistilGPT-2**
   - Si quieres mejor calidad → Usa **GPT-2**

### Para Usuarios Finales:

- **No necesitas el panel de administración**
- Solo haz preguntas en el chat
- El chatbot responderá basándose en los documentos que el administrador haya cargado

---

## 🔒 Seguridad

**Nota importante:**
- Actualmente el panel de administración es accesible para todos
- Si quieres restringir el acceso, puedes:
  1. Agregar autenticación (usuario/contraseña)
  2. Ocultar el botón del panel admin
  3. Usar una ruta secreta (ej: `/admin`)

**¿Quieres que agregue autenticación al panel de admin?** Puedo implementarlo si lo necesitas.

---

## ❓ Preguntas Frecuentes

### ¿Puedo subir múltiples documentos?
**Sí**, puedes subir tantos documentos como necesites. Cada uno se procesará y agregará al conocimiento del chatbot.

### ¿Qué pasa si subo el mismo documento dos veces?
El sistema lo procesará nuevamente y puede duplicar información. Es mejor subir cada documento solo una vez.

### ¿Cuánto tiempo tarda en procesar un documento?
- **PDF pequeño (< 10 páginas)**: 5-15 segundos
- **PDF mediano (10-50 páginas)**: 15-30 segundos
- **PDF grande (> 50 páginas)**: 30-60 segundos
- **DOCX/TXT**: Generalmente más rápido que PDF

### ¿Puedo eliminar documentos?
Actualmente no hay una función para eliminar documentos individuales. Si necesitas limpiar todo, puedes:
- Eliminar el archivo `rag_index.json` (se regenerará)
- O contactarme para agregar esta funcionalidad

### ¿Los documentos se guardan en el servidor?
Sí, los documentos se guardan en la carpeta `documents/` del servidor. En Render (plan gratuito), estos archivos se mantienen mientras el servicio esté activo.

---

## 🎯 Resumen Rápido

1. **Abrir panel**: Clic en ⚙️ (header superior derecha)
2. **Subir documento**: Seleccionar archivo → Clic en "Subir y Procesar"
3. **Cambiar modelo**: Seleccionar en el menú desplegable
4. **Ver estadísticas**: Se muestran automáticamente en el panel
5. **Cerrar panel**: Clic nuevamente en ⚙️

¡Listo! Ya sabes cómo usar el panel de administración. 🚀

