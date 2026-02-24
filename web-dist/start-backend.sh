#!/bin/bash
# 眼科注射预约系统 - 后端快速启动脚本
# 端口: 8031
# 适用于阿里云 Linux 服务器

set -e

# 配置
BACKEND_PORT="8031"
BACKEND_DIR="/work/local-show/backend"
PYTHON_CMD="python3"

echo "=========================================="
echo "   启动眼科注射预约系统后端"
echo "   端口: $BACKEND_PORT"
echo "=========================================="

# 检查 Python
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "错误: 未找到 $PYTHON_CMD，请先安装 Python3"
    exit 1
fi

# 检查后端目录
if [[ ! -d "$BACKEND_DIR" ]]; then
    echo "错误: 后端目录不存在: $BACKEND_DIR"
    echo "请确保已正确部署到: /work/local-show/"
    exit 1
fi

cd "$BACKEND_DIR"

# 检查依赖
echo "[1/4] 检查 Python 依赖..."
if [[ -f "requirements.txt" ]]; then
    echo "安装依赖包..."
    pip3 install -r requirements.txt
else
    echo "警告: 未找到 requirements.txt"
fi

# 创建日志目录
echo "[2/4] 设置日志..."
mkdir -p logs
chmod 755 logs

# 检查端口占用
echo "[3/4] 检查端口 $BACKEND_PORT..."
if netstat -tuln | grep ":$BACKEND_PORT " &> /dev/null; then
    echo "警告: 端口 $BACKEND_PORT 已被占用"
    echo "尝试停止现有服务..."
    pkill -f "run_server.py" || true
    sleep 2
fi

# 启动服务
echo "[4/4] 启动后端服务..."
echo "监听地址: 127.0.0.1:$BACKEND_PORT"
echo "API 地址: http://127.0.0.1:$BACKEND_PORT/api"
echo "日志文件: $BACKEND_DIR/logs/backend.log"

# 后台运行
nohup $PYTHON_CMD run_server.py --port $BACKEND_PORT > logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "✓ 后端服务已启动 (PID: $BACKEND_PID)"
echo ""
echo "管理命令:"
echo "  查看状态: ps aux | grep run_server.py"
echo "  查看日志: tail -f $BACKEND_DIR/logs/backend.log"
echo "  停止服务: kill $BACKEND_PID"
echo ""
echo "验证服务:"
echo "  curl http://127.0.0.1:$BACKEND_PORT/api/health"
echo ""
echo "Nginx 配置:"
echo "  确保 Nginx 代理到: http://127.0.0.1:$BACKEND_PORT"
echo "  当前域名: local-show.microcall.com.cn"