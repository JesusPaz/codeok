# CodeOK Helm Chart

A Helm chart for deploying the GitHub webhook API that automatically approves Pull Requests when specific users are mentioned.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- AWS Load Balancer Controller (for ALB ingress)
- External Secrets Operator (for production secrets management)

## Installation

### 1. Add the chart repository (if published)

```bash
helm repo add codeok https://your-charts-repo.com
helm repo update
```

### 2. Install the chart

#### Development Installation (with direct secrets)

```bash
# Copy and fill the secrets file
cp helm/codeok-webhook/secrets-example.yaml my-secrets.yaml
# Edit my-secrets.yaml with your actual values

# Install with direct secrets
helm install codeok ./helm/codeok-webhook \
  --values my-secrets.yaml \
  --set image.repository=your-dockerhub-username/codeok \
  --set image.tag=latest \
  --set ingress.hosts[0].host=webhook.your-domain.com
```

#### Production Installation (with External Secrets)

```bash
# Install with External Secrets
helm install codeok ./helm/codeok-webhook \
  --values ./helm/codeok-webhook/values-production.yaml \
  --set image.repository=your-dockerhub-username/codeok \
  --set image.tag=v1.0.0 \
  --set externalSecrets.enabled=true \
  --set ingress.hosts[0].host=webhook.yourdomain.com
```

## Configuration

### Required Secrets

The application requires the following secrets to function:

| Secret | Description | Required |
|--------|-------------|----------|
| `github-app-id` | GitHub App ID (number) | Yes |
| `github-private-key` | GitHub App private key (PEM format) | Yes |
| `webhook-secret` | GitHub webhook secret for signature verification | Yes |
| `github-installation-id` | GitHub App installation ID | No (auto-detected) |

### Secret Management Options

#### Option 1: Direct Secrets (Development)

```yaml
secrets:
  github:
    appId: "1530517"
    privateKey: |
      -----BEGIN RSA PRIVATE KEY-----
      YOUR_PRIVATE_KEY_CONTENT_HERE
      -----END RSA PRIVATE KEY-----
  webhook:
    secret: "your-webhook-secret"
```

#### Option 2: External Secrets (Production)

First, set up AWS Secrets Manager:

```bash
# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "prod/codeok/github-app-id" \
  --description "GitHub App ID for CodeOK webhook" \
  --secret-string '{"app-id":"1530517"}'

aws secretsmanager create-secret \
  --name "prod/codeok/github-private-key" \
  --description "GitHub App private key for CodeOK webhook" \
  --secret-string '{"private-key":"-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"}'

aws secretsmanager create-secret \
  --name "prod/codeok/webhook-secret" \
  --description "GitHub webhook secret for CodeOK webhook" \
  --secret-string '{"secret":"your-webhook-secret"}'
```

Then configure the chart:

```yaml
externalSecrets:
  enabled: true
  secretStore:
    name: "aws-secretsmanager-store"
    kind: "SecretStore"
  awsSecrets:
    region: "us-west-2"
    githubAppId:
      name: "prod/codeok/github-app-id"
      key: "app-id"
    githubPrivateKey:
      name: "prod/codeok/github-private-key"
      key: "private-key"
    webhookSecret:
      name: "prod/codeok/webhook-secret"
      key: "secret"
```

### AWS Load Balancer Configuration

The chart includes comprehensive ALB configuration:

```yaml
ingress:
  enabled: true
  className: "alb"
  annotations:
    # Basic ALB configuration
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/load-balancer-name: codeok-alb
    
    # SSL/TLS
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS-1-2-2017-01
    alb.ingress.kubernetes.io/certificate-arn: "arn:aws:acm:region:account:certificate/cert-id"
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    
    # Health checks
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: '30'
    
    # Security
    alb.ingress.kubernetes.io/security-groups: "sg-xxxxxxxxx"
    alb.ingress.kubernetes.io/subnets: "subnet-xxxxx,subnet-yyyyy"
```

## Security Features

### 1. Pod Security Context

- Runs as non-root user (UID 1000)
- Read-only root filesystem
- Drops all capabilities
- Prevents privilege escalation

### 2. Network Policies

- Restricts ingress traffic to ALB only
- Allows egress to DNS and GitHub API only
- Blocks all other network traffic

### 3. RBAC

- Minimal service account permissions
- No cluster-wide permissions
- Automatic service account token mounting disabled by default

### 4. Secret Management

- Secrets stored in Kubernetes secrets or AWS Secrets Manager
- Automatic secret rotation with External Secrets Operator
- Secrets mounted as environment variables (not files)

## Monitoring and Observability

### Health Checks

- Liveness probe: `/health` endpoint
- Readiness probe: `/health` endpoint
- Startup probe: Built-in with appropriate delays

### Metrics

The application exposes metrics at `/metrics` (if enabled):

```yaml
# Enable metrics collection
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

## Scaling

### Horizontal Pod Autoscaler

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### Pod Disruption Budget

```yaml
podDisruptionBudget:
  enabled: true
  minAvailable: 1
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `replicaCount` | int | `2` | Number of replicas |
| `image.repository` | string | `"your-dockerhub-username/codeok"` | Image repository |
| `image.pullPolicy` | string | `"IfNotPresent"` | Image pull policy |
| `image.tag` | string | `"latest"` | Image tag |
| `app.port` | int | `8000` | Application port |
| `app.targetUsername` | string | `"codeok"` | Target username for PR approval |
| `secrets.github.appId` | string | `""` | GitHub App ID |
| `secrets.github.privateKey` | string | `""` | GitHub App private key |
| `secrets.webhook.secret` | string | `""` | Webhook secret |
| `externalSecrets.enabled` | bool | `false` | Enable External Secrets |
| `ingress.enabled` | bool | `true` | Enable ingress |
| `ingress.className` | string | `"alb"` | Ingress class name |
| `resources.limits.cpu` | string | `"500m"` | CPU limit |
| `resources.limits.memory` | string | `"512Mi"` | Memory limit |
| `resources.requests.cpu` | string | `"100m"` | CPU request |
| `resources.requests.memory` | string | `"128Mi"` | Memory request |
| `autoscaling.enabled` | bool | `true` | Enable HPA |
| `autoscaling.minReplicas` | int | `2` | Minimum replicas |
| `autoscaling.maxReplicas` | int | `10` | Maximum replicas |
| `networkPolicy.enabled` | bool | `true` | Enable network policies |
| `podDisruptionBudget.enabled` | bool | `true` | Enable PDB |

## Troubleshooting

### Common Issues

1. **Secrets not found**
   ```bash
       # Check if secrets are created
    kubectl get secrets
    kubectl describe secret codeok-secrets
   ```

2. **ALB not created**
   ```bash
   # Check AWS Load Balancer Controller logs
   kubectl logs -n kube-system deployment/aws-load-balancer-controller
   ```

3. **External Secrets not working**
   ```bash
       # Check External Secrets Operator
    kubectl get externalsecrets
    kubectl describe externalsecret codeok-external-secrets
   ```

### Debug Commands

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=codeok

# Check pod logs
kubectl logs -l app.kubernetes.io/name=codeok

# Check service
kubectl get svc codeok

# Check ingress
kubectl get ingress codeok
kubectl describe ingress codeok

# Port forward for local testing
kubectl port-forward svc/codeok 8080:80
```

## Uninstallation

```bash
helm uninstall codeok
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `helm template` and `helm lint`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 