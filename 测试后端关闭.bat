@echo off
chcp 65001 >nul
echo ========================================
echo   测试后端进程关闭
echo ========================================
echo.

echo [1] 清理所有旧进程
taskkill /F /IM backend_server.exe >nul 2>&1
taskkill /F /IM 眼科注射预约系统.exe >nul 2>&1
timeout /t 2 >nul
echo ✓ 已清理
echo.

echo [2] 启动应用
start "" "dist-package\眼科注射预约系统.exe"
echo ✓ 应用已启动
echo.

echo [3] 等待 10 秒让应用完全启动...
timeout /t 10
echo.

echo [4] 检查进程状态
echo 当前运行的进程：
tasklist | findstr /I "眼科注射预约系统.exe backend_server.exe"
echo.

echo [5] 请手动关闭应用窗口...
echo 关闭后按任意键继续检查
pause >nul
echo.

echo [6] 等待 3 秒让进程完全关闭...
timeout /t 3 >nul
echo.

echo [7] 检查后端进程是否还在运行
tasklist | findstr /I "backend_server.exe"
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ✓ 成功！后端进程已关闭
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   ✗ 失败！后端进程仍在运行
    echo ========================================
    echo.
    echo 进程详情：
    tasklist | findstr /I "backend_server.exe"
    echo.
    echo 查看 Tauri 日志：
    type "dist-package\logs\tauri.log"
)
echo.
pause
