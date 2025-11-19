# 🔗 Link del Panel de Administración

## 📍 Ubicación del Panel Admin

**El panel de administración está en la MISMA URL de tu aplicación.**

No hay un link separado. El panel admin está integrado en la interfaz principal.

---

## 🎯 Cómo Acceder al Panel Admin

### Paso 1: Abre tu Aplicación

Abre el link de tu aplicación en Render:
```
https://tu-app.onrender.com
```

O el link que Render te haya asignado (ej: `https://arb-bot-xxxx.onrender.com`)

### Paso 2: Busca el Botón del Engranaje

En la parte **superior derecha** del header (donde dice "🤖 ARB-BOT"), verás dos botones:

- **⚙️ (Engranaje)** = Panel de Administración
- **🕐 (Reloj)** = Historial de Conversaciones

### Paso 3: Haz Clic en el Botón ⚙️

Al hacer clic, se desplegará el panel de administración justo debajo del header.

---

## 🔗 Ejemplo Completo

Si tu aplicación está en:
```
https://arb-bot.onrender.com
```

Para acceder al panel admin:
1. Ve a: `https://arb-bot.onrender.com`
2. Haz clic en el botón **⚙️** (arriba a la derecha)
3. ¡Listo! El panel admin se abrirá

**No necesitas agregar nada al link**, es la misma URL.

---

## 🎨 Visualización

```
┌─────────────────────────────────────────┐
│  🤖 ARB-BOT    [En línea]  [⚙️] [🕐]  │  ← Header (siempre visible)
├─────────────────────────────────────────┤
│                                         │
│  [Panel Admin se abre aquí cuando      │  ← Panel Admin (oculto por defecto)
│   haces clic en ⚙️]                    │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  💬 Chat principal                     │  ← Área de chat
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔒 ¿Quieres un Link Separado?

Actualmente, el panel admin está integrado en la misma página. Si quieres un link separado (ej: `/admin`), puedo agregarlo.

**Opciones:**
1. **Mantener como está** (botón ⚙️ en el header) - ✅ Más simple
2. **Agregar ruta `/admin`** - Requiere autenticación para seguridad

¿Quieres que agregue una ruta separada `/admin` con autenticación?

---

## 📝 Resumen

- **URL de la app:** `https://tu-app.onrender.com`
- **Panel admin:** Misma URL + clic en botón ⚙️
- **No hay link separado:** Todo está en la misma página
- **Acceso:** Cualquiera puede ver el botón ⚙️ (si quieres protegerlo, necesitamos autenticación)

---

## ❓ Preguntas Frecuentes

### ¿Puedo compartir solo el panel admin?
No hay un link separado. El panel está en la misma URL. Si quieres que solo ciertas personas accedan, necesitaríamos agregar autenticación.

### ¿El panel admin es visible para todos?
Sí, actualmente cualquiera que tenga el link de la aplicación puede:
- Ver el botón ⚙️
- Abrir el panel admin
- Subir documentos
- Cambiar configuración

Si quieres protegerlo, puedo agregar:
- Usuario/contraseña
- O ocultar el botón y usar una ruta secreta como `/admin-secreto-123`

### ¿Cómo oculto el panel admin de usuarios normales?
Puedo hacer que el botón ⚙️ solo aparezca si accedes desde una URL especial como:
- `https://tu-app.onrender.com/admin` (con contraseña)
- O simplemente ocultar el botón en el HTML

**¿Quieres que agregue protección al panel admin?**

