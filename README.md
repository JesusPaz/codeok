# GitHub Webhook API

API para aprobar automáticamente Pull Requests de GitHub cuando se menciona una cuenta específica.

## 🚀 Inicio Rápido

### 1. Verificar Variables de Entorno
```bash
python check_env.py
```

### 2. Probar Autenticación
```bash
python test_connection.py
```

### 3. Ejecutar la Aplicación
```bash
python run.py
```

## 📋 Configuración

### Variables de Entorno Requeridas

```bash
# GitHub App Configuration
GITHUB_CLIENT_ID=123456789012345678
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"
GITHUB_INSTALLATION_ID=12345678

# Webhook Configuration
WEBHOOK_SECRET=tu_webhook_secret
TARGET_USERNAME=tu_usuario

# Server Configuration (opcional)
HOST=0.0.0.0
PORT=8000
```

### Cómo Obtener las Variables

1. **GITHUB_CLIENT_ID**: En tu GitHub App → General → Client ID
2. **GITHUB_PRIVATE_KEY**: En tu GitHub App → General → Generate private key
3. **GITHUB_INSTALLATION_ID**: En tu GitHub App → Install App → Installation ID
4. **WEBHOOK_SECRET**: Cualquier string secreto para verificar webhooks
5. **TARGET_USERNAME**: El usuario que debe ser mencionado para aprobar PRs

### Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
export GITHUB_CLIENT_ID=tu_client_id
export GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\ntu_clave...\n-----END RSA PRIVATE KEY-----"
export GITHUB_INSTALLATION_ID=tu_installation_id
export WEBHOOK_SECRET=tu_webhook_secret
export TARGET_USERNAME=tu_usuario

# 3. Verificar configuración
python check_env.py

# 4. Probar autenticación
python test_connection.py

# 5. Ejecutar aplicación
python run.py
```

## 🔧 Uso

### Endpoints Disponibles

- `GET /` - Información de la API
- `GET /health` - Health check
- `POST /webhook` - Endpoint para webhooks de GitHub
- `GET /docs` - Documentación interactiva

### Configuración del Webhook en GitHub

1. Ve a tu repositorio → Settings → Webhooks → Add webhook
2. **Payload URL**: `https://tu-dominio.com/webhook`
3. **Content type**: `application/json`
4. **Secret**: El mismo valor que `WEBHOOK_SECRET`
5. **Events**: Selecciona "Pull requests"

## ⚡ Funcionamiento

1. Se recibe un webhook cuando se abre/actualiza un PR
2. Se verifica la firma del webhook para seguridad
3. Se busca menciones del usuario objetivo en el cuerpo del PR
4. Si se encuentra una mención, se aprueba automáticamente el PR usando GitHub App

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest

# Ejecutar tests específicos
python -m pytest test_app.py -v

# Test con coverage
python -m pytest --cov=app
```

## 📁 Estructura del Proyecto

```
app/
├── __init__.py
├── config.py          # Configuración y variables de entorno
├── github_auth.py     # Autenticación GitHub App con JWT
├── github_service.py  # Servicios de GitHub API
├── main.py           # Aplicación FastAPI principal
├── routes.py         # Rutas y endpoints
└── utils.py          # Utilidades (verificación, menciones)

# Scripts útiles
├── run.py            # Ejecutar aplicación
├── check_env.py      # Verificar variables de entorno
├── test_connection.py # Probar autenticación
└── env_example.txt   # Ejemplo de variables de entorno
```

## 🔐 Autenticación GitHub App

La aplicación usa GitHub App con JWT para autenticación:

1. **Genera JWT** usando Client ID y Private Key
2. **Obtiene Installation Access Token** usando el JWT
3. **Hace peticiones a la API** usando el Access Token

## 🛠️ Troubleshooting

### Error: "Could not parse the provided public key"
- Verifica que `GITHUB_PRIVATE_KEY` tenga el formato correcto
- Asegúrate de incluir `-----BEGIN RSA PRIVATE KEY-----` y `-----END RSA PRIVATE KEY-----`
- Usa `\n` para los saltos de línea en la variable de entorno

### Error: "Installation access token"
- Verifica que `GITHUB_INSTALLATION_ID` sea correcto
- Asegúrate de que la GitHub App esté instalada en tu repositorio

### Webhook no funciona
- Verifica que `WEBHOOK_SECRET` coincida con el configurado en GitHub
- Revisa los logs del webhook en GitHub → Settings → Webhooks

## 📝 Licencia

MIT License