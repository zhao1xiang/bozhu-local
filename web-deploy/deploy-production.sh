#!/bin/bash

# 生产环境部署脚本
# 域名: local-show.microcall.com.cn
# 后端端口: 8031

set -e

echo "=========================================="
echo "  眼科注射预约系统 - 生产环境部署"
echo "  域名: local-show.microcall.com.cn"
echo "  后端端口: 8031"
echo "=========================================="
echo

# 配置变量
DOMAIN="local-show.microcall.com.cn"
BACKEND_PORT=8031
DEPLOY_DIR="/var/www/bozhu"
FRONTEND_DIR="$DEPLOY_DIR/frontend"
BACKEND_DIR="$DEPLOY_DIR/backend"
NGINX_CONF="/etc/nginx/sites-available/bozhu"
NGINX_ENABLED="/etc/nginx/sites-enabled/bozhu"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

echo "[1/7] 创建部署目录..."
mkdir -p $FRONTEND_DIR
mkdir -p $BACKEND_DIR
mkdir -p $BACKEND_DIR/logs
echo "✓ 目录创建完成"

echo
echo "[2/7] 构建前端..."
cd ../frontend
export VITE_API_URL="http://$DOMAIN"
npm install
npm run build
echo "✓ 前端构建完成"

echo
echo "[3/7] 部署前端文件..."
rm -rf $FRONTEND_DIR/*
cp -r dist/* $FRONTEND_DIR/
chown -R www-data:www-data $FRONTEND_DIR
echo "✓ 前端部署完成"

echo
echo "[4/7] 部署后端..."
cd ../backend

# 复制后端文件
cp main.py $BACKEND_DIR/
cp requirements.txt $BACKEND_DIR/
cp database.db $BACKEND_DIR/ 2>/dev/null || echo "数据库文件不存在，将在首次运行时创建"
cp -r routers $BACKEND_DIR/ 2>/dev/null || true
cp -r models $BACKEND_DIR/ 2>/dev/null || true
cp -r utils $BACKEND_DIR/ 2>/dev/null || true

# 创建虚拟环境并安装依赖
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "✓ 后端部署完成"

echo
echo "[5/7] 创建后端服务..."
cat > /etc/systemd/system/bozhu-backend.service << EOF
[Unit]
Description=眼科注射预约系统后端服务
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
Environment="PORT=$BACKEND_PORT"
ExecStart=$BACKEND_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT
Restart=always
RestartSec=10

# 日志配置
StandardOutput=append:$BACKEND_DIR/logs/backend.log
StandardError=append:$BACKEND_DIR/logs/backend_error.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable bozhu-backend
systemctl restart bozhu-backend
echo "✓ 后端服务创建完成"

echo
echo "[6/7] 配置 Nginx..."
cd - > /dev/null
cp nginx-production.conf $NGINX_CONF

# 创建软链接
ln -sf $NGINX_CONF $NGINX_ENABLED

# 测试 Nginx 配置
nginx -t

# 重启 Nginx
systemctl restart nginx
echo "✓ Nginx 配置完成"

echo
echo "[7/7] 验证部署..."
sleep 2

# 检查后端服务状态
if systemctl is-active --quiet bozhu-backend; then
    echo "✓ 后端服务运行正常"
else
    echo "✗ 后端服务启动失败"
    systemctl status bozhu-backend
    exit 1
fi

# 检查 Nginx 状态
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx 运行正常"
else
    echo "✗ Nginx 启动失败"
    systemctl status nginx
    exit 1
fi

# 检查端口监听
if netstat -tuln | grep -q ":$BACKEND_PORT "; then
    echo "✓ 后端端口 $BACKEND_PORT 监听正常"
else
    echo "✗ 后端端口 $BACKEND_PORT 未监听"
fi

if netstat -tuln | grep -q ":80 "; then
    echo "✓ Nginx 端口 80 监听正常"
else
    echo "✗ Nginx 端口 80 未监听"
fi

echo
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo
echo "访问地址: http://$DOMAIN"
echo "后端端口: $BACKEND_PORT"
echo
echo "管理命令:"
echo "  查看后端状态: sudo systemctl status bozhu-backend"
echo "  查看后端日志: sudo tail -f $BACKEND_DIR/logs/backend.log"
echo "  重启后端: sudo systemctl restart bozhu-backend"
echo "  重启 Nginx: sudo systemctl restart nginx"
echo
echo "默认管理员账号:"
echo "  用户名: admin"
echo "  密码: admin123"
echo
