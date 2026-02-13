@echo off
chcp 65001 >nul
echo ========================================
echo   打包 Web 部署文件
echo ========================================
echo.

set OUTPUT_FILE=bozhu-web-deploy.zip

echo [1/2] 清理临时文件...
if exist "%OUTPUT_FILE%" del "%OUTPUT_FILE%"

echo.
echo [2/2] 打包文件...
echo 正在打包以下目录:
echo   - backend/
echo   - frontend/
echo   - web-deploy/
echo.

REM 使用 PowerShell 压缩文件
powershell -Command "& { ^
    $files = @( ^
        'backend', ^
        'frontend', ^
        'web-deploy' ^
    ); ^
    $exclude = @( ^
        '*/node_modules/*', ^
        '*/.venv/*', ^
        '*/dist/*', ^
        '*/__pycache__/*', ^
        '*/.git/*', ^
        '*/target/*', ^
        '*.pyc', ^
        '*.log' ^
    ); ^
    Compress-Archive -Path $files -DestinationPath '%OUTPUT_FILE%' -Force; ^
}"

if exist "%OUTPUT_FILE%" (
    echo.
    echo ========================================
    echo   打包完成！
    echo ========================================
    echo.
    echo 文件: %OUTPUT_FILE%
    echo 大小: 
    powershell -Command "(Get-Item '%OUTPUT_FILE%').Length / 1MB | ForEach-Object { '{0:N2} MB' -f $_ }"
    echo.
    echo 上传到服务器的方法:
    echo.
    echo 方法 1 - 使用 SCP:
    echo   scp %OUTPUT_FILE% your_username@your_server_ip:/tmp/
    echo.
    echo 方法 2 - 使用 WinSCP:
    echo   1. 打开 WinSCP 连接到服务器
    echo   2. 拖拽 %OUTPUT_FILE% 到 /tmp/ 目录
    echo.
    echo 在服务器上解压并部署:
    echo   cd /opt
    echo   sudo unzip /tmp/%OUTPUT_FILE% -d bozhu
    echo   cd bozhu
    echo   sudo bash web-deploy/deploy-production.sh
    echo.
) else (
    echo.
    echo ✗ 打包失败
    pause
    exit /b 1
)

pause
