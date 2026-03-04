@echo off
chcp 65001 >nul
echo.
echo ════════════════════════════════════════════════════════════
echo   密码格式迁移工具
echo   bcrypt 转 PBKDF2
echo ════════════════════════════════════════════════════════════
echo.
echo 使用说明：
echo   1. 此工具用于将旧版本（EXE）的数据库迁移到新版本（Web）
echo   2. 会自动备份数据库
echo   3. 需要为 bcrypt 格式的用户设置新密码
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM 设置 Python 路径
set PYTHON_EXE=D:\workpath\python3.7.9\python.exe

REM 检查 Python
if not exist "%PYTHON_EXE%" (
    echo ✗ 未找到 Python
    echo.
    echo 请修改此脚本第 18 行的 Python 路径
    echo 或者手动运行: python backend\migrate_bcrypt_to_pbkdf2.py
    echo.
    pause
    exit /b 1
)

REM 运行迁移工具
cd backend
"%PYTHON_EXE%" migrate_bcrypt_to_pbkdf2.py
cd ..

echo.
pause
