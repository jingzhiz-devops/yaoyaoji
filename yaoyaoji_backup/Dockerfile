# ============================================
# 药药记后端 Dockerfile
# Multi-stage build for Python FastAPI
# ============================================

# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim AS production

WORKDIR /app

# 创建非 root 用户
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 从 builder 阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup init_db.py ./

# 创建上传目录
RUN mkdir -p uploads/medicine_images && \
    chown -R appuser:appgroup uploads

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动命令 - 使用 gunicorn + uvicorn workers 用于生产
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
