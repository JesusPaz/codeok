# CodeOK - GitHub Webhook API

A FastAPI application that automatically approves GitHub Pull Requests when specific users are mentioned.

## Features

- 🚀 **Automatic PR Approval**: Approves PRs when target users are mentioned
- 🔐 **GitHub App Authentication**: Secure authentication using GitHub App with JWT
- 🔒 **Webhook Verification**: Validates GitHub webhook signatures
- 📦 **Docker Ready**: Containerized application with GitHub Actions CI/CD
- ⚡ **FastAPI**: Modern, fast web framework
- ☸️ **Kubernetes Ready**: Complete Helm chart for production deployment

## Quick Start

### Using Docker

```bash
# Pull and run the latest image
docker run -p 8000:8000 \
  -e GITHUB_APP_ID=your_app_id \
  -e GITHUB_PRIVATE_KEY="$(cat your-private-key.pem)" \
  -e WEBHOOK_SECRET=your_webhook_secret \
  -e TARGET_USERNAME=codeok \
  jesuspaz/codeok:latest
```

### Using Helm Chart

Add the Helm repository:

```bash
helm repo add codeok https://jesuspaz.github.io/codeok
helm repo update
```

Install the chart:

```bash
# Development installation
helm install codeok codeok/codeok \
  --set secrets.github.appId="your_app_id" \
  --set secrets.github.privateKey="$(cat your-private-key.pem)" \
  --set secrets.webhook.secret="your_webhook_secret" \
  --set app.targetUsername="codeok"

# Production installation with External Secrets
helm install codeok codeok/codeok \
  --values values-production.yaml \
  --set externalSecrets.enabled=true \
  --set ingress.hosts[0].host=webhook.yourdomain.com
```

## Configuration

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_APP_ID` | GitHub App ID (number) | Yes |
| `GITHUB_PRIVATE_KEY` | GitHub App private key (PEM format) | Yes |
| `WEBHOOK_SECRET` | GitHub webhook secret | Yes |
| `TARGET_USERNAME` | Username to trigger PR approval | Yes |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `GITHUB_INSTALLATION_ID` | GitHub App installation ID | Auto-detected |

## GitHub App Setup

1. **Create a GitHub App**:
   - Go to GitHub Settings → Developer settings → GitHub Apps
   - Click "New GitHub App"
   - Fill in the required information
   - Set webhook URL to your deployment URL + `/webhook`

2. **Configure Permissions**:
   - Repository permissions:
     - Pull requests: Read & Write
     - Metadata: Read
   - Subscribe to events:
     - Pull requests

3. **Generate Private Key**:
   - In your GitHub App settings, generate a private key
   - Download the `.pem` file

4. **Install the App**:
   - Install the GitHub App on your target repositories

## Deployment Options

### 1. Local Development

```bash
# Clone the repository
git clone https://github.com/JesusPaz/codeok.git
cd codeok

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_APP_ID=your_app_id
export GITHUB_PRIVATE_KEY="$(cat your-private-key.pem)"
export WEBHOOK_SECRET=your_webhook_secret
export TARGET_USERNAME=codeok

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Docker Compose

```yaml
version: '3.8'
services:
  codeok:
    image: jesuspaz/codeok:latest
    ports:
      - "8000:8000"
    environment:
      - GITHUB_APP_ID=your_app_id
      - GITHUB_PRIVATE_KEY_PATH=/secrets/private-key.pem
      - WEBHOOK_SECRET=your_webhook_secret
      - TARGET_USERNAME=codeok
    volumes:
      - ./your-private-key.pem:/secrets/private-key.pem:ro
```

### 3. Kubernetes with Helm

See the [Helm Chart Documentation](helm/codeok-webhook/README.md) for detailed Kubernetes deployment instructions.

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health check endpoint
- `POST /webhook` - GitHub webhook endpoint

## Security Features

- 🔐 **GitHub App Authentication**: Uses JWT tokens for secure GitHub API access
- 🔒 **Webhook Signature Verification**: Validates all incoming webhooks
- 🛡️ **Non-root Container**: Runs as non-privileged user
- 🔒 **Read-only Filesystem**: Container filesystem is read-only
- 🚫 **No Privilege Escalation**: Security context prevents privilege escalation

## Monitoring

The application provides health check endpoints and can be monitored using:

- **Health Checks**: `/health` endpoint
- **Logs**: Structured logging with request/response details
- **Metrics**: Can be integrated with Prometheus (when enabled)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/JesusPaz/codeok)
- 🐛 [Issues](https://github.com/JesusPaz/codeok/issues)
- 💬 [Discussions](https://github.com/JesusPaz/codeok/discussions)