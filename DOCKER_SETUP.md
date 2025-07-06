# Docker Deployment Setup

Este proyecto incluye una GitHub Action que automáticamente construye y sube una imagen Docker a DockerHub cuando se hace merge a la rama `main`.

## Configuración de Secretos en GitHub

Para que la GitHub Action funcione, necesitas configurar los siguientes secretos en tu repositorio:

### 1. Ir a la configuración de secretos

1. Ve a tu repositorio en GitHub
2. Click en **Settings** (Configuración)
3. En el menú lateral, click en **Secrets and variables** → **Actions**
4. Click en **New repository secret**

### 2. Agregar los secretos necesarios

#### DOCKERHUB_USERNAME
- **Nombre**: `DOCKERHUB_USERNAME`
- **Valor**: Tu nombre de usuario de DockerHub

#### DOCKERHUB_TOKEN
- **Nombre**: `DOCKERHUB_TOKEN`
- **Valor**: Un token de acceso de DockerHub

Para crear un token de DockerHub:
1. Ve a [DockerHub](https://hub.docker.com)
2. Inicia sesión en tu cuenta
3. Click en tu avatar → **Account Settings**
4. Click en **Security** → **New Access Token**
5. Dale un nombre descriptivo (ej: "GitHub Actions")
6. Selecciona los permisos necesarios (Read, Write, Delete)
7. Click en **Generate** y copia el token

## Configuración de la imagen

La GitHub Action está configurada para:

- **Nombre de imagen**: `codeok-webhook-api` (puedes cambiarlo en `.github/workflows/docker-build.yml`)
- **Tags generados**:
  - `latest` (para la rama main)
  - `main-<sha>` (commit específico)
  - Tags para PRs

## Funcionamiento

### Cuándo se ejecuta
- **Push a main**: Construye y sube la imagen a DockerHub
- **Pull Request**: Solo construye la imagen (no la sube)

### Plataformas soportadas
- `linux/amd64` (Intel/AMD)
- `linux/arm64` (Apple Silicon, ARM servers)

## Uso de la imagen

Una vez que la imagen esté en DockerHub, puedes usarla así:

```bash
# Ejecutar la imagen
docker run -d \
  -p 8000:8000 \
  -e GITHUB_APP_ID=your_app_id \
  -e GITHUB_PRIVATE_KEY_PATH=/path/to/key.pem \
  -e WEBHOOK_SECRET=your_secret \
  -e TARGET_USERNAME=codeok \
  --name codeok-webhook \
  tu_usuario_dockerhub/codeok-webhook-api:latest
```

### Con docker-compose

```yaml
version: '3.8'
services:
  webhook-api:
    image: tu_usuario_dockerhub/codeok-webhook-api:latest
    ports:
      - "8000:8000"
    environment:
      - GITHUB_APP_ID=your_app_id
      - GITHUB_PRIVATE_KEY_PATH=/app/private-key.pem
      - WEBHOOK_SECRET=your_secret
      - TARGET_USERNAME=codeok
    volumes:
      - ./private-key.pem:/app/private-key.pem:ro
    restart: unless-stopped
```

## Health Check

La imagen incluye un health check en `/health` que se ejecuta cada 30 segundos.

## Logs

Para ver los logs del contenedor:

```bash
docker logs codeok-webhook
```

## Troubleshooting

### Error de autenticación
- Verifica que `GITHUB_APP_ID` sea correcto
- Asegúrate de que la clave privada esté accesible
- Verifica que la GitHub App tenga los permisos necesarios

### Error de webhook
- Verifica que `WEBHOOK_SECRET` coincida con el configurado en GitHub
- Revisa los logs para ver detalles del error

### Problemas de red
- Asegúrate de que el puerto 8000 esté disponible
- Verifica que no haya conflictos con otros servicios 