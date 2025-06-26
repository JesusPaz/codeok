# Repository Analysis API

API para análisis de repositorios con ingesta, consultas y grafos usando FastAPI.

## Estructura del Proyecto

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── models.py            # Modelos Pydantic
│   ├── auth.py              # Autenticación GitHub App
│   ├── config.py            # Configuración de la aplicación
│   ├── queues.py            # Cola de trabajos en segundo plano
│   └── routers/
│       ├── __init__.py
│       ├── repos.py         # Endpoints de repositorios
│       ├── query.py         # Endpoint de consultas
│       └── webhooks.py      # Webhook de GitHub
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional para webhooks):
```bash
export GITHUB_APP_ID="your-app-id"
export GITHUB_PRIVATE_KEY="your-private-key"
export GITHUB_WEBHOOK_SECRET="your-webhook-secret"
```

3. Ejecutar la aplicación:
```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`

## Endpoints

### POST /repos
Registrar un repositorio (URL git + branch). Devuelve repo_id y estado inicial PENDING.

**Request:**
```json
{
  "url": "https://github.com/usuario/repo.git",
  "branch": "main"
}
```

**Response:**
```json
{
  "repo_id": "uuid-generado",
  "status": "PENDING"
}
```

### GET /repos/{repo_id}/status
Consultar el estado del proceso de ingesta (QUEUED / PROCESSING / READY / ERROR).

**Response:**
```json
{
  "status": "READY",
  "message": "Repository processed successfully"
}
```

### POST /query
Preguntar algo sobre el repo. Respuesta en stream (SSE).

**Request:**
```json
{
  "repo_id": "uuid-del-repo",
  "question": "¿Qué hace la función main?"
}
```

**Response:** Stream de texto con formato SSE

### GET /repos/{repo_id}/graph (Opcional)
Obtener un sub-grafo en JSON; acepta filtros depth y node_id.

**Query Parameters:**
- `depth`: Profundidad del grafo
- `node_id`: ID de nodo específico

### DELETE /repos/{repo_id}
Borrar repo, embeddings y grafo asociados.

### POST /github/webhook
Webhook para recibir eventos de GitHub App (pull requests, push, etc.).

**Headers requeridos:**
- `X-Hub-Signature-256`: Firma HMAC del payload
- `X-GitHub-Event`: Tipo de evento (pull_request, push, etc.)

**Eventos soportados:**
- `pull_request` (opened, synchronize): Procesa diffs de PRs
- `push`: Maneja eventos de push (opcional)

### GET /github/webhook/health
Health check del servicio de webhooks.

## Documentación Automática

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Estados de Repositorio

- `PENDING`: Recién registrado
- `QUEUED`: En cola para procesamiento
- `PROCESSING`: Siendo procesado
- `READY`: Listo para consultas
- `ERROR`: Error en el procesamiento

## Funcionalidades de GitHub App

### Autenticación
- Genera JWT tokens para autenticación de GitHub App
- Obtiene installation tokens para acceso a repositorios
- Verifica firmas HMAC de webhooks

### Procesamiento de PRs
- Recibe eventos de pull requests via webhook
- Encola trabajos para procesar diffs
- Procesa cambios en segundo plano

### Cola de Trabajos
- Sistema de cola en memoria para trabajos asíncronos
- Worker en segundo plano para procesar trabajos
- Logging de actividades

## Configuración de GitHub App

1. Crear una GitHub App en GitHub
2. Configurar webhook URL: `https://tu-dominio.com/github/webhook`
3. Seleccionar eventos: Pull requests, Push
4. Generar private key y obtener App ID
5. Instalar la app en repositorios deseados

## Notas de Implementación

- Usa almacenamiento en memoria (para producción usar base de datos)
- Simula procesamiento asíncrono de repositorios
- Implementa streaming para respuestas de consultas
- Sigue las mejores prácticas de FastAPI con APIRouter
- Incluye verificación de firmas HMAC para webhooks
- Sistema de cola simple para trabajos en segundo plano