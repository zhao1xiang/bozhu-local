@echo off
chcp 65001 >nul
echo ========================================
echo 眼科注射预约系统 - Web 演示环境
echo ========================================
echo.
echo 正在启动后端和前端服务...
echo.

:: 启动后端（在新窗口）
start "后端服务" cmd /k "cd backend && .venv\Scripts\activate && python main.py"

:: 等待后端启动
timeout /t 5 /nobreak >nul

:: 启动前端（在新窗口）
start "前端服务" cmd /k "cd frontend\dist && python -m http.server 8080"

:: 等待前端启动
timeout /t 3 /nobreak >nul

:: 打开浏览器
start http://localhost:8080

echo.
echo ========================================
echo 服务已启动！
echo ========================================
echo.
echo 前端地址：http://localhost:8080
echo 后端地址：http://localhost:8000
echo.
echo 按任意键关闭此窗口（服务将继续运行）...
pause >nul
