@echo off
chcp 65001 >nul
echo 启动前端服务（简单 HTTP 服务器）...
echo 访问地址：http://localhost:8080
cd frontend\dist
python -m http.server 8080
pause
