@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Web 版本打包工具 v2.1.7                           ║
echo ║         Windows 7 兼容版本 - bcrypt 支持                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 设置 Python 3.7 路径（请根据实际情况修改）
set PYTHON37_PATH=D:\workpath\python3.7.9
set PYTHON37_EXE=%PYTHON37_PATH%\python.exe
set PIP37_EXE=%PYTHON37_PATH%\Scripts\pip.exe
set PYINSTALLER37_EXE=%PYTHON37_PATH%\Scripts\pyinstaller.exe

REM 记录开始时间
echo [%time%] 开始打包流程
echo.

REM ============================================================
REM 步骤 0: 环境检查
REM ============================================================
echo ════════════════════════════════════════════════════════════
echo [步骤 0/5] 环境检查
echo ════════════════════════════════════════════════════════════
echo.

REM 检查 Python 3.7
echo [1/3] 检查 Python 3.7...
if not exist "%PYTHON37_EXE%" (
    echo.
    echo ✗ 错误：未找到 Python 3.7
    echo   路径：%PYTHON37_EXE%
    echo.
    echo 解决方法：
    echo   1. 安装 Python 3.7.9
    echo   2. 或修改脚本第 11 行的路径
    echo.
    echo 下载地址：https://www.python.org/downloads/release/python-379/
    echo.
    goto :error
)
"%PYTHON37_EXE%" --version 2>nul
if errorlevel 1 (
    echo ✗ Python 3.7 无法运行
    goto :error
)
echo ✓ Python 3.7 已安装
echo.

REM 检查 Node.js
echo [2/3] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ✗ 错误：未找到 Node.js
    echo.
    echo 解决方法：
    echo   安装 Node.js LTS 版本
    echo   下载地址：https://nodejs.org/
    echo.
    goto :error
)
node --version
echo ✓ Node.js 已安装
echo.

REM 检查 npm
echo [3/3] 检查 npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ✗ npm 不可用
    goto :error
)
npm --version
echo ✓ npm 已安装
echo.

REM ============================================================
REM 步骤 1: 安装 Python 依赖
REM ============================================================
echo ════════════════════════════════════════════════════════════
echo [步骤 1/5] 安装 Python 依赖
echo ════════════════════════════════════════════════════════════
echo.

cd backend
if errorlevel 1 (
    echo ✗ 无法进入 backend 目录
    goto :error
)

echo [1/3] 检查 PyInstaller...
"%PIP37_EXE%" show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller 5.13.2...
    "%PIP37_EXE%" install pyinstaller==5.13.2
    if errorlevel 1 (
        echo ✗ PyInstaller 安装失败
        cd ..
        goto :error
    )
) else (
    echo ✓ PyInstaller 已安装
)
echo.

echo [2/3] 检查 passlib 和 bcrypt（兼容性必需）...
"%PIP37_EXE%" show passlib >nul 2>&1
if errorlevel 1 (
    echo 正在安装 passlib[bcrypt]...
    "%PIP37_EXE%" install "passlib[bcrypt]"
    if errorlevel 1 (
        echo ⚠ passlib 安装失败，将影响 EXE 数据库兼容性
    )
) else (
    echo ✓ passlib 已安装
)

"%PIP37_EXE%" show bcrypt >nul 2>&1
if errorlevel 1 (
    echo 正在安装 bcrypt...
    "%PIP37_EXE%" install "bcrypt>=4.0.0,<5.0.0"
    if errorlevel 1 (
        echo ⚠ bcrypt 安装失败，将影响 EXE 数据库兼容性
    )
) else (
    echo ✓ bcrypt 已安装
)
echo.

echo [3/3] 安装其他依赖...
"%PIP37_EXE%" install -r requirements.txt
if errorlevel 1 (
    echo ⚠ 部分依赖安装失败，但继续执行
)
echo ✓ Python 依赖安装完成
echo.

REM ============================================================
REM 步骤 2: 构建前端
REM ============================================================
echo ════════════════════════════════════════════════════════════
echo [步骤 2/5] 构建前端
echo ════════════════════════════════════════════════════════════
echo.

cd ..\frontend
if errorlevel 1 (
    echo ✗ 无法进入 frontend 目录
    goto :error
)

echo [1/2] 检查前端依赖...
if not exist "node_modules" (
    echo 正在安装前端依赖（这可能需要几分钟）...
    call npm install
    if errorlevel 1 (
        echo ✗ 前端依赖安装失败
        cd ..
        goto :error
    )
) else (
    echo ✓ 前端依赖已安装
)
echo.

