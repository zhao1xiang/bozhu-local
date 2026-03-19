@echo off
chcp 65001 >nul
echo ============================================================
echo  HIS 同步服务打包
echo ============================================================

cd /d %~dp0

D:\workpath\python3.7.9\Scripts\pyinstaller.exe ^
    --distpath ..\his-sync-package ^
    --workpath ..\temp-build ^
    build_his_sync.spec

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 打包失败！
    pause
    exit /b 1
)

echo.
echo [OK] 打包成功！
echo.
echo 正在复制配置文件...
if not exist "..\his-sync-package\his_sync\config" mkdir "..\his-sync-package\his_sync\config"
if not exist "..\his-sync-package\his_sync\state" mkdir "..\his-sync-package\his_sync\state"
if not exist "..\his-sync-package\his_sync\logs" mkdir "..\his-sync-package\his_sync\logs"

copy /y "config\config.yaml" "..\his-sync-package\his_sync\config\config.yaml"
copy /y "state\sync_state.json" "..\his-sync-package\his_sync\state\sync_state.json"

echo.
echo ============================================================
echo  打包完成！输出目录: his-sync-package\his_sync\
echo  使用前请编辑 config\config.yaml 配置数据库连接
echo ============================================================
pause
