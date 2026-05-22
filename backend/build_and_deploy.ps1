# 打包和部署脚本
# 用法: .\build_and_deploy.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "眼科注射预约系统 - 打包和部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查 PyInstaller 是否安装
Write-Host "`n检查 PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstaller = pyinstaller --version
    Write-Host "✓ PyInstaller 已安装: $pyinstaller" -ForegroundColor Green
} catch {
    Write-Host "✗ PyInstaller 未安装，请先安装: pip install pyinstaller" -ForegroundColor Red
    exit 1
}

# 清理旧的构建文件
Write-Host "`n清理旧的构建文件..." -ForegroundColor Yellow
foreach ($dir in @("build", "dist", "bozhu-client-win")) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
        Write-Host "✓ 已删除 $dir 目录" -ForegroundColor Green
    }
}

# 开始打包
Write-Host "`n开始打包..." -ForegroundColor Yellow
pyinstaller build_web_server.spec

# 检查打包是否成功
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ 打包成功！" -ForegroundColor Green
    
    # 创建发布目录
    Write-Host "`n创建发布目录..." -ForegroundColor Yellow
    $releaseDir = "bozhu-client-win"
    New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
    Write-Host "✓ 已创建目录: $releaseDir" -ForegroundColor Green
    
    # 复制 exe 文件
    Write-Host "`n复制 exe 文件..." -ForegroundColor Yellow
    $exeSource = "dist\backend_server\backend_server.exe"
    $exeDest = "$releaseDir\backend_server.exe"
    
    if (Test-Path $exeSource) {
        Copy-Item $exeSource $exeDest
        Write-Host "✓ 已复制 exe: $exeDest" -ForegroundColor Green
    } else {
        Write-Host "✗ exe 文件不存在: $exeSource" -ForegroundColor Red
        exit 1
    }
    
    # 复制前端文件
    Write-Host "`n复制前端文件..." -ForegroundColor Yellow
    $frontendSource = "..\frontend\dist"
    $frontendDest = "$releaseDir\frontend"
    
    if (Test-Path $frontendSource) {
        if (Test-Path $frontendDest) {
            Remove-Item -Recurse -Force $frontendDest
        }
        Copy-Item -Recurse $frontendSource $frontendDest
        Write-Host "✓ 前端文件已复制到: $frontendDest" -ForegroundColor Green
    } else {
        Write-Host "✗ 前端文件不存在: $frontendSource" -ForegroundColor Red
        exit 1
    }
    
    # 复制数据库文件（如果存在）
    Write-Host "`n复制数据库文件..." -ForegroundColor Yellow
    if (Test-Path "database.db") {
        Copy-Item "database.db" "$releaseDir\database.db"
        Write-Host "✓ 数据库已复制到: $releaseDir\database.db" -ForegroundColor Green
    } else {
        Write-Host "⚠ 数据库文件不存在（首次运行时会自动创建）" -ForegroundColor Yellow
    }
    
    # 显示最终目录结构
    Write-Host "`n最终目录结构:" -ForegroundColor Yellow
    Get-ChildItem $releaseDir -Recurse | ForEach-Object {
        $indent = "  " * ($_.FullName.Split('\').Count - (Get-Item $releaseDir).FullName.Split('\').Count)
        if ($_.PSIsContainer) {
            Write-Host "$indent📁 $($_.Name)/" -ForegroundColor Cyan
        } else {
            Write-Host "$indent📄 $($_.Name)" -ForegroundColor White
        }
    }
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "打包完成！" -ForegroundColor Green
    Write-Host "发布目录: $releaseDir" -ForegroundColor Green
    Write-Host "  ├── backend_server.exe" -ForegroundColor Green
    Write-Host "  ├── frontend/" -ForegroundColor Green
    Write-Host "  └── database.db (可选)" -ForegroundColor Green
    Write-Host "`n使用方法:" -ForegroundColor Green
    Write-Host "  1. 进入 $releaseDir 目录" -ForegroundColor Green
    Write-Host "  2. 双击 backend_server.exe 运行" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "`n✗ 打包失败！" -ForegroundColor Red
    exit 1
}
