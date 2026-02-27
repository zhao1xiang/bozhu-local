@echo off
chcp 65001 >nul
echo ========================================
echo   构建32位版本
echo ========================================
echo.

REM 检查是否安装了32位Rust工具链
echo [1/6] 检查32位Rust工具链...
rustup target list | findstr /C:"i686-pc-windows-msvc (installed)" >nul
if errorlevel 1 (
    echo ✗ 未安装32位Rust工具链
    echo.
    echo 正在安装32位Rust工具链...
    rustup target add i686-pc-windows-msvc
    if errorlevel 1 (
        echo ✗ 安装失败
        pause
        exit /b 1
    )
    echo ✓ 安装成功
) else (
    echo ✓ 已安装32位Rust工具链
)
echo.

REM 检查32位Python
echo [2/6] 检查32位Python...
set PYTHON32=C:\Python311-32\python.exe
if not exist "%PYTHON32%" (
    echo ⚠ 未找到32位Python: %PYTHON32%
    echo.
    echo 请手动指定32位Python路径，或按回车使用默认Python
    set /p PYTHON32="32位Python路径 (留空使用默认): "
    if "%PYTHON32%"=="" set PYTHON32=python
)
echo ✓ 使用Python: %PYTHON32%
echo.

REM 清理旧的构建文件
echo [3/6] 清理旧的构建文件...
if exist "backend\dist" rmdir /s /q "backend\dist"
if exist "backend\build" rmdir /s /q "backend\build"
if exist "frontend\src-tauri\target\i686-pc-windows-msvc" rmdir /s /q "frontend\src-tauri\target\i686-pc-windows-msvc"
echo ✓ 清理完成
echo.

REM 构建后端（32位）
echo [4/6] 构建32位后端...
cd backend
"%PYTHON32%" -m pip install pyinstaller >nul 2>&1
"%PYTHON32%" -m PyInstaller build_backend.spec --clean
if errorlevel 1 (
    echo ✗ 后端构建失败
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✓ 后端构建完成
echo.

REM 构建前端
echo [5/6] 构建前端...
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

REM 构建Tauri应用（32位）
echo [6/6] 构建32位Tauri应用...
call npm run tauri build -- --target i686-pc-windows-msvc
if errorlevel 1 (
    echo ✗ Tauri构建失败
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✓ Tauri构建完成
echo.

echo ========================================
echo   构建完成！
echo ========================================
echo.
echo 32位版本位置：
echo frontend\src-tauri\target\i686-pc-windows-msvc\release\bundle\
echo.
echo 注意事项：
echo 1. 32位版本仅支持32位Windows系统
echo 2. 需要安装32位WebView2 Runtime
echo 3. 性能可能不如64位版本
echo.
pause
