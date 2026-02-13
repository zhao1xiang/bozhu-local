@echo off
chcp 65001 >nul
echo ========================================
echo   更新版本号工具
echo ========================================
echo.

set /p NEW_VERSION="请输入新版本号 (例如: 2.2.0): "

if "%NEW_VERSION%"=="" (
    echo 错误：版本号不能为空
    pause
    exit /b 1
)

echo.
echo 正在更新版本号到 %NEW_VERSION%...
echo.

REM 更新 VERSION.txt
echo %NEW_VERSION%> VERSION.txt
echo ✓ 已更新 VERSION.txt

REM 更新前端版本号
powershell -Command "(Get-Content 'frontend\src\config\version.ts') -replace 'APP_VERSION = ''[^'']*''', 'APP_VERSION = ''%NEW_VERSION%''' | Set-Content 'frontend\src\config\version.ts'"
echo ✓ 已更新 frontend\src\config\version.ts

REM 更新后端版本号
powershell -Command "(Get-Content 'backend\run_server.py') -replace 'APP_VERSION = \"[^\"]*\"', 'APP_VERSION = \"%NEW_VERSION%\"' | Set-Content 'backend\run_server.py'"
echo ✓ 已更新 backend\run_server.py

REM 更新 Tauri 配置
powershell -Command "(Get-Content 'frontend\src-tauri\tauri.conf.json') -replace '\"version\": \"[^\"]*\"', '\"version\": \"%NEW_VERSION%\"' | Set-Content 'frontend\src-tauri\tauri.conf.json'"
echo ✓ 已更新 frontend\src-tauri\tauri.conf.json (version)

powershell -Command "(Get-Content 'frontend\src-tauri\tauri.conf.json') -replace '\"title\": \"眼科注射预约系统 v[^\"]*\"', '\"title\": \"眼科注射预约系统 v%NEW_VERSION%\"' | Set-Content 'frontend\src-tauri\tauri.conf.json'"
echo ✓ 已更新 frontend\src-tauri\tauri.conf.json (title)

echo.
echo ========================================
echo   版本号更新完成！
echo ========================================
echo.
echo 新版本号: %NEW_VERSION%
echo.
echo 已更新的文件:
echo - VERSION.txt
echo - frontend\src\config\version.ts
echo - backend\run_server.py
echo - frontend\src-tauri\tauri.conf.json
echo.
echo 下一步：运行打包脚本
echo   快速更新-v3.bat  或  完整打包流程-v2.bat
echo.
pause
