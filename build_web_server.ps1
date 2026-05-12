# 眼科注射预约系统 Web版 构建脚本
# 用于构建前端和后端，生成完整的Web服务器版本

param(
    [switch]$SkipFrontend = $false,
    [switch]$SkipBackend = $false,
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Yellow
    Write-Host "  $Message" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Yellow
}

# 主程序
Write-Section "眼科注射预约系统 Web版 构建脚本"

# 检查必要的工具
Write-Info "检查必要的工具..."
$tools = @("node", "npm", "python")
foreach ($tool in $tools) {
    try {
        $version = & $tool --version 2>&1
        Write-Success "$tool 已安装: $version"
    }
    catch {
        Write-Error-Custom "$tool 未安装，请先安装"
        exit 1
    }
}

# 清理旧的构建文件
if ($Clean) {
    Write-Section "清理旧的构建文件"
    
    if (Test-Path "frontend/dist") {
        Write-Info "删除 frontend/dist..."
        Remove-Item -Path "frontend/dist" -Recurse -Force
        Write-Success "frontend/dist 已删除"
    }
    
    if (Test-Path "backend/dist") {
        Write-Info "删除 backend/dist..."
        Remove-Item -Path "backend/dist" -Recurse -Force
        Write-Success "backend/dist 已删除"
    }
}

# 构建前端
if (-not $SkipFrontend) {
    Write-Section "构建前端"
    
    if (-not (Test-Path "frontend")) {
        Write-Error-Custom "frontend 目录不存在"
        exit 1
    }
    
    Write-Info "进入 frontend 目录..."
    Push-Location frontend
    
    try {
        Write-Info "安装依赖..."
        & npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install 失败"
        }
        Write-Success "依赖安装完成"
        
        Write-Info "构建前端..."
        & npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "npm run build 失败"
        }
        Write-Success "前端构建完成"
        
        # 检查dist目录
        if (-not (Test-Path "dist")) {
            throw "dist 目录未生成"
        }
        Write-Success "dist 目录已生成"
        
    }
    finally {
        Pop-Location
    }
}

# 复制前端文件到backend/frontend
Write-Section "复制前端文件到后端"

if (-not (Test-Path "backend/frontend")) {
    Write-Info "创建 backend/frontend 目录..."
    New-Item -ItemType Directory -Path "backend/frontend" -Force | Out-Null
}

Write-Info "清空 backend/frontend 目录（保留 .exe 文件）..."
Get-ChildItem "backend/frontend" -Exclude "*.exe" -Force -ErrorAction SilentlyContinue | 
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Info "复制前端文件..."
Copy-Item -Path "frontend/dist/*" -Destination "backend/frontend" -Recurse -Force
Write-Success "前端文件已复制"

# 验证复制结果
$fileCount = (Get-ChildItem "backend/frontend" -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Success "backend/frontend 目录包含 $fileCount 个文件"

# 构建后端
if (-not $SkipBackend) {
    Write-Section "构建后端"
    
    if (-not (Test-Path "backend")) {
        Write-Error-Custom "backend 目录不存在"
        exit 1
    }
    
    Push-Location backend
    
    try {
        Write-Info "检查 Python 虚拟环境..."
        if (-not (Test-Path ".venv")) {
            Write-Info "创建虚拟环境..."
            & python -m venv .venv
            Write-Success "虚拟环境已创建"
        }
        
        Write-Info "激活虚拟环境..."
        & .\.venv\Scripts\Activate.ps1
        
        Write-Info "安装 Python 依赖..."
        & pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "pip install 失败"
        }
        Write-Success "Python 依赖安装完成"
        
        Write-Info "检查数据库..."
        if (-not (Test-Path "database.db")) {
            Write-Info "数据库不存在，将在首次启动时创建"
        }
        else {
            Write-Success "数据库已存在"
        }
        
    }
    finally {
        Pop-Location
    }
}

# 生成构建报告
Write-Section "构建完成"

Write-Success "前端构建文件位置: frontend/dist"
Write-Success "后端文件位置: backend"
Write-Success "前端文件已复制到: backend/frontend"

Write-Info ""
Write-Info "后续步骤:"
Write-Info "1. 启动服务器: python backend/web_server.py"
Write-Info "2. 访问应用: http://localhost:8000"
Write-Info "3. 默认用户: admin / admin123"

Write-Info ""
Write-Info "构建脚本执行完成！"
