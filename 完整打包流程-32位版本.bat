@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   完整打包流程 - 32位版本 v2.1.2
echo ========================================
echo.
echo 此脚本将完成以下步骤：
echo 1. 检查并安装32位Rust工具链
echo 2. 构建32位后端（PyInstaller）
echo 3. 构建前端（Vite）
echo 4. 构建32位Tauri应用
echo 5. 复制必要文件到发布目录
echo 6. 创建32位版本的升级包
echo.
pause

REM ==================== 步骤1：检查32位Rust工具链 ====================
echo.
echo [步骤 1/6] 检查32位Rust工具链...
echo ----------------------------------------
rustup target list | findstr /C:"i686-pc-windows-msvc (installed)" >nul
if errorlevel 1 (
    echo ⚠ 未安装32位Rust工具链，正在安装...
    rustup target add i686-pc-windows-msvc
    if errorlevel 1 (
        echo ✗ 安装失败！
        pause
        exit /b 1
    )
    echo ✓ 32位Rust工具链安装成功
) else (
    echo ✓ 32位Rust工具链已安装
)

REM ==================== 步骤2：构建32位后端 ====================
echo.
echo [步骤 2/6] 构建32位后端...
echo ----------------------------------------

REM 检查32位Python
set PYTHON32=C:\Python311-32\python.exe
if not exist "%PYTHON32%" (
    echo ⚠ 未找到32位Python: %PYTHON32%
    echo 使用默认Python（可能是64位）
    set PYTHON32=python
)
echo 使用Python: %PYTHON32%

REM 清理旧的构建
if exist "backend\dist" (
    echo 清理旧的后端构建...
    rmdir /s /q "backend\dist"
)
if exist "backend\build" (
    rmdir /s /q "backend\build"
)

REM 构建后端
cd backend
echo 正在使用PyInstaller构建后端...
"%PYTHON32%" -m PyInstaller build_backend.spec --clean
if errorlevel 1 (
    echo ✗ 后端构建失败！
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✓ 后端构建完成

REM ==================== 步骤3：构建前端 ====================
echo.
echo [步骤 3/6] 构建前端...
echo ----------------------------------------
cd frontend

REM 清理旧的构建
if exist "dist" (
    echo 清理旧的前端构建...
    rmdir /s /q "dist"
)

echo 正在使用Vite构建前端...
call npm run build
if errorlevel 1 (
    echo ✗ 前端构建失败！
    cd ..
    pause
    exit /b 1
)
echo ✓ 前端构建完成

REM ==================== 步骤4：构建32位Tauri应用 ====================
echo.
echo [步骤 4/6] 构建32位Tauri应用...
echo ----------------------------------------

REM 清理旧的Tauri构建
if exist "src-tauri\target\i686-pc-windows-msvc\release" (
    echo 清理旧的Tauri构建...
    rmdir /s /q "src-tauri\target\i686-pc-windows-msvc\release"
)

echo 正在构建32位Tauri应用（这可能需要几分钟）...
call npm run tauri build -- --target i686-pc-windows-msvc
if errorlevel 1 (
    echo ✗ Tauri构建失败！
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✓ Tauri应用构建完成

REM ==================== 步骤5：复制文件到发布目录 ====================
echo.
echo [步骤 5/6] 复制文件到发布目录...
echo ----------------------------------------

REM 创建32位发布目录
set DIST_DIR=dist-package-32bit
if exist "%DIST_DIR%" (
    echo 清理旧的发布目录...
    rmdir /s /q "%DIST_DIR%"
)
mkdir "%DIST_DIR%"

REM 复制EXE文件
echo 复制32位EXE文件...
copy "frontend\src-tauri\target\i686-pc-windows-msvc\release\眼科注射预约系统.exe" "%DIST_DIR%\" >nul
if errorlevel 1 (
    echo ✗ 复制EXE失败！
    pause
    exit /b 1
)

REM 复制后端
echo 复制后端文件...
xcopy "backend\dist\*" "%DIST_DIR%\" /E /I /Y >nul

REM 复制数据库（如果存在）
if exist "backend\database.db" (
    echo 复制数据库文件...
    copy "backend\database.db" "%DIST_DIR%\" >nul
)

REM 创建logs目录
mkdir "%DIST_DIR%\logs" 2>nul

echo ✓ 文件复制完成

REM ==================== 步骤6：创建升级包 ====================
echo.
echo [步骤 6/6] 创建32位升级包...
echo ----------------------------------------

REM 创建升级说明
echo 创建升级说明文件...
(
echo ========================================
echo   眼科注射预约系统 v2.1.2 - 32位版本
echo ========================================
echo.
echo 【重要提示】
echo 此为32位版本，仅适用于32位Windows系统
echo.
echo 【系统要求】
echo - Windows 7 SP1 32位或更高版本
echo - 需要安装32位WebView2 Runtime
echo - 至少2GB可用内存
echo.
echo 【升级步骤】
echo.
echo 1. 关闭正在运行的系统
echo    - 右键任务栏图标，选择"退出"
echo    - 或在任务管理器中结束进程
echo.
echo 2. 备份数据（重要！）
echo    - 复制 database.db 文件到安全位置
echo.
echo 3. 替换文件
echo    - 将本升级包中的所有文件复制到安装目录
echo    - 选择"替换目标中的文件"
echo.
echo 4. 启动系统
echo    - 双击"眼科注射预约系统.exe"
echo    - 系统会自动升级数据库结构
echo.
echo 【新增功能】
echo - 自动数据库升级
echo - 优化打印功能
echo - 修复预约流程
echo - 优化Dashboard显示
echo.
echo 【注意事项】
echo - 首次启动可能需要较长时间（数据库升级）
echo - 如遇到问题，请使用备份的数据库文件恢复
echo - 32位版本性能可能不如64位版本
echo.
echo 【技术支持】
echo 如有问题，请联系技术支持
echo.
echo ========================================
) > "%DIST_DIR%\升级说明_v2.1.2_32位.txt"

REM 创建WebView2安装说明
(
echo ========================================
echo   WebView2 Runtime 安装说明 - 32位
echo ========================================
echo.
echo 32位系统需要安装32位的WebView2 Runtime
echo.
echo 【下载地址】
echo https://go.microsoft.com/fwlink/p/?LinkId=2124703
echo.
echo 【安装步骤】
echo 1. 点击上述链接下载安装程序
echo 2. 选择"x86"（32位）版本
echo 3. 运行安装程序
echo 4. 等待安装完成
echo 5. 重启应用
echo.
echo ========================================
) > "%DIST_DIR%\WebView2安装说明_32位.txt"

echo ✓ 升级包创建完成

REM ==================== 完成 ====================
echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 32位版本位置：%DIST_DIR%\
echo.
echo 文件列表：
dir /b "%DIST_DIR%"
echo.
echo 文件大小：
for /f "tokens=3" %%a in ('dir "%DIST_DIR%\眼科注射预约系统.exe" ^| findstr "眼科"') do set SIZE=%%a
echo EXE文件：%SIZE% 字节
echo.
echo 【重要提示】
echo 1. 此为32位版本，仅适用于32位Windows系统
echo 2. 客户需要安装32位WebView2 Runtime
echo 3. 建议在32位虚拟机中测试后再发布
echo 4. 性能可能不如64位版本
echo.
echo 【下一步】
echo 1. 在32位系统中测试
echo 2. 验证所有功能正常
echo 3. 打包成ZIP发送给客户
echo.
pause
