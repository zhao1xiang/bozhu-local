@echo off
chcp 65001 >nul
echo ========================================
echo   Web 版本打包工具 v2.1.6
echo   Windows 7 兼容版本
echo ========================================
echo.

REM 设置 Python 3.7 路径（请根据实际情况修改）
set PYTHON37_PATH=D:\workpath\python3.7.9
set PYTHON37_EXE=%PYTHON37_PATH%\python.exe
set PIP37_EXE=%PYTHON37_PATH%\Scripts\pip.exe
set PYINSTALLER37_EXE=%PYTHON37_PATH%\Scripts\pyinstaller.exe

echo [检查环境]
echo.

REM 检查 Python 3.7
echo 检查 Python 3.7...
if not exist "%PYTHON37_EXE%" (
    echo ✗ 未找到 Python 3.7: %PYTHON37_EXE%
    echo.
    echo 请安装 Python 3.7.9 或修改脚本中的路径
    echo 下载地址: https://www.python.org/downloads/release/python-379/
    pause
    exit /b 1
)
"%PYTHON37_EXE%" --version
echo ✓ Python 3.7 已安装
echo.

REM 检查 Node.js
echo 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未找到 Node.js
    echo 请安装 Node.js LTS 版本
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo ✓ Node.js 已安装
echo.

REM 检查 npm
echo 检查 npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未找到 npm
    pause
    exit /b 1
)
npm --version
echo ✓ npm 已安装
echo.

echo ========================================
echo [1/5] 安装 Python 依赖
echo ========================================
echo.

cd backend

REM 检查并安装 PyInstaller
echo 检查 PyInstaller...
"%PIP37_EXE%" show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    "%PIP37_EXE%" install pyinstaller==5.13.2
) else (
    echo ✓ PyInstaller 已安装
)

REM 检查并安装其他依赖
echo.
echo 检查其他依赖...
"%PIP37_EXE%" install -r requirements.txt
echo ✓ Python 依赖安装完成
echo.

echo ========================================
echo [2/5] 构建前端
echo ========================================
echo.

cd ..\frontend

REM 检查 node_modules
if not exist "node_modules" (
    echo 正在安装前端依赖...
    call npm install
) else (
    echo ✓ 前端依赖已安装
)

echo.
echo 正在构建前端...
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

echo ========================================
echo [3/5] 打包后端
echo ========================================
echo.

cd ..\backend

echo 正在清理旧文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo ✓ 清理完成
echo.

echo 正在打包后端（这可能需要 1-2 分钟）...
"%PYINSTALLER37_EXE%" build_win7_compatible.spec --clean

if not exist "dist\backend_server.exe" (
    echo ✗ 后端打包失败
    cd ..
    pause
    exit /b 1
)
echo ✓ 后端打包完成
echo.

echo ========================================
echo [4/5] 整合文件
echo ========================================
echo.

cd ..

REM 创建输出目录
set OUTPUT_DIR=simple-web-package-win7-final
if exist "%OUTPUT_DIR%" (
    echo 正在清理旧的输出目录...
    rmdir /s /q "%OUTPUT_DIR%"
)
mkdir "%OUTPUT_DIR%"
echo ✓ 创建输出目录: %OUTPUT_DIR%
echo.

echo 正在复制文件...
echo - 复制后端程序...
copy "backend\dist\backend_server.exe" "%OUTPUT_DIR%\" >nul
echo - 复制前端文件...
xcopy "frontend\dist" "%OUTPUT_DIR%\frontend\" /E /I /Y >nul
echo - 复制数据库...
copy "backend\database.db" "%OUTPUT_DIR%\" >nul
echo ✓ 文件复制完成
echo.

echo ========================================
echo [5/5] 创建说明文件
echo ========================================
echo.

REM 创建使用说明
(
echo ========================================
echo   眼科注射预约系统 - Windows 7 版本
echo   最终版 v2.1.6
echo ========================================
echo.
echo 使用方法：
echo 1. 双击 backend_server.exe 启动程序
echo 2. 程序会自动打开浏览器
echo 3. 默认账号：admin
echo 4. 默认密码：admin123
echo.
echo 重要提示：
echo - 完全兼容 EXE 版本的数据库
echo - 可以直接使用旧版本的 database.db
echo - 旧密码格式自动兼容
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
echo 技术信息：
echo - 版本：v2.1.6-win7-final
echo - 打包日期：%date% %time%
echo - Python 版本：3.7.9
echo - 兼容性：完全兼容 EXE 版本数据库
echo.
) > "%OUTPUT_DIR%\使用说明.txt"

REM 创建启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo   眼科注射预约系统 - 调试模式
echo echo   v2.1.6-win7-final
echo echo ========================================
echo echo.
echo echo 正在启动程序...
echo echo 如果出现错误，请截图发送给技术支持
echo echo.
echo echo ========================================
echo echo.
echo.
echo backend_server.exe
echo.
echo echo.
echo echo ========================================
echo echo 程序已停止
echo echo ========================================
echo echo.
echo echo 如果程序无法启动，请检查：
echo echo 1. 是否安装了 VC++ 运行库
echo echo 2. 端口 8000 是否被占用
echo echo 3. frontend 文件夹是否完整
echo echo.
echo pause
) > "%OUTPUT_DIR%\启动并查看错误.bat"

echo ✓ 说明文件创建完成
echo.

echo ========================================
echo   ✅ 打包完成！
echo ========================================
echo.
echo 📦 输出目录：%OUTPUT_DIR%\
echo.
echo 📄 文件列表：
dir /B "%OUTPUT_DIR%"
echo.
echo 📊 文件大小：
for %%F in ("%OUTPUT_DIR%\backend_server.exe") do echo    backend_server.exe: %%~zF 字节
for %%F in ("%OUTPUT_DIR%\database.db") do echo    database.db: %%~zF 字节
echo.
echo 🎉 可以将 %OUTPUT_DIR% 文件夹打包发送给客户了！
echo.
echo 📋 下一步：
echo 1. 测试：双击 %OUTPUT_DIR%\backend_server.exe
echo 2. 验证：确认浏览器能正常打开并登录
echo 3. 打包：将整个文件夹压缩为 ZIP
echo 4. 发送：发送给客户
echo.
pause
