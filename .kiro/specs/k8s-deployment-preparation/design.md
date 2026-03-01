# Design Document

## Overview

本设计文档描述了药药记项目从开发环境向 Kubernetes 生产环境迁移的技术实现方案。系统将通过 Helm Chart 部署到 kind Kubernetes 集群，支持开发和生产两种环境配置。

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Ingress Controller                    │
│              (yaoyaoji.local / localhost)               │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             │ /                          │ /api
             ▼                            ▼
    ┌────────────────┐          ┌────────────────┐
    │   Frontend     │          │    Backend     │
    │   Service      │          │    Service     │
    │  (ClusterIP)   │          │  (ClusterIP)   │
    └────────┬───────┘          └────────┬───────┘
             │                            │
             ▼                            ▼
    ┌────────────────┐          ┌────────────────┐
    │   Frontend     │          │    Backend     │
    │  Deployment    │          │  Deployment    │
    │  (2 replicas)  │          │  (3 replicas)  │
    └────────────────┘          └────────┬───────┘
                                         │
                                         │ mysql:3306
                                         ▼
                                ┌────────────────┐
                                │     MySQL      │
                                │    Service     │
                                │  (ClusterIP)   │
                                └────────┬───────┘
                                         │
                                         ▼
                                ┌────────────────┐
                                │     MySQL      │
                                │  StatefulSet   │
                                │  (1 replica)   │
                                └────────┬───────┘
                                         │
                                         ▼
                                ┌────────────────┐
                                │   MySQL PVC    │
                                │   (10Gi RWO)   │
                                └────────────────┘
```


## Component Design

### 1. Project Cleanup

#### Files to Delete
- `yaoyaoji_backup/quick_test_api.py` - Development API testing script
- `yaoyaoji_backup/verify_improvements.py` - Development verification script
- `yaoyaoji_backup/start.sh` - Development startup script
- `yaoyaoji_backup/migrate_add_alerts_adherence.py` - Individual migration script
- `yaoyaoji_backup/migrate_add_avatar.py` - Individual migration script
- `yaoyaoji_backup/migrate_add_birth_date.py` - Individual migration script
- `yaoyaoji_backup/migrate_add_medication_schedule_fields.py` - Individual migration script
- `yaoyaoji_backup/migrate_chronic_disease.py` - Individual migration script

#### Files to Update
- `.gitignore` - Add IDE configuration patterns

#### Files to Preserve
- `docker-compose.yml` - Keep for local development
- `yaoyaoji_backup/run_all_migrations.py` - Consolidated migration script

### 2. Helm Chart Structure

```
helm/yaoyaoji/
├── Chart.yaml                 # Chart metadata
├── values.yaml               # Default values
├── values-dev.yaml           # Development environment values
├── values-prod.yaml          # Production environment values
├── README.md                 # Installation and usage documentation
├── .helmignore              # Files to ignore in chart package
└── templates/
    ├── NOTES.txt            # Post-installation notes
    ├── _helpers.tpl         # Template helpers
    ├── configmap.yaml       # Application configuration
    ├── secret.yaml          # Sensitive credentials
    ├── mysql-statefulset.yaml    # MySQL database
    ├── mysql-service.yaml        # MySQL service
    ├── mysql-pvc.yaml           # MySQL persistent storage
    ├── backend-deployment.yaml   # Backend API
    ├── backend-service.yaml      # Backend service
    ├── backend-pvc.yaml         # Backend uploads storage
    ├── frontend-deployment.yaml  # Frontend web app
    ├── frontend-service.yaml     # Frontend service
    ├── ingress.yaml             # HTTP routing
    └── init-job.yaml            # Database initialization job
