@echo off
chcp 65001 >nul
echo ========================================
echo   完整打包流程 v2.1.2
echo   (包含自动数据库升级功能)
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
echo 设置 Node.js 内存限制...
set NODE_OPTIONS=--max-old-space-size=4096
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
if not exist "dist-package\logs" mkdir "dist-package\logs"
echo ✓ 目录结构创建完成

echo.
echo [5/6] 复制文件（扁平化结构）...
echo 复制主程序...
copy "frontend\src-tauri\target\release\app.exe" "dist-package\眼科注射预约系统.exe" /Y

echo 复制后端文件到根目录...
copy "backend\dist\backend_server.exe" "dist-package\backend_server.exe" /Y
copy "backend\database.db" "dist-package\database.db" /Y

echo 复制 WebView2 相关文件...
copy "安装WebView2.bat" "dist-package\安装WebView2.bat" /Y
copy "检查WebView2.bat" "dist-package\检查WebView2.bat" /Y
if exist "WebView2安装说明.md" copy "WebView2安装说明.md" "dist-package\WebView2安装说明.md" /Y

echo 复制版本更新说明...
copy "版本更新说明_v2.1.2.txt" "dist-package\版本更新说明.txt" /Y

echo ✓ 文件复制完成

echo.
echo [6/6] 创建启动和诊断脚本...
cd dist-package

REM 创建智能启动脚本（自动检测 WebView2）
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo   眼科注射预约系统 v2.1.2
echo echo ========================================
echo echo.
echo.
echo REM 检查 WebView2
echo echo 正在检查 WebView2 运行时...
echo reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     reg query "HKCU\Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv ^>nul 2^>^&1
echo     if errorlevel 1 ^(
echo         echo.
echo         echo ✗ 未检测到 WebView2 运行时
echo         echo.
echo         echo 系统需要 WebView2 才能运行。
echo         echo 正在尝试自动安装...
echo         echo.
echo         call 安装WebView2.bat
echo         timeout /t 3
echo     ^) else ^(
echo         echo ✓ WebView2 已安装
echo     ^)
echo ^) else ^(
echo     echo ✓ WebView2 已安装
echo ^)
echo.
echo echo 正在启动应用...
echo start "" "眼科注射预约系统.exe"
echo echo ✓ 应用已启动
echo echo.
echo echo 日志文件位置: logs\backend.log
echo echo.
echo timeout /t 3
echo exit
) > 启动系统.bat

REM 创建查看日志脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo   查看日志文件
echo echo ========================================
echo echo.
echo if exist "logs\backend.log" ^(
echo     echo 后端日志内容:
echo     echo ----------------------------------------
echo     type "logs\backend.log"
echo ^) else ^(
echo     echo 日志文件不存在: logs\backend.log
echo ^)
echo echo.
echo pause
) > 查看日志.bat

REM 创建诊断工具
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo   系统诊断工具 v2.1.2
echo echo ========================================
echo echo.
echo echo [1] 检查文件结构...
echo if exist "眼科注射预约系统.exe" ^(echo ✓ 主程序存在^) else ^(echo ✗ 主程序不存在^)
echo if exist "backend_server.exe" ^(echo ✓ 后端程序存在^) else ^(echo ✗ 后端程序不存在^)
echo if exist "database.db" ^(echo ✓ 数据库存在^) else ^(echo ✗ 数据库不存在^)
echo if exist "logs" ^(echo ✓ logs 目录存在^) else ^(echo ✗ logs 目录不存在^)
echo echo.
echo echo [2] 检查 WebView2...
echo reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     reg query "HKCU\Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv ^>nul 2^>^&1
echo     if errorlevel 1 ^(
echo         echo ✗ WebView2 未安装
echo     ^) else ^(
echo         echo ✓ WebView2 已安装 ^(用户级^)
echo     ^)
echo ^) else ^(
echo     echo ✓ WebView2 已安装 ^(系统级^)
echo ^)
echo echo.
echo echo [3] 检查端口占用...
echo netstat -ano ^| findstr ":8000" ^>nul
echo if errorlevel 1 ^(
echo     echo ✓ 端口 8000 未被占用
echo ^) else ^(
echo     echo ✗ 端口 8000 已被占用
echo     echo 占用进程:
echo     netstat -ano ^| findstr ":8000"
echo ^)
echo echo.
echo echo [4] 查看最近的日志...
echo if exist "logs\backend.log" ^(
echo     echo 后端日志 ^(最后 20 行^):
echo     echo ----------------------------------------
echo     powershell -Command "Get-Content 'logs\backend.log' -Tail 20"
echo ^) else ^(
echo     echo 日志文件不存在
echo ^)
echo echo.
echo pause
) > 诊断工具.bat

