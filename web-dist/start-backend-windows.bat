@echo off
chcp 65001 >nul
echo ========================================
echo   眼科注射预约系统 - 后端启动脚本
echo   适用于 Windows 测试环境
echo   端口: 8031
echo ========================================
echo.

set BACKEND_PORT=8031
set BACKEND_DIR=backend

echo [1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未找到 Python，请先安装 Python3
    pause
    exit /b 1
)
echo ✓ Python 已安装

echo.
echo [2/4] 检查后端目录...
if not exist "%BACKEND_DIR%" (
    echo ✗ 后端目录不存在: %BACKEND_DIR%
    pause
    exit /b 1
)

cd "%BACKEND_DIR%"

echo.
echo [3/4] 检查 Python 依赖...
if exist "requirements.txt" (
    echo 安装依赖包...
    pip install -r requirements.txt
) else (
    echo 警告: 未找到 requirements.txt
)

echo.
echo [4/4] 启动后端服务...
echo 监听地址: 127.0.0.1:%BACKEND_PORT%
echo API 地址: http://127.0.0.1:%BACKEND_PORT%/api
echo 日志文件: %BACKEND_DIR%\logs\backend.log
echo.

REM 创建日志目录
if not exist "logs" mkdir logs

REM 检查端口占用
netstat -ano | findstr ":%BACKEND_PORT%" >nul
if not errorlevel 1 (
    echo 警告: 端口 %BACKEND_PORT% 已被占用
    echo 尝试停止现有服务...
    taskkill /f /im python.exe 2>nul
    timeout /t 2 /nobreak >nul
)

REM 启动服务
start "眼科注射预约系统后端" python run_server.py --port %BACKEND_PORT%

echo ✓ 后端服务已启动
echo.
echo 管理命令:
echo   查看进程: tasklist | findstr python
echo   停止服务: taskkill /f /im python.exe
echo   查看日志: type %BACKEND_DIR%\logs\backend.log
echo.
echo 验证服务:
echo   curl http://127.0.0.1:%BACKEND_PORT%/api/health
echo   curl http://127.0.0.1:%BACKEND_PORT%/api/auth/token ^
echo     -H "Content-Type: application/x-www-form-urlencoded" ^
echo     -d "username=admin&password=admin123"
echo.
echo 注意: 此脚本用于测试，生产环境请使用 Linux 脚本
echo.

pause