```


### 3. MySQL StatefulSet Design

#### Container Configuration
- Image: `mysql:8.0`
- Port: 3306
- Environment Variables:
  - `MYSQL_ROOT_PASSWORD`: From Secret
  - `MYSQL_DATABASE`: From ConfigMap
  - `MYSQL_CHARACTER_SET_SERVER`: utf8mb4
  - `MYSQL_COLLATION_SERVER`: utf8mb4_unicode_ci

#### Storage Configuration
- VolumeClaimTemplate: `mysql-data`
- Storage Size: 10Gi (configurable)
- Access Mode: ReadWriteOnce
- Storage Class: standard (kind default)

#### Health Checks
- Liveness Probe: `mysqladmin ping -h localhost -u root -p$MYSQL_ROOT_PASSWORD`
  - Initial Delay: 30s
  - Period: 10s
  - Timeout: 5s
- Readiness Probe: Same as liveness
  - Initial Delay: 10s

#### Resource Limits
- Development: requests(cpu: 250m, memory: 512Mi), limits(cpu: 500m, memory: 1Gi)
- Production: requests(cpu: 500m, memory: 1Gi), limits(cpu: 1000m, memory: 2Gi)

### 4. Backend Deployment Design

#### Container Configuration
- Image: Built from `yaoyaoji_backup/Dockerfile`
- Port: 8000
- Environment Variables (from ConfigMap):
  - `MYSQL_HOST`: mysql-service
  - `MYSQL_PORT`: 3306
  - `MYSQL_DATABASE`: yaoyaoji
  - `APP_NAME`: 药药记 API
  - `APP_VERSION`: 1.0.0
- Environment Variables (from Secret):
  - `MYSQL_PASSWORD`
  - `SECRET_KEY`
  - `DEEPSEEK_API_KEY`

#### Storage Configuration
- Volume: `backend-uploads`
- Mount Path: `/app/uploads`
- PVC: `backend-uploads-pvc`
- Storage Size: 5Gi (configurable)
- Access Mode: ReadWriteOnce (single replica) or ReadWriteMany (multiple replicas)

#### Health Checks
- Liveness Probe: HTTP GET `/health`
  - Initial Delay: 30s
  - Period: 10s
- Readiness Probe: HTTP GET `/health`
  - Initial Delay: 10s
  - Period: 5s

#### Replica Configuration
- Development: 1 replica
- Production: 3 replicas

#### Resource Limits
- Development: requests(cpu: 200m, memory: 256Mi), limits(cpu: 500m, memory: 512Mi)
- Production: requests(cpu: 500m, memory: 512Mi), limits(cpu: 1000m, memory: 1Gi)


### 5. Frontend Deployment Design

#### Container Configuration
- Image: Built from `yaoyaoji_frontend/web/Dockerfile`
- Port: 80
- Build Args:
  - `VITE_API_BASE_URL`: /api

#### Health Checks
- Liveness Probe: HTTP GET `/`
  - Initial Delay: 10s
  - Period: 10s
- Readiness Probe: HTTP GET `/`
  - Initial Delay: 5s
  - Period: 5s

#### Replica Configuration
- Development: 1 replica
- Production: 2 replicas

#### Resource Limits
- Development: requests(cpu: 100m, memory: 128Mi), limits(cpu: 200m, memory: 256Mi)
- Production: requests(cpu: 200m, memory: 256Mi), limits(cpu: 500m, memory: 512Mi)

### 6. Service Design

#### MySQL Service
- Type: ClusterIP
- Port: 3306
- Selector: `app: mysql`
- Headless: No

#### Backend Service
- Type: ClusterIP
- Port: 8000
- Selector: `app: backend`
- Target Port: 8000

#### Frontend Service
- Type: ClusterIP
- Port: 80
- Selector: `app: frontend`
- Target Port: 80

### 7. Ingress Design

#### Configuration
- Class: nginx (kind default)
- Host: `yaoyaoji.local` (configurable)
- TLS: Optional (disabled by default for kind)

#### Rules
- Path `/` → Frontend Service (port 80)
- Path `/api` → Backend Service (port 8000)
  - Path Type: Prefix
  - Strip Prefix: No (handled by backend)

#### Kind-Specific Configuration
- Use `extraPortMappings` in kind config to expose ports 80 and 443
- Add `yaoyaoji.local` to `/etc/hosts` pointing to 127.0.0.1


### 8. ConfigMap Design

#### Configuration Data
```yaml
data:
  MYSQL_HOST: "mysql-service"
  MYSQL_PORT: "3306"
  MYSQL_DATABASE: "yaoyaoji"
  MYSQL_USER: "root"
  APP_NAME: "药药记 API"
  APP_VERSION: "1.0.0"
  ALGORITHM: "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: "1440"
  DEEPSEEK_BASE_URL: "https://api.deepseek.com"
  DEBUG: "false"
