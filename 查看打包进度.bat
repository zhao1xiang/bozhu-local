@echo off
chcp 65001 >nul
echo ========================================
echo   EXE 打包进度监控
echo ========================================
echo.

:loop
cls
echo ========================================
echo   EXE 打包进度监控
echo   时间: %date% %time%
echo ========================================
echo.

echo [1] 检查编译进程...
tasklist | findstr /i "cargo rustc" >nul
if errorlevel 1 (
    echo ✗ 编译进程未运行
    echo.
    echo 打包可能已完成或已停止
    goto check_files
) else (
    echo ✓ 编译进程正在运行
    echo.
    echo 进程详情:
    tasklist | findstr /i "cargo rustc"
)

echo.
echo [2] 检查构建产物...
:check_files

echo.
echo 后端:
if exist "backend\dist\backend_server.exe" (
    echo ✓ backend_server.exe 已生成
    for %%A in ("backend\dist\backend_server.exe") do echo   大小: %%~zA 字节 ^(%%~zAMB^)
) else (
    echo ✗ backend_server.exe 未生成
)

echo.
echo 前端:
if exist "frontend\dist\index.html" (
    echo ✓ 前端构建完成
) else (
    echo ✗ 前端未构建
)

echo.
echo Tauri 应用:
if exist "frontend\src-tauri\target\release\app.exe" (
    echo ✓ app.exe 已生成
    for %%A in ("frontend\src-tauri\target\release\app.exe") do echo   大小: %%~zA 字节
) else (
    echo ✗ app.exe 未生成 ^(正在编译中...^)
)

echo.
echo 分发包:
if exist "dist-package\眼科注射预约系统.exe" (
    echo ✓ 分发包已创建
    for %%A in ("dist-package\眼科注射预约系统.exe") do echo   大小: %%~zA 字节
) else (
    echo ✗ 分发包未创建
)

echo.
echo [3] Rust 编译进度...
if exist "frontend\src-tauri\target\release\.fingerprint" (
    echo 正在编译 Rust 依赖...
    dir /b "frontend\src-tauri\target\release\.fingerprint" | find /c /v "" 
    echo 个包已编译
) else (
    echo 编译信息不可用
)

echo.
echo ========================================
echo 按 Ctrl+C 退出监控
echo 10秒后自动刷新...
echo ========================================

timeout /t 10 /nobreak >nul
goto loop
