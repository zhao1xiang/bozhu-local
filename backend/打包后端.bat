@echo off
chcp 65001 >nul
echo ========================================
echo   打包 FastAPI 后端
echo ========================================
echo.

echo 正在打包...
python -m PyInstaller build_backend.spec --clean

if exist "dist\backend_server.exe" (
    echo.
    echo ========================================
    echo   打包成功！
    echo ========================================
    echo.
    echo 输出文件: dist\backend_server.exe
    dir dist\backend_server.exe
) else (
    echo.
    echo [错误] 打包失败
)

echo.
pause