```

### 9. Secret Design

#### Sensitive Data (Base64 Encoded)
```yaml
data:
  MYSQL_PASSWORD: <base64-encoded>
  SECRET_KEY: <base64-encoded>
  DEEPSEEK_API_KEY: <base64-encoded>
```

#### Default Values (for development)
- MYSQL_PASSWORD: yaoyaoji123
- SECRET_KEY: your-secret-key-change-in-production
- DEEPSEEK_API_KEY: sk-your-api-key

### 10. Database Initialization Job Design

#### Job Configuration
- Type: Job
- Restart Policy: OnFailure
- Backoff Limit: 3
- TTL After Finished: 100s

#### Helm Hooks
- `helm.sh/hook`: pre-install,pre-upgrade
- `helm.sh/hook-weight`: "-5"
- `helm.sh/hook-delete-policy`: before-hook-creation

#### Container Configuration
- Image: Same as backend
- Command: `["python", "run_all_migrations.py"]`
- Environment: Same as backend (ConfigMap + Secret)

#### Execution Flow
1. Helm triggers job before installing/upgrading
2. Job creates pod with backend image
3. Pod executes `run_all_migrations.py`
4. Script checks existing tables and adds missing ones
5. Job completes successfully or fails
6. If successful, Helm proceeds with deployment
7. If failed, Helm installation fails


### 11. Values Configuration Design

#### values.yaml (Default/Base Configuration)
```yaml
global:
  environment: production
  
mysql:
  image: mysql:8.0
  storage:
    size: 10Gi
    storageClass: standard
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi

backend:
  replicaCount: 3
  image:
    repository: yaoyaoji-backend
    tag: latest
  storage:
    size: 5Gi
    storageClass: standard
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

frontend:
  replicaCount: 2
  image:
    repository: yaoyaoji-frontend
    tag: latest
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

ingress:
  enabled: true
  className: nginx
  host: yaoyaoji.local
  tls:
    enabled: false

config:
  database: yaoyaoji
  appName: "药药记 API"
  appVersion: "1.0.0"
  debug: false

secrets:
  mysqlPassword: yaoyaoji123
  secretKey: your-secret-key-change-in-production
  deepseekApiKey: sk-your-api-key
```

#### values-dev.yaml (Development Overrides)
```yaml
global:
  environment: development

mysql:
  storage:
    size: 5Gi
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi

backend:
  replicaCount: 1
  storage:
    size: 2Gi
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

frontend:
  replicaCount: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

config:
  debug: true
```

#### values-prod.yaml (Production Overrides)
```yaml
global:
  environment: production

mysql:
  storage:
    size: 20Gi
  resources:
    requests:
      cpu: 1000m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 4Gi

backend:
  replicaCount: 3
  storage:
    size: 10Gi

ingress:
  host: yaoyaoji.example.com
  tls:
    enabled: true
    secretName: yaoyaoji-tls
```


## Deployment Workflow

### 1. Prerequisites Setup

```bash
# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 2. Create Kind Cluster

```bash
# Create cluster with ingress support
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

# Install nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 3. Build and Load Images

```bash
# Build backend image
docker build -t yaoyaoji-backend:latest ./yaoyaoji_backup

# Build frontend image
docker build -t yaoyaoji-frontend:latest ./yaoyaoji_frontend/web

# Load images into kind cluster
kind load docker-image yaoyaoji-backend:latest
kind load docker-image yaoyaoji-frontend:latest
```

### 4. Deploy with Helm

```bash
# Development deployment
helm install yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-dev.yaml

# Production deployment
helm install yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-prod.yaml

# Check deployment status
kubectl get pods
kubectl get services
kubectl get ingress

# View logs
kubectl logs -l app=backend
kubectl logs -l app=frontend
kubectl logs -l app=mysql
```

### 5. Access Application

```bash
# Add to /etc/hosts
echo "127.0.0.1 yaoyaoji.local" | sudo tee -a /etc/hosts

