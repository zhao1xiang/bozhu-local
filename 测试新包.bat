@echo off
chcp 65001 >nul
echo ========================================
echo   测试修复后的应用
echo ========================================
echo.
echo 测试内容：
echo 1. 数据库是否独立（不打包在 EXE 中）
echo 2. admin666 账号是否能登录
echo.
echo 当前数据库状态：
python 测试admin666登录.py
echo.
echo ========================================
echo 按任意键启动应用进行测试...
pause >nul

cd dist-package
start 眼科注射预约系统.exe
cd ..

echo.
echo 应用已启动！
echo.
echo 测试步骤：
echo 1. 使用 admin666 / admin 登录
echo 2. 如果能登录，说明数据库独立成功
echo 3. 关闭应用后，可以随时替换 dist-package\backend\database.db
echo.
pause
