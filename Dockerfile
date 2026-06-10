FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制前端build产物
COPY admin/dist/ ./admin_dist/

# 环境变量
ENV PORT=10000
ENV ADMIN_DIST=/app/admin_dist

EXPOSE 10000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
