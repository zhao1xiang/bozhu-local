#!/bin/bash

# 启动后端服务脚本
# 在服务器上执行

set -e

echo "=========================================="
echo "  启动眼科注射预约系统后端服务"
echo "  端口: 8031"
echo "=========================================="
echo

BACKEND_DIR="/work/local-show/backend"
LOG_DIR="$BACKEND_DIR/logs"

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

echo "[1/4] 检查目录..."
if [ ! -d "$BACKEND_DIR" ]; then
    echo "✗ 后端目录不存在: $BACKEND_DIR"
    echo "请先解压部署包到 /work/local-show/"
    exit 1
fi

echo "✓ 后端目录存在"

echo
echo "[2/4] 检查 Python 依赖..."
cd "$BACKEND_DIR"

# 检查是否安装了依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "安装 Python 依赖..."
    pip3 install --upgrade pip
    pip3 install fastapi uvicorn sqlmodel sqlalchemy python-multipart python-jose passlib pydantic python-dateutil openpyxl
    echo "✓ 依赖安装完成"
else
    echo "✓ 依赖已安装"
fi

echo
echo "[3/4] 创建 systemd 服务..."
cat > /etc/systemd/system/bozhu-backend.service << EOF
[Unit]
Description=眼科注射预约系统后端服务
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$BACKEND_DIR
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8031
Restart=always
RestartSec=10

StandardOutput=append:$LOG_DIR/backend.log
StandardError=append:$LOG_DIR/backend_error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建日志目录
mkdir -p "$LOG_DIR"

# 重新加载 systemd
systemctl daemon-reload
systemctl enable bozhu-backend
systemctl restart bozhu-backend

echo "✓ 服务创建完成"

echo
echo "[4/4] 验证服务..."
sleep 2

# 检查服务状态
if systemctl is-active --quiet bozhu-backend; then
    echo "✓ 后端服务运行正常"
else
    echo "✗ 后端服务启动失败"
    systemctl status bozhu-backend --no-pager
    exit 1
fi

# 检查端口
if netstat -tuln 2>/dev/null | grep -q ":8031 "; then
    echo "✓ 端口 8031 监听正常"
else
    echo "✗ 端口 8031 未监听"
fi

# 测试健康检查
if curl -s http://localhost:8031/api/health > /dev/null; then
    echo "✓ 后端健康检查通过"
else
    echo "✗ 后端健康检查失败"
fi

echo
echo "=========================================="
echo "  后端服务启动完成！"
echo "=========================================="
echo
echo "服务信息："
echo "  服务名称: bozhu-backend"
echo "  运行端口: 8031"
echo "  日志目录: $LOG_DIR"
echo "  前端地址: https://local-show.microcall.com.cn"
echo
echo "管理命令："
echo "  查看状态: sudo systemctl status bozhu-backend"
echo "  查看日志: sudo tail -f $LOG_DIR/backend.log"
echo "  重启服务: sudo systemctl restart bozhu-backend"
echo "  停止服务: sudo systemctl stop bozhu-backend"
echo
echo "测试访问："
echo "  curl https://local-show.microcall.com.cn/health"
echo "  curl http://localhost:8031/api/health"
echo