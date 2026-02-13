@echo off
chcp 65001 >nul
echo ========================================
echo WebView2 运行时检查工具
echo ========================================
echo.

:: 检查 WebView2 注册表项
echo [检查 1/3] 检查 WebView2 注册表...
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] WebView2 运行时已安装
    
    :: 获取版本信息
    for /f "tokens=3" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv 2^>nul ^| findstr pv') do (
        echo     版本：%%a
    )
) else (
    echo [✗] WebView2 运行时未安装
    echo.
    echo 请运行"安装WebView2.bat"进行安装
)

echo.

:: 检查 Microsoft Edge
echo [检查 2/3] 检查 Microsoft Edge 浏览器...
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo [✓] Microsoft Edge 已安装
) else (
    echo [!] Microsoft Edge 未安装（不影响 WebView2 运行）
)

echo.

:: 检查系统版本
echo [检查 3/3] 检查系统版本...
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo     Windows 版本：%VERSION%

if "%VERSION%" geq "10.0" (
    echo [✓] 系统版本符合要求
) else (
    echo [!] 系统版本较低，建议升级到 Windows 10 或更高版本
)

echo.
echo ========================================
echo 检查完成
echo ========================================
echo.

:: 给出建议
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 (
    echo 您的系统已安装 WebView2，可以正常运行"眼科注射预约系统"
    echo.
    echo 如果应用仍无法启动，请尝试：
    echo 1. 重启计算机
    echo 2. 以管理员身份运行应用
    echo 3. 检查防火墙和杀毒软件设置
    echo 4. 查看日志文件：logs\tauri.log
) else (
    echo 您的系统未安装 WebView2，请先安装：
    echo.
    echo 方式 1：运行"安装WebView2.bat"（推荐）
    echo 方式 2：参考"WebView2安装说明.md"手动安装
)

echo.
pause
