#!/bin/bash

# Mac版本启动脚本
# 适用于所有Mac系统（Intel和Apple Silicon）

echo "======================================"
echo "  玻注预约系统 - Mac版 v2.1.8"
echo "======================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3"
    echo "请先安装Python3: https://www.python.org/downloads/macos/"
    exit 1
fi

echo "Python版本: $(python3 --version)"
echo ""

# 检查并安装依赖
if [ ! -d "backend/venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    echo "正在安装依赖包（需要几分钟）..."
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    echo "依赖安装完成！"
    echo ""
else
    cd backend
    source venv/bin/activate
    cd ..
fi

# 检查前端文件
if [ ! -d "frontend/dist" ]; then
    echo "错误：前端文件不存在"
    echo "请确保frontend/dist目录存在"
    exit 1
fi

# 启动服务
echo "正在启动服务..."
echo "服务地址: http://localhost:8000"
echo "默认账号: admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务"
echo "======================================"
echo ""

cd backend
python3 simple_web_server.py

# 退出时清理
deactivate 2>/dev/null
