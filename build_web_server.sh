#!/bin/bash

# 眼科注射预约系统 Web版 构建脚本
# 用于构建前端和后端，生成完整的Web服务器版本

set -e

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 输出函数
write_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

write_error() {
    echo -e "${RED}✗ $1${NC}"
}

write_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

write_section() {
    echo ""
    echo -e "${YELLOW}============================================================${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}============================================================${NC}"
}

# 解析命令行参数
SKIP_FRONTEND=false
SKIP_BACKEND=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 主程序
write_section "眼科注射预约系统 Web版 构建脚本"

# 检查必要的工具
write_info "检查必要的工具..."
for tool in node npm python3; do
    if command -v $tool &> /dev/null; then
        version=$($tool --version 2>&1)
        write_success "$tool 已安装: $version"
    else
        write_error "$tool 未安装，请先安装"
        exit 1
    fi
done

# 清理旧的构建文件
if [ "$CLEAN" = true ]; then
    write_section "清理旧的构建文件"
    
    if [ -d "frontend/dist" ]; then
        write_info "删除 frontend/dist..."
        rm -rf frontend/dist
        write_success "frontend/dist 已删除"
    fi
    
    if [ -d "backend/dist" ]; then
        write_info "删除 backend/dist..."
        rm -rf backend/dist
        write_success "backend/dist 已删除"
    fi
fi

# 构建前端
if [ "$SKIP_FRONTEND" = false ]; then
    write_section "构建前端"
    
    if [ ! -d "frontend" ]; then
        write_error "frontend 目录不存在"
        exit 1
    fi
    
    write_info "进入 frontend 目录..."
    cd frontend
    
    write_info "安装依赖..."
    npm install
    write_success "依赖安装完成"
    
    write_info "构建前端..."
    npm run build
    write_success "前端构建完成"
    
    # 检查dist目录
    if [ ! -d "dist" ]; then
        write_error "dist 目录未生成"
        exit 1
    fi
    write_success "dist 目录已生成"
    
    cd ..
fi

# 复制前端文件到backend/frontend
write_section "复制前端文件到后端"

if [ ! -d "backend/frontend" ]; then
    write_info "创建 backend/frontend 目录..."
    mkdir -p backend/frontend
fi

write_info "清空 backend/frontend 目录（保留 .exe 文件）..."
find backend/frontend -type f ! -name "*.exe" -delete
find backend/frontend -type d -empty -delete

write_info "复制前端文件..."
cp -r frontend/dist/* backend/frontend/
write_success "前端文件已复制"

# 验证复制结果
file_count=$(find backend/frontend -type f | wc -l)
write_success "backend/frontend 目录包含 $file_count 个文件"

# 构建后端
if [ "$SKIP_BACKEND" = false ]; then
    write_section "构建后端"
    
    if [ ! -d "backend" ]; then
        write_error "backend 目录不存在"
        exit 1
    fi
    
    cd backend
    
    write_info "检查 Python 虚拟环境..."
    if [ ! -d ".venv" ]; then
        write_info "创建虚拟环境..."
        python3 -m venv .venv
        write_success "虚拟环境已创建"
    fi
    
    write_info "激活虚拟环境..."
    source .venv/bin/activate
    
    write_info "安装 Python 依赖..."
    pip install -r requirements.txt
    write_success "Python 依赖安装完成"
    
    write_info "检查数据库..."
    if [ ! -f "database.db" ]; then
        write_info "数据库不存在，将在首次启动时创建"
    else
        write_success "数据库已存在"
    fi
    
    cd ..
fi

# 生成构建报告
write_section "构建完成"

write_success "前端构建文件位置: frontend/dist"
write_success "后端文件位置: backend"
write_success "前端文件已复制到: backend/frontend"

write_info ""
write_info "后续步骤:"
write_info "1. 启动服务器: python backend/web_server.py"
write_info "2. 访问应用: http://localhost:8000"
write_info "3. 默认用户: admin / admin123"

write_info ""
write_info "构建脚本执行完成！"
