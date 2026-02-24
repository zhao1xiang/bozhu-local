@echo off
chcp 65001 >nul
echo ========================================
echo   清理并重新打包 EXE v2.1.1
echo ========================================
echo.

echo [1/3] 清理旧的构建文件...
cd frontend
if exist "dist" (
    echo 删除 frontend/dist...
    rmdir /s /q "dist"
)
if exist ".vite" (
    echo 删除 frontend/.vite...
    rmdir /s /q ".vite"
)
if exist "src-tauri\target\release" (
    echo 删除 src-tauri/target/release...
    rmdir /s /q "src-tauri\target\release"
)
cd ..

cd backend
if exist "dist" (
    echo 删除 backend/dist...
    rmdir /s /q "dist"
)
if exist "build" (
    echo 删除 backend/build...
    rmdir /s /q "build"
)
cd ..

echo ✓ 清理完成

echo.
echo [2/3] 确认环境变量未设置...
set VITE_SKIP_SPLASH=
set VITE_API_URL=
echo ✓ 环境变量已清除

echo.
echo [3/3] 开始完整打包...
call "完整打包流程-v2.1.1.bat"
