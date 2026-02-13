@echo off
chcp 65001 >nul
echo ========================================
echo 眼科注射预约系统 - Web 版本部署脚本
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo [步骤 1/5] 创建部署目录...
if not exist "backend" mkdir backend
if not exist "frontend" mkdir frontend

echo.
echo [步骤 2/5] 复制后端文件...
xcopy /E /I /Y ..\backend\*.py backend\
xcopy /E /I /Y ..\backend\models backend\models\
xcopy /E /I /Y ..\backend\routers backend\routers\
copy ..\backend\requirements.txt backend\
copy ..\backend\database.py backend\
copy ..\backend\main.py backend\

echo.
echo [步骤 3/5] 安装后端依赖...
cd backend
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo.
echo [步骤 4/5] 构建前端...
cd ..\frontend
call npm install
set VITE_API_URL=http://localhost:8000
call npm run build
cd ..\web-deploy

echo.
echo [步骤 5/5] 复制前端构建产物...
if exist "frontend\dist" rmdir /s /q frontend\dist
xcopy /E /I /Y ..\frontend\dist frontend\dist

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 启动方式：
echo 1. 后端：cd backend ^&^& .venv\Scripts\activate ^&^& python main.py
echo 2. 前端：使用 Web 服务器（如 Nginx）托管 frontend/dist 目录
echo    或使用 Python 简单服务器：cd frontend/dist ^&^& python -m http.server 8080
echo.
echo 访问地址：http://localhost:8080
echo API 地址：http://localhost:8000
echo.
pause
