#!/bin/bash

# 检查系统状态脚本

echo "=========================================="
echo "  眼科注射预约系统 - 状态检查"
echo "=========================================="
echo

echo "=== 1. 后端服务状态 ==="
systemctl status bozhu-backend --no-pager 2>/dev/null || echo "服务不存在或未运行"

echo -e "\n=== 2. 端口检查 ==="
echo "端口 8031 状态:"
netstat -tuln 2>/dev/null | grep ":8031 " || echo "端口 8031 未监听"

echo -e "\n=== 3. 后端健康检查 ==="
echo "本地健康检查:"
curl -s -m 3 http://localhost:8031/api/health || echo "后端不可达"

echo -e "\n=== 4. Nginx 代理检查 ==="
echo "HTTPS 健康检查:"
curl -s -m 3 https://local-show.microcall.com.cn/health || echo "HTTPS 代理失败"

echo -e "\n=== 5. 日志检查 ==="
echo "后端日志（最后5行）:"
tail -5 /work/local-show/backend/logs/backend.log 2>/dev/null || echo "日志文件不存在"

echo -e "\n=== 6. Nginx 错误日志 ==="
echo "Nginx 错误日志（最后5行）:"
tail -5 /var/log/nginx/error.log 2>/dev/null || echo "Nginx 日志不存在"

echo -e "\n=== 7. 前端文件检查 ==="
echo "前端目录:"
ls -la /work/local-show/frontend/ 2>/dev/null | head -5 || echo "前端目录不存在"

echo -e "\n=== 8. 后端文件检查 ==="
echo "后端目录:"
ls -la /work/local-show/backend/ 2>/dev/null | head -5 || echo "后端目录不存在"

echo -e "\n=========================================="
echo "  检查完成"
echo "=========================================="
echo
echo "常见问题解决方案："
echo "1. 后端未启动: sudo bash /work/local-show/start-backend.sh"
echo "2. Nginx 配置错误: nginx -t"
echo "3. 端口冲突: netstat -tuln | grep 8031"
echo "4. 查看详细日志: tail -f /work/local-show/backend/logs/backend.log"
echo