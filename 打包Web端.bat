@echo off
chcp 65001 >nul
echo ========================================
echo   打包 Web 端部署包
echo   域名: local-show.microcall.com.cn
echo ========================================
echo.

set DOMAIN=local-show.microcall.com.cn
set OUTPUT_DIR=web-dist

echo [1/4] 清理旧文件...
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
if exist "web-deploy.zip" del "web-deploy.zip"

echo.
echo [2/4] 构建前端...
cd frontend
REM 清理缓存
if exist "dist" rmdir /s /q "dist"
if exist ".vite" rmdir /s /q ".vite"
REM 设置环境变量
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

REM 复制后端文件（排除不必要的）
xcopy backend\*.py "%OUTPUT_DIR%\backend" /Q
xcopy backend\routers "%OUTPUT_DIR%\backend\routers" /E /I /Q
xcopy backend\models "%OUTPUT_DIR%\backend\models" /E /I /Q
xcopy backend\utils "%OUTPUT_DIR%\backend\utils" /E /I /Q 2>nul
copy backend\database.db "%OUTPUT_DIR%\backend\" 2>nul
copy backend\requirements.txt "%OUTPUT_DIR%\backend\"

REM 创建简化的 requirements.txt（去掉 PyInstaller）
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
echo 眼科注射预约系统 - Web 端部署包
echo =====================================
echo.
echo 域名: %DOMAIN%
echo 后端端口: 8000 ^(可自定义^)
echo.
echo 部署步骤：
echo ----------
echo.
echo 1. 上传整个 web-dist 目录到服务器
echo.
echo 2. 部署前端 ^(Nginx^)
echo    - 将 frontend 目录内容复制到 Nginx 网站根目录
echo    - 配置 Nginx 反向代理 /api/ 到后端
echo.
echo 3. 部署后端 ^(Python^)
echo    cd backend
echo    python3 -m venv venv
echo    source venv/bin/activate
echo    pip install --upgrade pip
echo    pip install -r requirements.txt
echo    uvicorn main:app --host 0.0.0.0 --port 8000
echo.
echo 4. Nginx 配置示例：
echo    server {
echo        listen 80;
echo        server_name %DOMAIN%;
echo        
echo        location / {
echo            root /var/www/bozhu/frontend;
echo            try_files $uri $uri/ /index.html;
echo        }
echo        
echo        location /api/ {
echo            proxy_pass http://127.0.0.1:8000;
echo            proxy_set_header Host $host;
echo        }
echo    }
echo.
echo 5. 使用 systemd 管理后端服务 ^(推荐^)
echo    创建 /etc/systemd/system/bozhu.service
echo    [Unit]
echo    Description=Bozhu Backend
echo    After=network.target
echo    
echo    [Service]
echo    Type=simple
echo    User=root
echo    WorkingDirectory=/var/www/bozhu/backend
echo    ExecStart=/var/www/bozhu/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
echo    Restart=always
echo    
echo    [Install]
echo    WantedBy=multi-user.target
echo.
echo    启动服务：
echo    sudo systemctl daemon-reload
echo    sudo systemctl enable bozhu
echo    sudo systemctl start bozhu
echo.
echo 默认账号：
echo    用户名: admin
echo    密码: admin123
echo.
echo 注意事项：
echo    - 首次登录后请修改密码
echo    - 定期备份 database.db 文件
echo    - 确保端口 8000 未被占用
) > "%OUTPUT_DIR%\部署说明.txt"

echo ✓ 部署说明已创建

echo.
echo [压缩] 打包成 zip 文件...
powershell -Command "Compress-Archive -Path '%OUTPUT_DIR%\*' -DestinationPath 'web-deploy.zip' -Force"

if exist "web-deploy.zip" (
    echo.
    echo ========================================
    echo   打包完成！
    echo ========================================
    echo.
    echo 文件: web-deploy.zip
    for %%A in ("web-deploy.zip") do echo 大小: %%~zA 字节
    echo.
    echo 包含内容:
    echo   - frontend/  ^(前端构建产物^)
    echo   - backend/   ^(后端源码^)
    echo   - 部署说明.txt
    echo.
    echo 上传到服务器后解压即可部署
    echo.
) else (
    echo.
    echo ✗ 打包失败
    pause
    exit /b 1
)

pause
