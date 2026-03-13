#!/bin/bash
# 眼科注射预约系统 v2.2.2 - 重启服务脚本

echo "眼科注射预约系统 v2.2.2 - 重启服务"
echo "================================"

# 停止服务
echo "1. 停止当前服务..."
./stop_server.sh

# 等待一下确保进程完全停止
sleep 3

# 启动服务
echo ""
echo "2. 启动新服务..."
./start_background.sh

echo ""
echo "重启完成！"