echo [2/2] 构建前端（这可能需要 1-2 分钟）...
set NODE_OPTIONS=--max-old-space-size=4096
call npm run build
if errorlevel 1 (
    echo ✗ 前端构建失败
    cd ..
    goto :error
)

if not exist "dist\index.html" (
    echo ✗ 前端构建失败：未找到 dist\index.html
    cd ..
    goto :error
)
echo ✓ 前端构建完成
echo.

REM ============================================================
REM 步骤 3: 打包后端
REM ============================================================
echo ════════════════════════════════════════════════════════════
echo [步骤 3/5] 打包后端
echo ════════════════════════════════════════════════════════════
echo.

cd ..\backend
if errorlevel 1 (
    echo ✗ 无法进入 backend 目录
    goto :error
)

echo [1/2] 清理旧文件...
if exist "build" (
    rmdir /s /q build
    echo   - 已删除 build 目录
)
if exist "dist" (
    rmdir /s /q dist
    echo   - 已删除 dist 目录
)
echo ✓ 清理完成
echo.

echo [2/2] 打包后端（这可能需要 2-3 分钟）...
echo   提示：请耐心等待，不要关闭窗口
echo.
"%PYINSTALLER37_EXE%" build_win7_compatible.spec --clean
if errorlevel 1 (
    echo.
    echo ✗ 后端打包失败
    echo.
    echo 常见原因：
    echo   1. 缺少依赖库
    echo   2. 磁盘空间不足
    echo   3. 杀毒软件拦截
    echo.
    cd ..
    goto :error
)

if not exist "dist\backend_server.exe" (
    echo ✗ 打包失败：未找到 backend_server.exe
    cd ..
    goto :error
)

REM 获取文件大小
for %%F in ("dist\backend_server.exe") do set EXE_SIZE=%%~zF
set /a EXE_SIZE_MB=!EXE_SIZE! / 1048576
echo ✓ 后端打包完成（大小：!EXE_SIZE_MB! MB）
echo.

REM ============================================================
REM 步骤 4: 整合文件
REM ============================================================
echo ════════════════════════════════════════════════════════════
echo [步骤 4/5] 整合文件
echo ════════════════════════════════════════════════════════════
echo.

cd ..

REM 创建输出目录
set OUTPUT_DIR=simple-web-package-win7-v2.1.7
if exist "%OUTPUT_DIR%" (
    echo [1/4] 清理旧的输出目录...
    rmdir /s /q "%OUTPUT_DIR%"
    if errorlevel 1 (
        echo ⚠ 无法删除旧目录，可能被占用
        set OUTPUT_DIR=simple-web-package-win7-v2.1.7-new
        echo   使用新目录名：!OUTPUT_DIR!
    )
)
mkdir "%OUTPUT_DIR%"
echo ✓ 创建输出目录：%OUTPUT_DIR%
echo.

echo [2/4] 复制后端程序...
copy "backend\dist\backend_server.exe" "%OUTPUT_DIR%\" >nul
if errorlevel 1 (
    echo ✗ 复制后端程序失败
    goto :error
)
echo ✓ backend_server.exe

echo [3/4] 复制前端文件...
xcopy "frontend\dist" "%OUTPUT_DIR%\frontend\" /E /I /Y /Q >nul
if errorlevel 1 (
    echo ✗ 复制前端文件失败
    goto :error
)
echo ✓ frontend/

echo [4/4] 复制数据库...
if exist "backend\database.db" (
    copy "backend\database.db" "%OUTPUT_DIR%\" >nul
    echo ✓ database.db
) else (
    echo ⚠ 未找到 database.db，将在首次启动时创建
)
echo.

REM ============================================================
REM 步骤 5: 创建说明文件
REM ============================================================
echo ════════════════════════════════════════════════════════════
echo [步骤 5/5] 创建说明文件
echo ════════════════════════════════════════════════════════════
echo.

