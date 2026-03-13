#!/bin/bash

# 生产环境后台启动脚本
# 用法：./start_production.sh

echo "════════════════════════════════════════════════════════════"
echo "  眼科注射预约系统 - 生产环境后台启动"
echo "════════════════════════════════════════════════════════════"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 配置参数
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/backend.log"
PID_FILE="$SCRIPT_DIR/backend.pid"

echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "✗ 未找到 Python 3"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本：$PYTHON_VERSION"
echo ""

echo "[2/4] 检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "✗ 未找到 requirements.txt"
    exit 1
fi

# 检查是否需要安装依赖
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "✗ 依赖安装失败"
        exit 1
    fi
fi
echo "✓ 依赖检查完成"
echo ""

echo "[3/4] 创建日志目录..."
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"
echo "✓ 日志目录：$LOG_DIR"
echo ""

echo "[4/4] 启动后端服务..."

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "⚠ 服务已在运行 (PID: $OLD_PID)"
        echo "如需重启，请先运行：kill -9 $OLD_PID"
        exit 0
    else
        echo "清理旧的 PID 文件..."
        rm -f "$PID_FILE"
    fi
fi

# 后台启动服务
echo "启动命令：python3 run_server_production.py"
nohup python3 run_server_production.py > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!

# 保存 PID
echo $BACKEND_PID > "$PID_FILE"

echo "✓ 后端服务已启动 (PID: $BACKEND_PID)"
echo "✓ 监听地址：0.0.0.0:8031"
echo "✓ 日志文件：$LOG_FILE"
echo ""

# 等待服务启动
sleep 3

# 检查服务是否成功启动
if kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "✓ 服务启动成功"
    echo ""
    echo "【常用命令】"
    echo "  查看日志：tail -50 $LOG_FILE"
    echo "  查看实时日志：tail -f $LOG_FILE"
    echo "  停止服务：kill -9 $BACKEND_PID"
    echo "  检查状态：ps aux | grep run_server_production.py"
    echo ""
else
    echo "✗ 服务启动失败，请检查日志："
    tail -20 "$LOG_FILE"
    exit 1
fi

echo "════════════════════════════════════════════════════════════"
