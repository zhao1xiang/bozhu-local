# 多阶段构建 - 眼科注射预约系统 Web 版

# 阶段 1: 构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY ../frontend/package*.json ./
RUN npm install
COPY ../frontend/ ./
ENV VITE_API_URL=/api
RUN npm run build

# 阶段 2: 后端 + Nginx
FROM python:3.11-slim
WORKDIR /app

# 安装 Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# 复制后端代码
COPY ../backend/ ./backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx-docker.conf /etc/nginx/sites-available/default

# 暴露端口
EXPOSE 80 8000

# 启动脚本
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
