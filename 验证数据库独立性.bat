@echo off
chcp 65001 >nul
echo ========================================
echo   验证数据库独立性测试
echo ========================================
echo.

echo [测试 1] 检查当前数据库内容
echo ----------------------------------------
python 测试admin666登录.py
echo.

echo [测试 2] 备份当前数据库
echo ----------------------------------------
copy "dist-package\backend\database.db" "dist-package\backend\database_backup.db" /Y >nul
echo ✓ 已备份到 database_backup.db
echo.

echo [测试 3] 启动应用测试
echo ----------------------------------------
echo 请按以下步骤测试：
echo.
echo 1. 点击任意键启动应用
echo 2. 使用 admin666 / admin 登录
echo 3. 查看患者列表（应该有数据）
echo 4. 关闭应用
echo.
pause

cd dist-package
start 眼科注射预约系统.exe
cd ..

echo.
echo 应用已启动，请完成测试后关闭应用...
echo.
pause

echo.
echo [测试 4] 替换数据库测试
echo ----------------------------------------
echo 现在我们将替换数据库文件，测试是否生效
echo.
echo 选项：
echo 1. 使用备份的数据库（恢复原状）
echo 2. 使用新的空数据库（清空数据）
echo 3. 跳过此测试
echo.
set /p choice="请选择 (1/2/3): "

if "%choice%"=="1" (
    copy "dist-package\backend\database_backup.db" "dist-package\backend\database.db" /Y >nul
    echo ✓ 已恢复备份数据库
) else if "%choice%"=="2" (
    echo 创建新的空数据库...
    python -c "import sqlite3; conn = sqlite3.connect('dist-package/backend/database_new.db'); conn.close()"
    copy "dist-package\backend\database_new.db" "dist-package\backend\database.db" /Y >nul
    echo ✓ 已替换为空数据库
) else (
    echo 跳过测试
    goto :end
)

echo.
echo 再次启动应用验证...
pause

cd dist-package
start 眼科注射预约系统.exe
cd ..

echo.
echo 应用已启动！
echo 如果数据库独立成功，你应该看到：
echo - 选项1：数据恢复正常
echo - 选项2：数据被清空
echo.

:end
echo.
echo ========================================
echo   测试完成
echo ========================================
echo.
echo 结论：
echo 如果替换数据库后重启应用，数据发生了变化，
echo 说明数据库独立性修复成功！
echo.
echo 现在你可以随时替换 dist-package\backend\database.db
echo 重启应用即可生效。
echo.
pause
