#!/bin/bash
echo "眼科注射预约系统 v2.2.2 - 服务器版"
echo "正在启动..."

cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8031 --reload