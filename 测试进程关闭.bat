@echo off
chcp 65001 >nul
echo ========================================
echo 测试后端进程关闭功能
echo ========================================
echo.

echo [步骤 1] 检查当前是否有 backend_server.exe 进程
tasklist | findstr /i "backend_server.exe"
if %errorlevel% equ 0 (
    echo 发现运行中的 backend_server.exe 进程
    echo 正在清理...
    taskkill /F /IM backend_server.exe
    timeout /t 2 >nul
) else (
    echo 没有发现运行中的 backend_server.exe 进程
)
echo.

echo [步骤 2] 启动应用
echo 请手动启动 dist-package\眼科注射预约系统.exe
echo 等待应用完全启动后按任意键继续...
pause >nul
echo.

echo [步骤 3] 检查后端进程是否启动
tasklist | findstr /i "backend_server.exe"
if %errorlevel% equ 0 (
    echo ✓ 后端进程已启动
) else (
    echo ✗ 后端进程未启动
    goto end
)
echo.

echo [步骤 4] 关闭应用
echo 请手动关闭应用窗口，然后按任意键继续...
pause >nul
echo.

echo [步骤 5] 等待 2 秒后检查进程
timeout /t 2 >nul
echo.

echo [步骤 6] 检查后端进程是否已关闭
tasklist | findstr /i "backend_server.exe"
if %errorlevel% equ 0 (
    echo ✗ 失败：后端进程仍在运行
    echo.
    echo 运行中的 backend_server.exe 进程：
    tasklist | findstr /i "backend_server.exe"
) else (
    echo ✓ 成功：后端进程已关闭
)
echo.

:end
echo ========================================
echo 测试完成
echo ========================================
pause
