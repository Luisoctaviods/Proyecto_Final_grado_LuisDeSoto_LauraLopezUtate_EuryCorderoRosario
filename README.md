# 🤖 inchat - Chatbot Universitario

Un chatbot inteligente desarrollado con Flask y OpenAI que utiliza una base de conocimiento personalizable para responder preguntas sobre una universidad.

## ✨ Características

- 🔐 **Sistema de autenticación** completo (registro y login)
- 💬 **Chat en tiempo real** con IA
- 📚 **Base de conocimiento** personalizable
- 📱 **Diseño responsive** (PC y móvil)
- 🗄️ **Almacenamiento en MongoDB**
- 🎨 **Interfaz moderna** 

## 🏗️ Estructura del Proyecto

```
inchat/
├── app.py                 # Aplicación Flask principal
├── setup.py              # Script de configuración automática
├── requirements.txt      # Dependencias de Python
├── .env.example          # Archivo de configuración de ejemplo
├── README.md             # Este archivo
└── templates/
    ├── base.html         # Template base
    ├── login.html        # Pantalla de login/registro
    ├── chat.html         # Pantalla de chat
    └── admin_knowledge.html # Administración de base de conocimiento
```

## 🚀 Instalación Rápida

### Prerrequisitos

1. **Python 3.7+** instalado
2. **MongoDB** instalado y ejecutándose
3. **Cuenta de OpenAI** con API key

### Instalación Automática

1. **Clona o descarga** todos los archivos del proyecto
2. **Ejecuta el script de configuración**:
   ```bash
   python setup.py
   ```
3. **Sigue las instrucciones** del script para configurar:
   - API Key de OpenAI
   - Clave secreta de Flask
   - URI de MongoDB (opcional)

4. **Ejecuta la aplicación**:
   ```bash
   python app.py
   ```

5. **Abre tu navegador** en `http://localhost:5000`

### Instalación Manual

Si prefieres configurar manualmente:

1. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configura las variables de entorno**:
   ```bash
   cp .env.example .env
   # Edita .env con tus configuraciones
   ```

3. **Configura MongoDB** creando las colecciones:
   - `users`
   - `chat_sessions` 
   - `messages`
   - `knowledge_base`

## 🗄️ Estructura de Base de Datos

### Colección `users`
```javascript
{
  "_id": ObjectId,
  "nombre_completo": "string",
  "email": "string",
  "password": "string (hash)",
  "fecha_registro": "datetime",
  "activo": "boolean"
}
```

### Colección `chat_sessions`
```javascript
{
  "_id": ObjectId,
  "user_id": "ObjectId (referencia a users)",
  "titulo": "string",
  "fecha_creacion": "datetime",
  "activa": "boolean"
}
```

### Colección `messages`
```javascript
{
  "_id": ObjectId,
  "session_id": "ObjectId (referencia a chat_sessions)",
  "tipo": "string (user/assistant)",
  "contenido": "string",
  "timestamp": "datetime"
}
```

### Colección `knowledge_base`
```javascript
{
  "_id": ObjectId,
  "titulo": "string",
  "contenido": "string",
  "tipo": "string (documento/enlace)",
  "url": "string (opcional)",
  "activo": "boolean",
  "fecha_subida": "datetime"
}
```

## 🎯 Uso

### Para Usuarios

1. **Registro**: Crea una cuenta nueva con nombre, email y contraseña
2. **Login**: Inicia sesión con tus credenciales
3. **Chat**: Haz preguntas sobre la universidad y recibe respuestas inteligentes
4. **Historial**: Accede a tus conversaciones anteriores desde el sidebar

### Para Administradores

1. **Gestión de conocimiento**: Visita `/admin/knowledge`
2. **Agregar documentos**: Sube información sobre la universidad
3. **Tipos de contenido**:
   - **Documentos**: Texto con información
   - **Enlaces**: URLs con descripción

## 🎨 Diseño Responsive

La aplicación se adapta automáticamente a diferentes tamaños de pantalla:

- **Desktop**: Sidebar visible, layout completo
- **Mobile**: Sidebar colapsable, interfaz optimizada para touch

## 🔧 Configuración Avanzada

### Personalizar el Prompt del Sistema

Edita la función `send_message()` en `app.py` para modificar cómo responde el chatbot:

```python
system_message = f"""Eres un asistente virtual de inchat para una universidad. 
Utiliza la siguiente información de la base de conocimiento para responder:

{knowledge_context}

Responde de manera útil y amigable, basándote en la información proporcionada."""
```

### Agregar Autenticación de Admin

Para proteger `/admin/knowledge`, puedes agregar autenticación específica:

```python
@app.route('/admin/knowledge')
def manage_knowledge():
    # Verificar si el usuario es admin
    if not is_admin(session.get('user_id')):
        return redirect(url_for('index'))
    # ... resto del código
```

## 🚨 Solución de Problemas

### Error de conexión a MongoDB
```bash
# Verificar que MongoDB esté ejecutándose
sudo systemctl status mongod  # Linux
brew services list | grep mongodb  # macOS
```

### Error de API Key de OpenAI
- Verifica que tu API key sea válida
- Asegúrate de tener créditos disponibles en tu cuenta
- Comprueba que la key esté correctamente en el archivo `.env`

### Problemas de dependencias
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## 📱 Características del Diseño

### Pantalla de Login/Registro
- ✅ Tabs intercambiables
- ✅ Validación en tiempo real
- ✅ Mensajes de error/éxito
- ✅ Diseño idéntico a los mockups

### Pantalla de Chat
- ✅ Sidebar con historial de conversaciones
- ✅ Mensajes con avatares y timestamps
- ✅ Input con auto-resize
- ✅ Indicadores de carga
- ✅ Responsive para móvil

### Colores y Estilo
- 🎨 Fondo claro
- 🔴 Acentos rojos (#ff3333)
- 📱 Totalmente responsive
- ✨ Animaciones suaves

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que MongoDB esté ejecutándose
4. Comprueba que tu API key de OpenAI sea válida

## 🔜 Próximas Características

- [ ] Sistema de roles (admin/usuario)
- [ ] Carga de archivos PDF para la base de conocimiento
- [ ] Exportación de conversaciones
- [ ] Métricas y analíticas
- [ ] Integración con más modelos de IA
- [ ] API REST para integraciones externas

---

¡Disfruta usando inchat! 🎉
