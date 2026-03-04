@echo off
chcp 65001 >nul
echo.
echo ════════════════════════════════════════════════════════════
echo   快速打包 - 仅后端（跳过前端构建）
echo ════════════════════════════════════════════════════════════
echo.

REM 设置 Python 3.7 路径
set PYTHON37_PATH=D:\workpath\python3.7.9
set PYINSTALLER37_EXE=%PYTHON37_PATH%\Scripts\pyinstaller.exe

echo [1/3] 检查环境...
if not exist "%PYINSTALLER37_EXE%" (
    echo ✗ 未找到 PyInstaller
    echo 请先运行：pip install pyinstaller==5.13.2
    pause
    exit /b 1
)
echo ✓ PyInstaller 已安装
echo.

echo [2/3] 打包后端...
cd backend

echo 清理旧文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo 开始打包（请等待 1-2 分钟）...
"%PYINSTALLER37_EXE%" build_win7_compatible.spec --clean

if not exist "dist\backend_server.exe" (
    echo ✗ 打包失败
    cd ..
    pause
    exit /b 1
)

for %%F in ("dist\backend_server.exe") do (
    set /a SIZE_MB=%%~zF / 1048576
    echo ✓ 打包完成（大小：!SIZE_MB! MB）
)
echo.

echo [3/3] 复制到输出目录...
cd ..
if not exist "simple-web-package-win7-v2.1.7" mkdir "simple-web-package-win7-v2.1.7"
copy "backend\dist\backend_server.exe" "simple-web-package-win7-v2.1.7\" >nul
echo ✓ 已复制到 simple-web-package-win7-v2.1.7\
echo.

echo ════════════════════════════════════════════════════════════
echo ✅ 后端打包完成
echo ════════════════════════════════════════════════════════════
echo.
echo 提示：
echo - 前端文件未更新，请手动复制 frontend\dist 到输出目录
echo - 或运行完整打包脚本
echo.
pause