REM 创建使用说明
(
echo ========================================
echo   眼科注射预约系统 - Windows 7 版本
echo   v2.1.7-win7-auto-migrate
echo ========================================
echo.
echo 使用方法：
echo 1. 双击 backend_server.exe 启动程序
echo 2. 程序会自动打开浏览器
echo 3. 默认账号：admin
echo 4. 默认密码：admin
echo.
echo 重要提示：
echo - ✅ 自动检测并升级数据库结构
echo - ✅ 自动迁移旧密码格式（bcrypt → PBKDF2）
echo - ✅ 旧密码统一重置为：admin
echo - ✅ 可以直接使用旧版本的 database.db
echo.
echo 数据库迁移（自动）：
echo - 直接复制旧版本的 database.db 到此目录
echo - 启动程序时会自动检测并升级
echo - 旧密码会自动重置为：admin
echo - 无需手动操作
echo.
echo 系统要求：
echo - Windows 7 SP1 或更高版本
echo - 64 位操作系统
echo - 至少 2GB 内存
echo.
echo 故障排除：
echo 1. 如果无法启动，请安装 VC++ 运行库
echo    下载：https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
echo 2. 如果浏览器未自动打开，请手动访问：
echo    http://127.0.0.1:8000
echo.
echo 3. 如果端口被占用，请关闭其他占用 8000 端口的程序
echo.
echo 4. 如果杀毒软件报警，请添加信任（本程序安全无毒）
echo.
echo 技术信息：
echo - 版本：v2.1.7-win7-auto-migrate
echo - 打包日期：%date% %time%
echo - Python 版本：3.7.9
echo - 密码格式：PBKDF2（自动迁移）
echo.
) > "%OUTPUT_DIR%\使用说明.txt"

REM 创建调试启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ════════════════════════════════════════════════════════════
echo echo   眼科注射预约系统 - 调试模式
echo echo   v2.1.7-win7-auto-migrate
echo echo ════════════════════════════════════════════════════════════
echo echo.
echo echo 正在启动程序...
echo echo 如果出现错误，请截图发送给技术支持
echo echo.
echo echo ════════════════════════════════════════════════════════════
echo echo.
echo.
echo backend_server.exe
echo.
echo echo.
echo echo ════════════════════════════════════════════════════════════
echo echo 程序已停止
echo echo ════════════════════════════════════════════════════════════
echo echo.
echo echo 如果程序无法启动，请检查：
echo echo 1. 是否安装了 VC++ 运行库
echo echo 2. 端口 8000 是否被占用
echo echo 3. frontend 文件夹是否完整
echo echo 4. database.db 文件是否存在
echo echo.
echo pause
) > "%OUTPUT_DIR%\启动并查看错误.bat"

echo ✓ 使用说明.txt
echo ✓ 启动并查看错误.bat
echo.

REM ============================================================
REM 完成
REM ============================================================
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                  ✅ 打包完成！                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 输出目录：%OUTPUT_DIR%\
echo.
echo 📄 文件列表：
dir /B "%OUTPUT_DIR%"
echo.
echo 📊 文件大小：
for %%F in ("%OUTPUT_DIR%\backend_server.exe") do (
    set /a SIZE_MB=%%~zF / 1048576
    echo    backend_server.exe: !SIZE_MB! MB
)
for %%F in ("%OUTPUT_DIR%\database.db") do (
    set /a SIZE_KB=%%~zF / 1024
    echo    database.db: !SIZE_KB! KB
)
echo.
echo 🎉 可以将 %OUTPUT_DIR% 文件夹打包发送给客户了！
echo.
echo 📋 下一步：
echo 1. 测试：双击 %OUTPUT_DIR%\backend_server.exe
echo 2. 登录：使用 admin/admin 登录
echo 3. 验证：测试自动迁移功能（复制旧 database.db 测试）
echo 4. 打包：将整个文件夹压缩为 ZIP
echo 5. 发送：发送给客户
echo.
echo [%time%] 打包流程完成
echo.
pause
exit /b 0

:error
echo.
echo ════════════════════════════════════════════════════════════
echo ✗ 打包失败
echo ════════════════════════════════════════════════════════════
echo.
echo 请检查上面的错误信息，解决问题后重新运行
echo.
echo 常见问题：
echo 1. Python 3.7 路径不正确 → 修改脚本第 11 行
echo 2. 缺少依赖库 → 运行 pip install -r requirements.txt
echo 3. Node.js 未安装 → 从 https://nodejs.org/ 下载安装
echo 4. 磁盘空间不足 → 清理磁盘空间
echo 5. 杀毒软件拦截 → 临时关闭杀毒软件
echo.
echo [%time%] 打包流程失败
echo.
pause
exit /b 1
