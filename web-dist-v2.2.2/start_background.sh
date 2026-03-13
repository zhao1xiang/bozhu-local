#!/bin/bash
# 眼科注射预约系统 v2.2.2 - 后台启动脚本

echo "眼科注射预约系统 v2.2.2 - 服务器版"
echo "正在后台启动..."

# 进入后端目录
cd backend

# 创建日志目录
mkdir -p logs

# 后台启动服务，输出到日志文件
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8031 > logs/server.log 2>&1 &

# 获取进程ID
PID=$!
echo $PID > server.pid

echo "服务已在后台启动"
echo "进程ID: $PID"
echo "日志文件: backend/logs/server.log"
echo "访问地址: http://localhost:8031"
echo ""
echo "停止服务请运行: ./stop_server.sh"