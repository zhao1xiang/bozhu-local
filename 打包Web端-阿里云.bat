@echo off
chcp 65001 >nul
echo ========================================
echo   打包 Web 端部署包（阿里云专用）
echo   域名: local-show.microcall.com.cn
echo   后端端口: 8031
echo ========================================
echo.

set DOMAIN=local-show.microcall.com.cn
set BACKEND_PORT=8031
set OUTPUT_DIR=web-dist-aliyun

echo [1/4] 清理旧文件...
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
if exist "web-deploy-aliyun.zip" del "web-deploy-aliyun.zip"

echo.
echo [2/4] 构建前端...
cd frontend
REM 清理缓存
if exist "dist" rmdir /s /q "dist"
if exist ".vite" rmdir /s /q ".vite"
REM 设置环境变量 - Web 端跳过 Splash 检测
set VITE_API_URL=https://%DOMAIN%/api
set VITE_SKIP_SPLASH=true
set NODE_OPTIONS=--max-old-space-size=4096
call npm run build
if not exist "dist\index.html" (
    echo ✗ 前端构建失败
    cd ..
    pause
    exit /b 1
)
echo ✓ 前端构建完成
cd ..

echo.
echo [3/4] 准备部署文件...
mkdir "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%\frontend"
mkdir "%OUTPUT_DIR%\backend"

REM 复制前端构建产物
xcopy frontend\dist "%OUTPUT_DIR%\frontend" /E /I /Q

REM 复制后端文件（简化版，去掉 PyInstaller）
xcopy backend\*.py "%OUTPUT_DIR%\backend" /Q
xcopy backend\routers "%OUTPUT_DIR%\backend\routers" /E /I /Q
xcopy backend\models "%OUTPUT_DIR%\backend\models" /E /I /Q
xcopy backend\utils "%OUTPUT_DIR%\backend\utils" /E /I /Q 2>nul
copy backend\database.db "%OUTPUT_DIR%\backend\" 2>nul

REM 创建简化的 requirements.txt（Web 端专用）
(
echo fastapi
echo uvicorn[standard]
echo sqlmodel
echo sqlalchemy
echo python-multipart
echo python-jose[cryptography]
echo passlib[bcrypt]
echo pydantic
echo python-dateutil
echo openpyxl
) > "%OUTPUT_DIR%\backend\requirements.txt"

echo ✓ 文件准备完成

echo.
echo [4/4] 创建部署说明...
(
echo 眼科注射预约系统 - Web 端部署包（阿里云专用）
echo ==============================================
echo.
echo 域名: %DOMAIN%
echo 后端端口: %BACKEND_PORT%
echo 前端路径: /work/local-show/frontend/
echo.
echo 部署步骤：
echo ----------
echo.
echo 1. 上传文件到服务器
echo    scp web-deploy-aliyun.zip root@your_server_ip:/tmp/
echo.
echo 2. SSH 登录服务器
echo    ssh root@your_server_ip
echo.
echo 3. 解压文件
echo    cd /work
echo    unzip /tmp/web-deploy-aliyun.zip -d local-show
echo.
echo 4. 部署前端
echo    # 前端文件已经在前端构建时自动部署到 /work/local-show/frontend/
echo    # 确保 Nginx 配置正确指向该目录
echo.
echo 5. 部署后端
echo    cd /work/local-show/backend
echo    # 安装 Python 依赖
echo    pip3 install --upgrade pip
echo    pip3 install -r requirements.txt
echo.
echo 6. 创建后端服务
echo    cat > /etc/systemd/system/bozhu-backend.service << 'EOF'
echo    [Unit]
echo    Description=眼科注射预约系统后端服务
echo    After=network.target
echo    
echo    [Service]
echo    Type=simple
echo    User=root
echo    Group=root
echo    WorkingDirectory=/work/local-show/backend
echo    ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT%
echo    Restart=always
echo    RestartSec=10
echo    
echo    StandardOutput=append:/work/local-show/backend/logs/backend.log
echo    StandardError=append:/work/local-show/backend/logs/backend_error.log
echo    
echo    [Install]
echo    WantedBy=multi-user.target
echo    EOF
echo.
echo    # 启动服务
echo    mkdir -p /work/local-show/backend/logs
echo    systemctl daemon-reload
echo    systemctl enable bozhu-backend
echo    systemctl start bozhu-backend
echo.
echo 7. 验证部署
echo    # 检查后端状态
echo    systemctl status bozhu-backend
echo    
echo    # 测试健康检查
echo    curl https://%DOMAIN%/health
echo    curl http://localhost:%BACKEND_PORT%/api/health
echo.
echo 8. 访问系统
echo    浏览器打开: https://%DOMAIN%/
echo    默认账号: admin / admin123
echo.
echo 管理命令：
echo ----------
echo 查看后端状态: systemctl status bozhu-backend
echo 查看后端日志: tail -f /work/local-show/backend/logs/backend.log
echo 重启后端: systemctl restart bozhu-backend
echo 重启 Nginx: systemctl restart nginx
echo.
echo 特点：
echo -------
echo ✓ Web 端跳过 Splash 启动检测
echo ✓ 使用 HTTPS 访问
echo ✓ 后端端口: %BACKEND_PORT%
echo ✓ 前端路径: /work/local-show/frontend/
echo ✓ 不影响 EXE 桌面版
echo.
echo 技术支持：
echo ----------
echo 后端日志: /work/local-show/backend/logs/backend.log
echo Nginx 日志: /var/log/nginx/error.log
echo 服务状态: systemctl status bozhu-backend
) > "%OUTPUT_DIR%\部署说明.txt"

echo ✓ 部署说明已创建

echo.
echo [压缩] 打包成 zip 文件...
powershell -Command "Compress-Archive -Path '%OUTPUT_DIR%\*' -DestinationPath 'web-deploy-aliyun.zip' -Force"

if exist "web-deploy-aliyun.zip" (
    echo.
    echo ========================================
    echo   打包完成！
    echo ========================================
    echo.
    echo 文件: web-deploy-aliyun.zip
    for %%A in ("web-deploy-aliyun.zip") do echo 大小: %%~zA 字节
    echo.
    echo 包含内容:
    echo   - frontend/  ^(前端构建产物，已配置跳过 Splash^)
    echo   - backend/   ^(后端源码，简化版^)
    echo   - 部署说明.txt
    echo.
    echo 上传到服务器后解压到 /work/local-show/ 目录
    echo.
    echo 注意：此包专为阿里云部署，不影响 EXE 桌面版
    echo.
) else (
    echo.
    echo ✗ 打包失败
    pause
    exit /b 1
)

pause