@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Web 版本打包工具 - 调试模式                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 设置 Python 3.7 路径
set PYTHON37_PATH=D:\workpath\python3.7.9
set PYTHON37_EXE=%PYTHON37_PATH%\python.exe
set PIP37_EXE=%PYTHON37_PATH%\Scripts\pip.exe
set PYINSTALLER37_EXE=%PYTHON37_PATH%\Scripts\pyinstaller.exe

echo [调试信息] 当前目录: %CD%
echo [调试信息] Python 路径: %PYTHON37_EXE%
echo.

REM 检查 Python 3.7
echo [1/3] 检查 Python 3.7...
if not exist "%PYTHON37_EXE%" (
    echo.
    echo ✗ 错误：未找到 Python 3.7
    echo   路径：%PYTHON37_EXE%
    echo.
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)

"%PYTHON37_EXE%" --version
if errorlevel 1 (
    echo ✗ Python 3.7 无法运行
    echo.
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)
echo ✓ Python 3.7 已安装
echo.

REM 检查 Node.js
echo [2/3] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未找到 Node.js
    echo.
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)
node --version
echo ✓ Node.js 已安装
echo.

REM 检查 npm
echo [3/3] 检查 npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ✗ npm 不可用
    echo.
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)
npm --version
echo ✓ npm 已安装
echo.

echo ════════════════════════════════════════════════════════════
echo 环境检查完成！
echo ════════════════════════════════════════════════════════════
echo.
echo 现在可以运行完整打包脚本了
echo.
echo 请按任意键退出...
pause >nul
