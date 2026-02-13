@echo off
chcp 65001 >nul
echo ========================================
echo Microsoft Edge WebView2 运行时安装
echo ========================================
echo.
echo 正在检查 WebView2 运行时...
echo.

:: 检查是否已安装 WebView2
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] WebView2 运行时已安装
    echo.
    echo 如果应用仍无法启动，请尝试：
    echo 1. 重启计算机
    echo 2. 重新安装 WebView2（删除后重新运行此脚本）
    echo 3. 联系技术支持
    echo.
    pause
    exit /b 0
)

echo [!] 未检测到 WebView2 运行时
echo.
echo 正在下载并安装 WebView2...
echo 这可能需要几分钟时间，请耐心等待...
echo.

:: 创建临时目录
set TEMP_DIR=%TEMP%\WebView2Setup
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: 下载 WebView2 安装程序
echo [1/3] 正在下载安装程序...
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile '%TEMP_DIR%\MicrosoftEdgeWebview2Setup.exe'}"

if %errorlevel% neq 0 (
    echo.
    echo [错误] 下载失败，请检查网络连接
    echo.
    echo 您也可以手动下载安装：
    echo 1. 访问：https://developer.microsoft.com/zh-cn/microsoft-edge/webview2/
    echo 2. 下载"常青版独立安装程序"
    echo 3. 运行安装程序
    echo.
    pause
    exit /b 1
)

echo [✓] 下载完成
echo.

:: 运行安装程序
echo [2/3] 正在安装 WebView2...
echo 请在弹出的安装窗口中按照提示完成安装
echo.
start /wait "" "%TEMP_DIR%\MicrosoftEdgeWebview2Setup.exe"

:: 清理临时文件
echo.
echo [3/3] 清理临时文件...
del /f /q "%TEMP_DIR%\MicrosoftEdgeWebview2Setup.exe"
rmdir "%TEMP_DIR%"

:: 验证安装
echo.
echo 正在验证安装...
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [✓] WebView2 安装成功！
    echo ========================================
    echo.
    echo 现在可以启动"眼科注射预约系统"了
    echo.
) else (
    echo.
    echo ========================================
    echo [!] 安装可能未成功
    echo ========================================
    echo.
    echo 请尝试：
    echo 1. 重启计算机后重新运行此脚本
    echo 2. 手动下载安装（参考 WebView2安装说明.md）
    echo 3. 联系技术支持
    echo.
)

pause
