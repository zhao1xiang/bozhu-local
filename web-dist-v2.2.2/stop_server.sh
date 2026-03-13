#!/bin/bash
# 眼科注射预约系统 v2.2.2 - 停止服务脚本

echo "正在停止眼科注射预约系统..."

# 检查 PID 文件是否存在
if [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    
    # 检查进程是否还在运行
    if ps -p $PID > /dev/null 2>&1; then
        echo "正在停止进程 $PID..."
        kill $PID
        
        # 等待进程结束
        sleep 2
        
        # 如果进程还在运行，强制杀死
        if ps -p $PID > /dev/null 2>&1; then
            echo "强制停止进程 $PID..."
            kill -9 $PID
        fi
        
        echo "服务已停止"
    else
        echo "进程 $PID 不存在或已停止"
    fi
    
    # 删除 PID 文件
    rm -f server.pid
else
    echo "未找到 server.pid 文件"
    echo "尝试查找并停止所有相关进程..."
    
    # 查找并停止所有 uvicorn 进程
    pkill -f "uvicorn main:app"
    
    if [ $? -eq 0 ]; then
        echo "已停止所有相关进程"
    else
        echo "未找到运行中的服务进程"
    fi
fi