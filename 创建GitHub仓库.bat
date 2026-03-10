@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo 创建干净的GitHub仓库
echo ==========================================
echo.

REM 设置目标目录
set TARGET_DIR=bozhu_github
set SOURCE_DIR=%CD%

REM 检查目标目录是否存在
if exist "%TARGET_DIR%" (
    echo 警告: %TARGET_DIR% 目录已存在
    set /p CONFIRM="是否删除并重新创建? (y/n): "
    if /i "!CONFIRM!"=="y" (
        echo 删除旧目录...
        rmdir /s /q "%TARGET_DIR%"
    ) else (
        echo 操作已取消
        pause
        exit /b
    )
)

echo.
echo 创建目标目录...
mkdir "%TARGET_DIR%"

echo.
echo ==========================================
echo 复制必需文件...
echo ==========================================

REM 复制后端代码
echo [1/10] 复制后端模型...
xcopy /E /I /Y "%SOURCE_DIR%\backend\models" "%TARGET_DIR%\backend\models" >nul

echo [2/10] 复制后端路由...
xcopy /E /I /Y "%SOURCE_DIR%\backend\routers" "%TARGET_DIR%\backend\routers" >nul

echo [3/10] 复制后端核心文件...
copy /Y "%SOURCE_DIR%\backend\database.py" "%TARGET_DIR%\backend\" >nul
copy /Y "%SOURCE_DIR%\backend\security.py" "%TARGET_DIR%\backend\" >nul
copy /Y "%SOURCE_DIR%\backend\main.py" "%TARGET_DIR%\backend\" >nul
copy /Y "%SOURCE_DIR%\backend\simple_web_server.py" "%TARGET_DIR%\backend\" >nul
copy /Y "%SOURCE_DIR%\backend\requirements.txt" "%TARGET_DIR%\backend\" >nul
copy /Y "%SOURCE_DIR%\backend\build_mac.spec" "%TARGET_DIR%\backend\" >nul

REM 复制前端代码
echo [4/10] 复制前端源码...
xcopy /E /I /Y "%SOURCE_DIR%\frontend\src" "%TARGET_DIR%\frontend\src" >nul

echo [5/10] 复制前端公共文件...
xcopy /E /I /Y "%SOURCE_DIR%\frontend\public" "%TARGET_DIR%\frontend\public" >nul

echo [6/10] 复制前端配置文件...
copy /Y "%SOURCE_DIR%\frontend\package.json" "%TARGET_DIR%\frontend\" >nul
copy /Y "%SOURCE_DIR%\frontend\tsconfig.json" "%TARGET_DIR%\frontend\" >nul
copy /Y "%SOURCE_DIR%\frontend\vite.config.ts" "%TARGET_DIR%\frontend\" >nul
copy /Y "%SOURCE_DIR%\frontend\index.html" "%TARGET_DIR%\frontend\" >nul
if exist "%SOURCE_DIR%\frontend\tsconfig.node.json" copy /Y "%SOURCE_DIR%\frontend\tsconfig.node.json" "%TARGET_DIR%\frontend\" >nul

REM 复制GitHub Actions配置
echo [7/10] 复制GitHub Actions配置...
mkdir "%TARGET_DIR%\.github\workflows"
copy /Y "%SOURCE_DIR%\.github\workflows\build-mac.yml" "%TARGET_DIR%\.github\workflows\" >nul

REM 复制配置文件
echo [8/10] 复制配置文件...
copy /Y "%SOURCE_DIR%\.gitignore" "%TARGET_DIR%\" >nul
copy /Y "%SOURCE_DIR%\README.md" "%TARGET_DIR%\" >nul

REM 复制文档
echo [9/10] 复制文档...
copy /Y "%SOURCE_DIR%\快速开始-GitHub自动打包.md" "%TARGET_DIR%\" >nul
if exist "%SOURCE_DIR%\GitHub-Actions自动打包说明.md" copy /Y "%SOURCE_DIR%\GitHub-Actions自动打包说明.md" "%TARGET_DIR%\" >nul
if exist "%SOURCE_DIR%\Mac打包教程.md" copy /Y "%SOURCE_DIR%\Mac打包教程.md" "%TARGET_DIR%\" >nul

REM 创建README
echo [10/10] 创建README...
(
echo # 玻注预约系统
echo.
echo 眼科玻璃体腔注射预约管理系统
echo.
echo ## 功能特点
echo.
echo - 患者信息管理
echo - 预约管理
echo - 打印功能
echo - 随访管理
echo - 数据统计
echo.
echo ## 技术栈
echo.
echo - 后端: Python + FastAPI + SQLModel
echo - 前端: React + TypeScript + Ant Design
echo - 数据库: SQLite
echo.
echo ## 快速开始
echo.
echo ### 开发环境
echo.
echo 1. 安装依赖
echo ```bash
echo # 后端
echo cd backend
echo pip install -r requirements.txt
echo.
echo # 前端
echo cd frontend
echo npm install
echo ```
echo.
echo 2. 运行开发服务器
echo ```bash
echo # 后端
echo cd backend
echo python main.py
echo.
echo # 前端
echo cd frontend
echo npm run dev
echo ```
echo.
echo ### Mac版本打包
echo.
echo 本项目支持使用GitHub Actions自动打包Mac版本，无需Mac电脑。
echo.
echo 详见: [快速开始-GitHub自动打包.md](./快速开始-GitHub自动打包.md^)
echo.
echo ## 文档
echo.
echo - [快速开始-GitHub自动打包.md](./快速开始-GitHub自动打包.md^) - GitHub Actions使用指南
echo - [Mac打包教程.md](./Mac打包教程.md^) - 本地打包教程
echo.
echo ## 许可证
echo.
echo 本项目仅供内部使用
) > "%TARGET_DIR%\README.md"

echo.
echo ==========================================
echo 初始化Git仓库...
echo ==========================================

cd "%TARGET_DIR%"
git init
git add .
git commit -m "Initial commit: 玻注预约系统"

echo.
echo ==========================================
echo 完成！
echo ==========================================
echo.
echo 干净的GitHub仓库已创建在: %TARGET_DIR%
echo.
echo 下一步操作:
echo 1. 在GitHub上创建新仓库
echo 2. 执行以下命令推送代码:
echo.
echo    cd %TARGET_DIR%
echo    git remote add origin https://github.com/^<your-username^>/bozhu_local.git
echo    git push -u origin master
echo.
echo 3. 在GitHub Actions中触发Mac版本打包
echo.
pause
