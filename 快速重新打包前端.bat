@echo off
chcp 65001 >nul
echo ========================================
echo   快速重新打包前端和Tauri
echo   (跳过后端打包，节省时间)
echo ========================================
echo.

echo [1/3] 清理前端缓存...
cd frontend
if exist "dist" rmdir /s /q "dist"
if exist ".vite" rmdir /s /q ".vite"
if exist "src-tauri\target\release\app.exe" del "src-tauri\target\release\app.exe"
echo ✓ 清理完成

echo.
echo [2/3] 构建前端...
set NODE_OPTIONS=--max-old-space-size=4096
call npm run build
if not exist "dist\index.html" (
    echo ✗ 前端构建失败
    cd ..
    pause
    exit /b 1
)
echo ✓ 前端构建完成

echo.
echo [3/3] 构建 Tauri 应用...
call npm run tauri build
if not exist "src-tauri\target\release\app.exe" (
    echo ✗ Tauri 构建失败
    cd ..
    pause
    exit /b 1
)
echo ✓ Tauri 构建完成

cd ..

echo.
echo [4/4] 更新分发包...
if not exist "dist-package" mkdir "dist-package"
copy "frontend\src-tauri\target\release\app.exe" "dist-package\眼科注射预约系统.exe" /Y
echo ✓ 分发包已更新

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 文件位置: dist-package\眼科注射预约系统.exe
echo.
echo 测试步骤:
echo 1. 运行 dist-package\眼科注射预约系统.exe
echo 2. 应该先看到紫色 Splash 页面
echo 3. 如果直接进入登录页，访问: http://localhost:5173/debug
echo    查看环境检测信息
echo.

pause
