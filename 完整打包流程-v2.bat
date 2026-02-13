@echo off
chcp 65001 >nul
echo ========================================
echo   完整打包流程 v2.0
echo   (新文件结构: backend/ 和 logs/)
echo ========================================
echo.

echo [1/6] 打包后端...
cd backend
echo 正在打包后端...
python -m PyInstaller build_backend.spec --clean
if not exist "dist\backend_server.exe" (
    echo ✗ 后端打包失败
    cd ..
    pause
    exit /b 1
)
echo ✓ 后端打包完成
cd ..

echo.
echo [2/6] 构建前端...
cd frontend
call npm run build
if not exist "dist\index.html" (
    echo ✗ 前端构建失败
    cd ..
    pause
    exit /b 1
)
echo ✓ 前端构建完成

echo.
echo [3/6] 构建 Tauri 应用...
call npm run tauri build
if not exist "src-tauri\target\release\app.exe" (
    echo ✗ Tauri 构建失败
    cd ..
    pause
    exit /b 1
)
echo ✓ Tauri 构建完成
cd ..

echo.
echo [4/6] 创建分发包目录结构...
if not exist "dist-package" mkdir "dist-package"
if not exist "dist-package\backend" mkdir "dist-package\backend"
if not exist "dist-package\logs" mkdir "dist-package\logs"
echo ✓ 目录结构创建完成

echo.
echo [5/6] 复制文件...
echo 复制主程序...
copy "frontend\src-tauri\target\release\app.exe" "dist-package\眼科注射预约系统.exe" /Y

echo 复制后端文件到 backend 目录...
copy "backend\dist\backend_server.exe" "dist-package\backend\backend_server.exe" /Y
copy "backend\database.db" "dist-package\backend\database.db" /Y

echo ✓ 文件复制完成

echo.
echo [6/6] 创建启动和诊断脚本...
cd dist-package

REM 创建启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo   眼科注射预约系统
echo echo ========================================
echo echo.
echo echo 正在启动应用...
echo start "" "眼科注射预约系统.exe"
echo echo ✓ 应用已启动
echo echo.
echo echo 日志文件位置:
echo echo - logs\backend.log  ^(后端日志^)
echo echo - logs\tauri.log    ^(前端日志^)
echo echo.
echo timeout /t 3
echo exit
) > 启动应用.bat

REM 创建查看日志脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo   查看日志文件
echo echo ========================================
echo echo.
echo echo [1] 后端日志 ^(logs\backend.log^):
echo echo ----------------------------------------
echo if exist "logs\backend.log" ^(
echo     type "logs\backend.log"
echo ^) else ^(
echo     echo 日志文件不存在
echo ^)
echo echo.
echo echo.
echo echo [2] Tauri 日志 ^(logs\tauri.log^):
echo echo ----------------------------------------
echo if exist "logs\tauri.log" ^(
echo     type "logs\tauri.log"
echo ^) else ^(
echo     echo 日志文件不存在
echo ^)
echo echo.
echo pause
) > 查看日志.bat

REM 创建诊断工具
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo   系统诊断工具
echo echo ========================================
echo echo.
echo echo [1] 检查文件结构...
echo if exist "眼科注射预约系统.exe" ^(echo ✓ 主程序存在^) else ^(echo ✗ 主程序不存在^)
echo if exist "backend\backend_server.exe" ^(echo ✓ 后端程序存在^) else ^(echo ✗ 后端程序不存在^)
echo if exist "backend\database.db" ^(echo ✓ 数据库存在^) else ^(echo ✗ 数据库不存在^)
echo if exist "logs" ^(echo ✓ logs 目录存在^) else ^(echo ✗ logs 目录不存在^)
echo echo.
echo echo [2] 检查端口占用...
echo netstat -ano ^| findstr ":8000"
echo if errorlevel 1 ^(
echo     echo ✓ 端口 8000 未被占用
echo ^) else ^(
echo     echo ✗ 端口 8000 已被占用
echo ^)
echo echo.
echo echo [3] 查看最近的日志...
echo if exist "logs\backend.log" ^(
echo     echo 后端日志 ^(最后 20 行^):
echo     powershell -Command "Get-Content 'logs\backend.log' -Tail 20"
echo ^)
echo echo.
echo if exist "logs\tauri.log" ^(
echo     echo Tauri 日志 ^(最后 20 行^):
echo     powershell -Command "Get-Content 'logs\tauri.log' -Tail 20"
echo ^)
echo echo.
echo pause
) > 诊断工具.bat

REM 创建使用说明
(
echo 眼科注射预约系统 v2.0
echo ====================
echo.
echo 文件结构：
echo   眼科注射预约系统.exe  - 主程序
echo   backend/              - 后端文件夹
echo     backend_server.exe  - 后端服务
echo     database.db         - 数据库文件
echo   logs/                 - 日志文件夹
echo     backend.log         - 后端日志
echo     tauri.log           - 前端日志
echo.
echo 启动方法：
echo   1. 双击"启动应用.bat"启动系统
echo   2. 或直接双击"眼科注射预约系统.exe"
echo   3. 应用会自动启动后端服务
echo   4. 关闭应用时会自动关闭后端服务
echo.
echo 默认管理员账号：
echo   用户名：admin
echo   密码：admin123
echo.
echo 注意事项：
echo   1. 首次使用请修改默认密码
echo   2. 定期备份 backend\database.db 文件
echo   3. 如遇问题，运行"诊断工具.bat"检查
echo   4. 查看日志请运行"查看日志.bat"
echo.
echo 新功能：
echo   ✓ 关闭应用时自动关闭后端服务
echo   ✓ 日志文件统一管理在 logs 目录
echo   ✓ 后端文件独立存放在 backend 目录
echo.
echo 技术支持：
echo   如有问题请联系系统管理员
) > 使用说明.txt

cd ..

echo ✓ 脚本创建完成

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 分发包位置: dist-package\
echo.
echo 文件结构:
echo   dist-package\
echo   ├── 眼科注射预约系统.exe
echo   ├── backend\
echo   │   ├── backend_server.exe
echo   │   └── database.db
echo   ├── logs\
echo   ├── 启动应用.bat
echo   ├── 查看日志.bat
echo   ├── 诊断工具.bat
echo   └── 使用说明.txt
echo.
echo 可以将 dist-package 文件夹打包发送给用户
echo.
pause
