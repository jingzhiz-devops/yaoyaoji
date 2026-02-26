# Kubernetes 部署指南

本文档提供药药记项目在 Kubernetes 集群上的完整部署指南。

## 目录

- [架构概览](#架构概览)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [故障排查](#故障排查)

## 架构概览

```
┌─────────────────────────────────────────────┐
│          Ingress (yaoyaoji.local)           │
└────────────┬────────────────────────────────┘
             │
             ├─ / → Frontend Service (Nginx)
             ├─ /api → Backend Service (FastAPI)
             └─ /uploads → Backend Service
                    │
                    ├─ Backend Deployment (3 replicas)
                    │  └─ PVC (uploads)
                    │
                    └─ MySQL StatefulSet (1 replica)
                       └─ PVC (data)
```

## 快速开始

### 前置要求

- Docker
- kind
- kubectl
- Helm 3

### 一键部署（开发环境）

```bash
# 1. 创建 kind 集群
./scripts/create-kind-cluster.sh

# 2. 构建并加载镜像
./scripts/build-and-load-images.sh

# 3. 部署应用
helm install yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-dev.yaml

# 4. 添加 hosts 记录
echo "127.0.0.1 yaoyaoji.local" | sudo tee -a /etc/hosts

# 5. 访问应用
open http://yaoyaoji.local
```

## 详细步骤

### 1. 安装工具

#### 安装 kind

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

#### 安装 kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

#### 安装 Helm

```bash
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

### 3. 安装 Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 4. 构建 Docker 镜像

```bash
# 后端镜像
docker build -t yaoyaoji-backend:latest ./yaoyaoji_backup

# 前端镜像
docker build -t yaoyaoji-frontend:latest ./yaoyaoji_frontend/web
```

### 5. 加载镜像到 kind

```bash
kind load docker-image yaoyaoji-backend:latest
kind load docker-image yaoyaoji-frontend:latest
```

### 6. 部署应用

#### 开发环境

```bash
helm install yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-dev.yaml
```

#### 生产环境

```bash
helm install yaoyaoji ./helm/yaoyaoji \
  -f ./helm/yaoyaoji/values-prod.yaml \
  --set secrets.mysqlPassword=<your-password> \
  --set secrets.secretKey=<your-secret-key> \
  --set secrets.deepseekApiKey=<your-api-key>
```

### 7. 验证部署

```bash
# 查看 Pod 状态
kubectl get pods

# 查看服务
kubectl get services

# 查看 Ingress
kubectl get ingress

# 检查健康状态
curl http://yaoyaoji.local/api/health
```

## 配置说明

### 环境变量

通过 ConfigMap 和 Secret 管理：

- **ConfigMap**: 非敏感配置（数据库名、应用名等）
- **Secret**: 敏感信息（密码、API Key 等）

### 存储配置

- **MySQL**: 使用 StatefulSet 的 volumeClaimTemplate，10Gi 存储
- **Backend Uploads**: 使用 PVC，5Gi 存储

### 资源限制

#### 开发环境

- MySQL: 250m CPU, 512Mi Memory
- Backend: 200m CPU, 256Mi Memory
- Frontend: 100m CPU, 128Mi Memory

#### 生产环境

- MySQL: 1000m CPU, 2Gi Memory
- Backend: 500m CPU, 512Mi Memory
- Frontend: 200m CPU, 256Mi Memory

## 故障排查

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

### 常见问题

#### 1. Pod 无法启动

```bash
# 查看 Pod 详情
kubectl describe pod <pod-name>

# 查看事件
kubectl get events --sort-by='.lastTimestamp'
```

#### 2. 数据库连接失败

```bash
# 检查 MySQL Pod
kubectl get pods -l app=mysql

# 进入 MySQL 容器测试
kubectl exec -it <mysql-pod> -- mysql -u root -p
```

#### 3. Ingress 无法访问

```bash
# 检查 Ingress Controller
kubectl get pods -n ingress-nginx

# 检查 Ingress 配置
kubectl describe ingress yaoyaoji-ingress

# 确认 /etc/hosts 配置
cat /etc/hosts | grep yaoyaoji
```

## 升级和回滚

### 升级

```bash
# 升级应用
helm upgrade yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-dev.yaml

# 查看历史
helm history yaoyaoji
```

### 回滚

```bash
# 回滚到上一版本
helm rollback yaoyaoji

# 回滚到指定版本
helm rollback yaoyaoji 2
```

## 卸载

```bash
# 卸载应用
helm uninstall yaoyaoji

# 删除 PVC（可选）
kubectl delete pvc -l "app.kubernetes.io/instance=yaoyaoji"

# 删除 kind 集群
kind delete cluster
```

## 生产环境建议

1. **使用外部数据库**: 考虑使用云数据库服务（如 AWS RDS、Azure Database）
2. **配置持久化存储**: 使用云存储（如 AWS EBS、Azure Disk）
3. **启用 TLS**: 配置 HTTPS 证书
4. **配置监控**: 集成 Prometheus + Grafana
5. **配置日志**: 集成 ELK Stack 或 Loki
6. **配置备份**: 定期备份数据库和上传文件
7. **配置自动扩缩容**: 使用 HPA（Horizontal Pod Autoscaler）

## 更多信息

详细配置说明请参考：[Helm Chart README](./helm/yaoyaoji/README.md)
