# 药药记 Helm Chart

药药记（YaoYaoJi）智能用药安全管理系统的 Kubernetes Helm Chart。

## 前置要求

- Kubernetes 1.19+
- Helm 3.0+
- kubectl configured to access your cluster
- kind (for local development)

## 快速开始

### 1. 安装 kind 和相关工具

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

### 2. 创建 kind 集群

```bash
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
```

### 3. 安装 Nginx Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 4. 构建并加载 Docker 镜像

```bash
# Build backend image
docker build -t yaoyaoji-backend:latest ./yaoyaoji_backup

# Build frontend image
docker build -t yaoyaoji-frontend:latest ./yaoyaoji_frontend/web

# Load images into kind cluster
kind load docker-image yaoyaoji-backend:latest
kind load docker-image yaoyaoji-frontend:latest
```

### 5. 部署应用

#### 开发环境部署

```bash
helm install yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-dev.yaml

# Add to /etc/hosts
echo "127.0.0.1 yaoyaoji.local" | sudo tee -a /etc/hosts
```

#### 生产环境部署

```bash
helm install yaoyaoji ./helm/yaoyaoji \
  -f ./helm/yaoyaoji/values-prod.yaml \
  --set secrets.mysqlPassword=<your-password> \
  --set secrets.secretKey=<your-secret-key> \
  --set secrets.deepseekApiKey=<your-api-key>
```

## 配置参数

### 全局配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `global.environment` | 环境名称 | `production` |

### MySQL 配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `mysql.image` | MySQL 镜像 | `mysql:8.0` |
| `mysql.storage.size` | 存储大小 | `10Gi` |
| `mysql.storage.storageClass` | 存储类 | `standard` |
| `mysql.resources.requests.cpu` | CPU 请求 | `500m` |
| `mysql.resources.requests.memory` | 内存请求 | `1Gi` |
| `mysql.resources.limits.cpu` | CPU 限制 | `1000m` |
| `mysql.resources.limits.memory` | 内存限制 | `2Gi` |

### 后端配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `backend.replicaCount` | 副本数量 | `3` |
| `backend.image.repository` | 镜像仓库 | `yaoyaoji-backend` |
| `backend.image.tag` | 镜像标签 | `latest` |
| `backend.storage.size` | 上传文件存储大小 | `5Gi` |
| `backend.resources.requests.cpu` | CPU 请求 | `500m` |
| `backend.resources.requests.memory` | 内存请求 | `512Mi` |

### 前端配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `frontend.replicaCount` | 副本数量 | `2` |
| `frontend.image.repository` | 镜像仓库 | `yaoyaoji-frontend` |
| `frontend.image.tag` | 镜像标签 | `latest` |
| `frontend.resources.requests.cpu` | CPU 请求 | `200m` |
| `frontend.resources.requests.memory` | 内存请求 | `256Mi` |

### Ingress 配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `ingress.enabled` | 启用 Ingress | `true` |
| `ingress.className` | Ingress 类名 | `nginx` |
| `ingress.host` | 主机名 | `yaoyaoji.local` |
| `ingress.tls.enabled` | 启用 TLS | `false` |

### 应用配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `config.database` | 数据库名称 | `yaoyaoji` |
| `config.appName` | 应用名称 | `药药记 API` |
| `config.debug` | 调试模式 | `false` |

### 密钥配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `secrets.mysqlPassword` | MySQL 密码 | `yaoyaoji123` |
| `secrets.secretKey` | JWT 密钥 | `your-secret-key-change-in-production` |
| `secrets.deepseekApiKey` | DeepSeek API Key | `sk-your-api-key` |

## 访问应用

### 本地开发（kind）

```bash
# 访问前端
http://yaoyaoji.local

# 访问 API 文档
http://yaoyaoji.local/api/docs

# 检查健康状态
curl http://yaoyaoji.local/api/health
```

### 生产环境

根据 `ingress.host` 配置的域名访问。

## 升级和回滚

### 升级

```bash
# 升级到新版本
helm upgrade yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-dev.yaml

# 查看升级历史
helm history yaoyaoji
```

### 回滚

```bash
# 回滚到上一个版本
helm rollback yaoyaoji

# 回滚到指定版本
helm rollback yaoyaoji 2
```

## 卸载

```bash
helm uninstall yaoyaoji

# 删除 PVC（可选）
kubectl delete pvc -l "app.kubernetes.io/instance=yaoyaoji"
```

## 故障排查

### 查看 Pod 状态

```bash
kubectl get pods -l "app.kubernetes.io/instance=yaoyaoji"
```

### 查看日志

```bash
# 后端日志
kubectl logs -l app=backend --tail=100 -f

# 前端日志
kubectl logs -l app=frontend --tail=100 -f

# MySQL 日志
kubectl logs -l app=mysql --tail=100 -f

# 初始化 Job 日志
kubectl logs -l app=init-db
```

### 查看事件

```bash
kubectl get events --sort-by='.lastTimestamp'
```

### 进入容器调试

```bash
# 进入后端容器
kubectl exec -it <backend-pod-name> -- /bin/bash

# 进入 MySQL 容器
kubectl exec -it <mysql-pod-name> -- mysql -u root -p
```

### 常见问题

#### 1. Pod 一直处于 Pending 状态

检查存储类是否可用：
```bash
kubectl get storageclass
```

#### 2. 数据库连接失败

检查 MySQL Pod 是否就绪：
```bash
kubectl get pods -l app=mysql
kubectl logs -l app=mysql
```

#### 3. Ingress 无法访问

检查 Ingress Controller 是否运行：
```bash
kubectl get pods -n ingress-nginx
```

检查 Ingress 配置：
```bash
kubectl describe ingress yaoyaoji-ingress
```

## 开发指南

### 本地测试 Helm Chart

```bash
# Lint chart
helm lint ./helm/yaoyaoji

# Dry run
helm install yaoyaoji ./helm/yaoyaoji --dry-run --debug

# Template rendering
helm template yaoyaoji ./helm/yaoyaoji -f values-dev.yaml
```

### 更新镜像

```bash
# 重新构建镜像
docker build -t yaoyaoji-backend:v2 ./yaoyaoji_backup
docker build -t yaoyaoji-frontend:v2 ./yaoyaoji_frontend/web

# 加载到 kind
kind load docker-image yaoyaoji-backend:v2
kind load docker-image yaoyaoji-frontend:v2

# 升级部署
helm upgrade yaoyaoji ./helm/yaoyaoji \
  --set backend.image.tag=v2 \
  --set frontend.image.tag=v2
```

## 许可证

MIT License

## 支持

如有问题，请提交 Issue 或联系开发团队。
