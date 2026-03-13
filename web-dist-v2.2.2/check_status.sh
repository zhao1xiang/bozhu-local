#!/bin/bash
# 眼科注射预约系统 v2.2.2 - 服务状态检查脚本

echo "眼科注射预约系统 v2.2.2 - 服务状态"
echo "================================"

# 检查 PID 文件
if [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    echo "PID 文件存在: $PID"
    
    # 检查进程是否运行
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 服务正在运行 (PID: $PID)"
        
        # 显示进程信息
        echo ""
        echo "进程信息:"
        ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem
        
        # 检查端口占用
        echo ""
        echo "端口占用情况:"
        netstat -tlnp 2>/dev/null | grep :8031 || ss -tlnp | grep :8031
        
        # 显示最近的日志
        if [ -f "backend/logs/server.log" ]; then
            echo ""
            echo "最近日志 (最后10行):"
            tail -10 backend/logs/server.log
        fi
        
    else
        echo "❌ 进程不存在或已停止"
        echo "PID 文件存在但进程未运行，建议删除 server.pid 文件"
    fi
else
    echo "❌ 未找到 PID 文件"
    
    # 检查是否有相关进程在运行
    UVICORN_PIDS=$(pgrep -f "uvicorn main:app")
    if [ ! -z "$UVICORN_PIDS" ]; then
        echo ""
        echo "⚠️  发现相关进程在运行:"
        ps -p $UVICORN_PIDS -o pid,ppid,cmd,etime,pcpu,pmem
        echo ""
        echo "这些进程可能是手动启动的，如需停止请运行: ./stop_server.sh"
    else
        echo "未发现相关进程运行"
    fi
fi

echo ""
echo "================================"
echo "可用命令:"
echo "  ./start_background.sh  - 后台启动服务"
echo "  ./start_production.sh  - 前台启动服务"
echo "  ./stop_server.sh       - 停止服务"
echo "  ./restart_server.sh    - 重启服务"
echo "  ./check_status.sh      - 检查状态"