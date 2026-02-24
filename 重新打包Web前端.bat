@echo off
chcp 65001 >nul
echo ========================================
echo   重新打包 Web 前端代码
echo   确保接口路径携带 /api
echo   不影响 EXE 版本
echo ========================================
echo.

set DOMAIN=local-show.microcall.com.cn
set OUTPUT_DIR=web-frontend-only

echo [1/4] 清理旧文件...
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
if exist "web-frontend-only.zip" del "web-frontend-only.zip"

echo.
echo [2/4] 构建前端（携带 /api 路径）...
cd frontend
REM 清理缓存
if exist "dist" rmdir /s /q "dist"
if exist ".vite" rmdir /s /q ".vite"
REM 设置环境变量 - Web 端使用完整 API 路径
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
echo [3/4] 准备前端文件...
mkdir "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%\frontend"

REM 复制前端构建产物
xcopy frontend\dist "%OUTPUT_DIR%\frontend" /E /I /Q

echo ✓ 前端文件准备完成

echo.
echo [4/4] 创建部署说明...
(
echo Web 前端部署包
echo ================
echo.
echo 说明：此包仅包含前端代码，已配置正确的 API 路径
echo.
echo 配置详情：
echo   - API 地址: https://%DOMAIN%/api
echo   - 跳过 Splash 页面: 是
echo   - 不影响 EXE 版本: 是
echo.
echo 部署步骤：
echo ----------
echo 1. 上传到服务器
echo    scp web-frontend-only.zip root@your_server_ip:/tmp/
echo.
echo 2. 解压并替换前端文件
echo    cd /work/local-show
echo    unzip /tmp/web-frontend-only.zip
echo    # 或手动复制
echo    # cp -r frontend/* /work/local-show/frontend/
echo.
echo 3. 重启 Nginx（可选）
echo    systemctl restart nginx
echo.
echo 验证：
echo   - 访问: https://%DOMAIN%/
echo   - 登录接口: https://%DOMAIN%/api/auth/token
echo   - 健康检查: https://%DOMAIN%/health
echo.
echo 注意：此包专为 Web 部署，EXE 版本使用独立配置
) > "%OUTPUT_DIR%\部署说明.txt"

echo ✓ 部署说明已创建

echo.
echo [压缩] 打包成 zip 文件...
powershell -Command "Compress-Archive -Path '%OUTPUT_DIR%\*' -DestinationPath 'web-frontend-only.zip' -Force"

if exist "web-frontend-only.zip" (
    echo.
    echo ========================================
    echo   打包完成！
    echo ========================================
    echo.
    echo 文件: web-frontend-only.zip
    for %%A in ("web-frontend-only.zip") do echo 大小: %%~zA 字节
    echo.
    echo 包含内容:
    echo   - frontend/  ^(前端构建产物^)
    echo   - 部署说明.txt
    echo.
    echo 关键配置:
    echo   ✓ API 路径: https://%DOMAIN%/api
    echo   ✓ 跳过 Splash 页面
    echo   ✓ 不影响 EXE 版本
    echo.
    echo 上传到服务器替换 /work/local-show/frontend/ 目录
    echo.
) else (
    echo.
    echo ✗ 打包失败
    pause
    exit /b 1
)

echo 验证构建配置:
echo 1. 检查 API 配置:
findstr /C:"VITE_API_URL" frontend\.env* 2>nul || echo "使用环境变量配置"
echo 2. EXE 版本配置保持不变:
echo    - 默认 API: http://127.0.0.1:8000/api
echo    - 显示 Splash 页面
echo    - 检测后端启动

pause