REM 创建部署说明
(
echo 眼科注射预约系统 v2.1.2 部署说明
echo ====================================
echo.
echo 【重要更新】
echo 本版本包含自动数据库升级功能！
echo 启动时会自动检测并升级数据库结构，无需手动操作。
echo.
echo 文件结构（扁平化）：
echo   眼科注射预约系统.exe  - 主程序
echo   backend_server.exe    - 后端服务（包含自动升级功能）
echo   database.db           - 数据库文件
echo   logs/                 - 日志文件夹
echo     backend.log         - 后端日志（包含升级日志）
echo   安装WebView2.bat      - WebView2 安装工具
echo   检查WebView2.bat      - WebView2 检测工具
echo   启动系统.bat          - 智能启动脚本
echo   查看日志.bat          - 日志查看工具
echo   诊断工具.bat          - 系统诊断工具
echo   版本更新说明.txt      - 详细更新说明
echo.
echo 【首次安装】
echo   1. 解压所有文件到目标目录
echo   2. 双击"启动系统.bat"或"眼科注射预约系统.exe"
echo   3. 系统会自动检测并安装 WebView2（如需要）
echo   4. 使用默认账号登录：admin / admin123
echo.
echo 【版本升级】
echo   1. 关闭正在运行的应用程序
echo   2. 备份 database.db 文件（可选，系统会自动备份）
echo   3. 用新版本的 .exe 文件覆盖旧文件：
echo      - 眼科注射预约系统.exe
echo      - backend_server.exe
echo   4. 启动应用程序
echo   5. 系统会自动升级数据库（首次启动可能需要几秒钟）
echo   6. 完成！
echo.
echo 【自动数据库升级】
echo   ✓ 启动时自动检测数据库结构
echo   ✓ 自动备份数据库（database.db.backup_日期时间）
echo   ✓ 静默添加新字段
echo   ✓ 保留所有现有数据
echo   ✓ 升级日志记录在 logs\backend.log
echo.
echo 【新增功能 v2.1.2】
echo   ✓ 患者管理：新增"就诊卡号"字段
echo   ✓ 预约管理：新增管床医生、病毒报告、血糖、血压、眼压、冲眼结果等字段
echo   ✓ 数据导出：包含所有新增字段
echo   ✓ 预约流程：优化从患者列表跳转预约的体验
echo   ✓ 自动升级：启动时自动升级数据库，无需手动操作
echo.
echo 【默认管理员账号】
echo   用户名：admin
echo   密码：admin123
echo   首次使用请修改默认密码
echo.
echo 【注意事项】
echo   1. 首次升级启动可能需要3-5秒（数据库升级）
echo   2. 升级后会生成备份文件，建议保留
echo   3. 定期备份 database.db 文件
echo   4. 如遇问题，运行"诊断工具.bat"检查
echo   5. 查看升级日志请运行"查看日志.bat"
echo.
echo 【系统要求】
echo   - Windows 10/11
echo   - WebView2 运行时（首次启动会自动安装）
echo   - 端口 8000 未被占用
echo.
echo 【故障排除】
echo   问题：升级后无法启动
echo   解决：查看 logs\backend.log，使用备份文件恢复
echo.
echo   问题：提示缺少 WebView2
echo   解决：运行"安装WebView2.bat"
echo.
echo   问题：端口被占用
echo   解决：运行"诊断工具.bat"查看占用进程
echo.
echo 【技术支持】
echo   如有问题请联系系统管理员
echo   日志文件：logs\backend.log
echo   备份文件：database.db.backup_日期时间
) > 部署说明_v2.1.2.txt

cd ..

echo ✓ 脚本创建完成

echo.
echo ========================================
echo   打包完成！v2.1.2
echo ========================================
echo.
echo 分发包位置: dist-package\
echo.
echo 文件结构（扁平化）:
echo   dist-package\
echo   ├── 眼科注射预约系统.exe
echo   ├── backend_server.exe （包含自动升级功能）
echo   ├── database.db
echo   ├── logs\
echo   ├── 安装WebView2.bat
echo   ├── 检查WebView2.bat
echo   ├── 启动系统.bat
echo   ├── 查看日志.bat
echo   ├── 诊断工具.bat
echo   ├── 版本更新说明.txt
echo   └── 部署说明_v2.1.2.txt
echo.
echo 【重要】本版本包含自动数据库升级功能
echo   - 客户只需覆盖 .exe 文件并启动
echo   - 系统会自动升级数据库
echo   - 无需手动操作
echo.
echo 可以将 dist-package 文件夹打包发送给用户
echo 用户替换版本时，只需替换 .exe 文件即可
echo.
pause
