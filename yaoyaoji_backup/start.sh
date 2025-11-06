#!/bin/bash

# 药药记后端启动脚本

echo "🚀 启动药药记后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 检查并安装依赖..."
pip install -r requirements.txt

# 启动服务
echo "🌟 启动 FastAPI 服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
