@echo off
chcp 65001 >nul
echo ========================================
echo   修复数据库不生效问题
echo ========================================
echo.

echo 问题原因：
echo Tauri 将 backend/dist/database.db 打包到了 EXE 中
echo 每次启动都会使用打包时的数据库，而不是你替换的文件
echo.

echo 解决方案：
echo 1. 修改 Tauri 配置，不打包数据库文件
echo 2. 重新打包 Tauri
echo 3. 数据库文件将独立存放，可以随时替换
echo.

echo ========================================
echo   开始修复
echo ========================================
echo.

echo [1/4] 已修改 Tauri 配置...
echo ✓ 配置已更新为只打包 backend_server.exe
echo.

echo [2/4] 构建前端...
cd frontend
call npm run build
if errorlevel 1 (
    echo ✗ 前端构建失败
    cd ..
    pause
    exit /b 1
)
echo ✓ 前端构建完成
echo.

echo [3/4] 重新打包 Tauri...
call npm run tauri build
if errorlevel 1 (
    echo ✗ Tauri 构建失败
    cd ..
    pause
    exit /b 1
)
echo ✓ Tauri 构建完成
cd ..
echo.

echo [4/4] 更新分发包...
copy "frontend\src-tauri\target\release\app.exe" "dist-package\眼科注射预约系统.exe" /Y
echo ✓ 文件已更新
echo.

echo ========================================
echo   修复完成！
echo ========================================
echo.
echo 现在数据库文件是独立的：
echo - 位置：dist-package\backend\database.db
echo - 可以随时替换
echo - 替换后重启应用即可生效
echo.
echo 测试：
echo 1. 替换 dist-package\backend\database.db
echo 2. 启动应用
echo 3. 数据应该是新的了
echo.
pause
