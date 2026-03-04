@echo off
echo 测试后端启动...
cd simple-web-package
timeout /t 5 /nobreak >nul
taskkill /f /im backend_server.exe >nul 2>&1
start /min backend_server.exe
echo 后端已启动，5秒后自动关闭...
timeout /t 5 /nobreak >nul
taskkill /f /im backend_server.exe >nul 2>&1
echo 测试完成