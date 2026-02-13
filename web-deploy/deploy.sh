#!/bin/bash

echo "========================================"
echo "眼科注射预约系统 - Web 版本部署脚本"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.11+"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "[步骤 1/5] 创建部署目录..."
mkdir -p backend
mkdir -p frontend

echo ""
echo "[步骤 2/5] 复制后端文件..."
cp -r ../backend/*.py backend/
cp -r ../backend/models backend/
cp -r ../backend/routers backend/
cp ../backend/requirements.txt backend/
cp ../backend/database.py backend/
cp ../backend/main.py backend/

echo ""
echo "[步骤 3/5] 安装后端依赖..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
cd ..

echo ""
echo "[步骤 4/5] 构建前端..."
cd ../frontend
npm install
export VITE_API_URL=http://localhost:8000
npm run build
cd ../web-deploy

echo ""
echo "[步骤 5/5] 复制前端构建产物..."
rm -rf frontend/dist
cp -r ../frontend/dist frontend/

echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "启动方式："
echo "1. 后端：cd backend && source .venv/bin/activate && python main.py"
echo "2. 前端：使用 Web 服务器（如 Nginx）托管 frontend/dist 目录"
echo "   或使用 Python 简单服务器：cd frontend/dist && python3 -m http.server 8080"
echo ""
echo "访问地址：http://localhost:8080"
echo "API 地址：http://localhost:8000"
echo ""