# Access application
curl http://yaoyaoji.local
curl http://yaoyaoji.local/api/health
```


## Implementation Considerations

### 1. Storage Class Compatibility

Kind cluster uses `standard` storage class by default with local-path provisioner. This supports:
- ReadWriteOnce (RWO): Single node read-write access
- ReadWriteMany (RWX): Not supported by default

For backend uploads with multiple replicas in production:
- Option A: Use ReadWriteOnce and configure pod affinity to same node
- Option B: Use external storage solution (NFS, Ceph) for RWX support
- Option C: Use object storage (MinIO, S3) instead of filesystem

Recommendation: Start with Option A for kind, document Option C for production.

### 2. Image Pull Policy

For kind cluster with locally loaded images:
- Set `imagePullPolicy: IfNotPresent` or `Never`
- Avoid `Always` which tries to pull from registry

### 3. Database Initialization Timing

The init job must:
- Wait for MySQL to be ready before running migrations
- Use `initContainers` with MySQL readiness check
- Set appropriate `backoffLimit` for retries

### 4. Secret Management

For production deployment:
- Do not commit actual secrets to values-prod.yaml
- Use `--set` flags during helm install
- Or use external secret management (Sealed Secrets, External Secrets Operator)
- Or use Kubernetes Secret created separately

Example:
```bash
helm install yaoyaoji ./helm/yaoyaoji \
  -f values-prod.yaml \
  --set secrets.mysqlPassword=$MYSQL_PASSWORD \
  --set secrets.secretKey=$SECRET_KEY \
  --set secrets.deepseekApiKey=$DEEPSEEK_API_KEY
```

### 5. Health Check Endpoints

Backend must implement `/health` endpoint that:
- Returns 200 OK when healthy
- Checks database connectivity
- Returns 503 Service Unavailable when unhealthy

### 6. Graceful Shutdown

Backend should handle SIGTERM signal:
- Complete in-flight requests
- Close database connections
- Shutdown within `terminationGracePeriodSeconds` (default 30s)

### 7. Rolling Update Strategy

Configure deployment strategy:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

This ensures zero-downtime deployments.


## Testing Strategy

### 1. Helm Chart Validation

```bash
# Lint chart
helm lint ./helm/yaoyaoji

# Dry run installation
helm install yaoyaoji ./helm/yaoyaoji --dry-run --debug

# Template rendering
helm template yaoyaoji ./helm/yaoyaoji -f values-dev.yaml
```

### 2. Deployment Testing

```bash
# Check pod status
kubectl get pods -w

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check logs
kubectl logs -l app=backend --tail=100
kubectl logs -l app=frontend --tail=100
kubectl logs -l app=mysql --tail=100

# Check services
kubectl get svc
kubectl describe svc backend-service

# Check ingress
kubectl get ingress
kubectl describe ingress yaoyaoji-ingress
```

### 3. Functional Testing

```bash
# Test frontend
curl -I http://yaoyaoji.local

# Test backend health
curl http://yaoyaoji.local/api/health

# Test backend API
curl http://yaoyaoji.local/api/docs

# Test database connectivity
kubectl exec -it mysql-0 -- mysql -u root -p$MYSQL_PASSWORD -e "SHOW DATABASES;"
```

### 4. Load Testing

```bash
# Install hey (HTTP load generator)
go install github.com/rakyll/hey@latest

# Test backend endpoint
hey -n 1000 -c 10 http://yaoyaoji.local/api/health

# Monitor resource usage
kubectl top pods
kubectl top nodes
```

### 5. Failure Testing

```bash
# Delete backend pod (test auto-recovery)
kubectl delete pod -l app=backend

# Scale down to 0 (test scaling)
kubectl scale deployment backend-deployment --replicas=0
kubectl scale deployment backend-deployment --replicas=3

# Simulate MySQL failure
kubectl delete pod mysql-0
# Verify data persistence after pod recreation
```

## Rollback Strategy

### Helm Rollback

```bash
# List releases
helm list

# View release history
helm history yaoyaoji

# Rollback to previous version
helm rollback yaoyaoji

# Rollback to specific revision
helm rollback yaoyaoji 2
```

### Manual Rollback

```bash
# Rollback deployment
kubectl rollout undo deployment/backend-deployment
kubectl rollout undo deployment/frontend-deployment

# Check rollout status
kubectl rollout status deployment/backend-deployment
```

## Monitoring and Observability

### Recommended Tools

1. Prometheus + Grafana for metrics
2. ELK Stack or Loki for logs
3. Jaeger for distributed tracing

### Basic Monitoring

```bash
# Watch pod status
kubectl get pods -w

# Stream logs
kubectl logs -f -l app=backend

# Check resource usage
kubectl top pods
kubectl describe node
```

