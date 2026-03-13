#!/bin/bash
echo "眼科注射预约系统 v2.2.2 - 服务器版"
echo "正在启动..."

cd backend

# 检查 Python 版本
python3 --version

# 启动方式1：使用 uvicorn 直接启动（推荐）
echo "使用 uvicorn 启动服务..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8031

# 启动方式2：使用生产启动脚本
# echo "使用生产启动脚本..."
# python3 run_server_production.py