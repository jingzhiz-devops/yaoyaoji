#!/bin/bash
# ============================================
# EC2 + KinD 一键部署脚本
# 适用于 Amazon Linux 2 / Ubuntu EC2 实例
# ============================================
set -euo pipefail

DOMAIN="${1:?用法: $0 <域名> [邮箱]}"
EMAIL="${2:-admin@${DOMAIN}}"

echo "=== 药药记 EC2 + KinD 部署 ==="
echo "域名: ${DOMAIN}"
echo "邮箱: ${EMAIL}"
echo ""

# ---- 1. 安装 Docker ----
if ! command -v docker &> /dev/null; then
  echo ">>> 安装 Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
  sudo systemctl enable --now docker
  echo "Docker 安装完成，如果是首次安装请重新登录后再运行此脚本"
fi

# ---- 2. 安装 kubectl ----
if ! command -v kubectl &> /dev/null; then
  echo ">>> 安装 kubectl..."
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
  rm -f kubectl
fi

# ---- 3. 安装 KinD ----
if ! command -v kind &> /dev/null; then
  echo ">>> 安装 KinD..."
  curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
  sudo install -o root -g root -m 0755 kind /usr/local/bin/kind
  rm -f kind
fi

# ---- 4. 安装 Helm ----
if ! command -v helm &> /dev/null; then
  echo ">>> 安装 Helm..."
  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

# ---- 5. 创建 KinD 集群（映射 80/443 到宿主机）----
if ! kind get clusters 2>/dev/null | grep -q yaoyaoji; then
  echo ">>> 创建 KinD 集群..."
  cat <<EOF | kind create cluster --name yaoyaoji --config=-
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
else
  echo ">>> KinD 集群 yaoyaoji 已存在，跳过创建"
fi

kubectl cluster-info --context kind-yaoyaoji

# ---- 6. 安装 NGINX Ingress Controller（KinD 专用版）----
echo ">>> 安装 NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

echo ">>> 等待 Ingress Controller 就绪..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# ---- 7. 安装 cert-manager（自动 HTTPS 证书）----
echo ">>> 安装 cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

echo ">>> 等待 cert-manager 就绪..."
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=120s

# 创建 Let's Encrypt ClusterIssuer
echo ">>> 配置 Let's Encrypt..."
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ${EMAIL}
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# ---- 8. 部署药药记 ----
echo ">>> 部署药药记应用..."
echo ""
echo "请运行以下命令完成部署（替换真实密码）："
echo ""
echo "  helm install yaoyaoji ./helm/yaoyaoji \\"
echo "    -f ./helm/yaoyaoji/values-ec2.yaml \\"
echo "    --set ingress.host=${DOMAIN} \\"
echo "    --set secrets.mysqlPassword=<你的MySQL密码> \\"
echo "    --set secrets.secretKey=<你的JWT密钥> \\"
echo "    --set secrets.deepseekApiKey=<你的DeepSeek密钥>"
echo ""
echo "=== 基础设施就绪 ==="
echo ""
echo "确保你的域名 ${DOMAIN} 的 DNS A 记录指向此 EC2 的公网 IP"
echo "cert-manager 会自动通过 HTTP-01 验证获取 Let's Encrypt 证书"
