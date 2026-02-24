#!/bin/bash
# 眼科注射预约系统 - 后端服务启动脚本
# 适用于阿里云 Linux 服务器
# 端口: 8031
# 域名: local-show.microcall.com.cn

set -e

# 配置参数
APP_NAME="bozhu-backend"
APP_VERSION="2.1.1"
BACKEND_PORT="8031"
WORK_DIR="/work/local-show"
BACKEND_DIR="$WORK_DIR/backend"
LOG_DIR="$BACKEND_DIR/logs"
PID_FILE="$BACKEND_DIR/backend.pid"
LOG_FILE="$LOG_DIR/backend.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以 root 运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "此脚本需要 root 权限运行"
        print_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    # 检查 Python3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_info "✓ Python3: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        print_info "✓ Python: $PYTHON_VERSION"
    else
        print_error "未找到 Python，请先安装 Python3"
        exit 1
    fi
    
    # 检查 pip
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        print_info "✓ pip3 已安装"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        print_info "✓ pip 已安装"
    else
        print_warn "未找到 pip，尝试安装..."
        if [[ -f /etc/redhat-release ]]; then
            yum install -y python3-pip
        else
            apt-get update && apt-get install -y python3-pip
        fi
        PIP_CMD="pip3"
    fi
    
    # 检查端口占用
    if netstat -tuln | grep ":$BACKEND_PORT " &> /dev/null; then
        print_warn "端口 $BACKEND_PORT 已被占用"
        PID=$(lsof -ti:$BACKEND_PORT)
        if [[ -n "$PID" ]]; then
            print_info "占用进程: $PID"
        fi
    else
        print_info "✓ 端口 $BACKEND_PORT 可用"
    fi
}

# 安装 Python 依赖
install_dependencies() {
    print_info "安装 Python 依赖..."
    
    cd "$BACKEND_DIR"
    
    # 检查 requirements.txt
    if [[ ! -f "requirements.txt" ]]; then
        print_error "未找到 requirements.txt 文件"
        exit 1
    fi
    
    # 安装依赖
    $PIP_CMD install --upgrade pip
    $PIP_CMD install -r requirements.txt
    
    # 检查关键包
    print_info "检查关键包..."
    if $PYTHON_CMD -c "import uvicorn" &> /dev/null; then
        print_info "✓ uvicorn 已安装"
    else
        print_error "uvicorn 安装失败"
        exit 1
    fi
    
    if $PYTHON_CMD -c "import fastapi" &> /dev/null; then
        print_info "✓ fastapi 已安装"
    else
        print_error "fastapi 安装失败"
        exit 1
    fi
}

# 创建日志目录
setup_logging() {
    print_info "设置日志目录..."
    
    mkdir -p "$LOG_DIR"
    chmod 755 "$LOG_DIR"
    
    print_info "✓ 日志目录: $LOG_DIR"
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务..."
    
    cd "$BACKEND_DIR"
    
    # 检查是否已在运行
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_warn "后端服务已在运行 (PID: $PID)"
            print_info "如需重启，请先停止服务: sudo bash $0 stop"
            return 0
        else
            print_warn "发现旧的 PID 文件，清理..."
            rm -f "$PID_FILE"
        fi
    fi
    
    # 启动服务
    print_info "启动命令: $PYTHON_CMD run_server.py --port $BACKEND_PORT"
    
    # 修改 run_server.py 以支持端口参数
    if grep -q "port=8000" "$BACKEND_DIR/run_server.py"; then
        print_info "更新 run_server.py 端口配置..."
        sed -i "s/port=8000/port=$BACKEND_PORT/g" "$BACKEND_DIR/run_server.py"
        sed -i "s/127.0.0.1:8000/127.0.0.1:$BACKEND_PORT/g" "$BACKEND_DIR/run_server.py"
    fi
    
    # 后台运行
    nohup $PYTHON_CMD run_server.py > "$LOG_FILE" 2>&1 &
    BACKEND_PID=$!
    
    # 保存 PID
    echo $BACKEND_PID > "$PID_FILE"
    
    print_info "✓ 后端服务已启动 (PID: $BACKEND_PID)"
    print_info "✓ 日志文件: $LOG_FILE"
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if check_service_status; then
        print_info "✓ 后端服务启动成功"
        print_info "✓ 监听地址: http://127.0.0.1:$BACKEND_PORT"
        print_info "✓ API 地址: http://127.0.0.1:$BACKEND_PORT/api"
    else
        print_error "后端服务启动失败，请检查日志: $LOG_FILE"
        tail -20 "$LOG_FILE"
        exit 1
    fi
}

# 检查服务状态
check_service_status() {
    local max_attempts=10
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s "http://127.0.0.1:$BACKEND_PORT/api/health" &> /dev/null; then
            return 0
        fi
        sleep 2
        ((attempt++))
    done
    
    return 1
}

# 停止后端服务
stop_backend() {
    print_info "停止后端服务..."
    
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill $PID
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 $PID
                print_warn "强制终止进程 (PID: $PID)"
            fi
            print_info "✓ 后端服务已停止 (PID: $PID)"
        else
            print_warn "进程不存在 (PID: $PID)"
        fi
        rm -f "$PID_FILE"
    else
        print_warn "未找到 PID 文件，尝试查找进程..."
        PID=$(ps aux | grep "run_server.py" | grep -v grep | awk '{print $2}')
        if [[ -n "$PID" ]]; then
            kill $PID
            print_info "✓ 停止进程 (PID: $PID)"
        else
            print_info "未找到运行中的后端服务"
        fi
    fi
}

# 查看服务状态
status_backend() {
    print_info "检查后端服务状态..."
    
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_info "✓ 后端服务正在运行 (PID: $PID)"
            print_info "✓ 端口: $BACKEND_PORT"
            print_info "✓ 工作目录: $BACKEND_DIR"
            
            # 检查端口监听
            if netstat -tuln | grep ":$BACKEND_PORT " &> /dev/null; then
                print_info "✓ 端口 $BACKEND_PORT 正在监听"
            else
                print_warn "✗ 端口 $BACKEND_PORT 未监听"
            fi
            
            # 检查健康接口
            if check_service_status; then
                print_info "✓ 健康检查通过"
                print_info "✓ API 可用: http://127.0.0.1:$BACKEND_PORT/api/health"
            else
                print_warn "✗ 健康检查失败"
            fi
            
            # 显示日志文件大小
            if [[ -f "$LOG_FILE" ]]; then
                LOG_SIZE=$(du -h "$LOG_FILE" | awk '{print $1}')
                print_info "✓ 日志文件: $LOG_FILE ($LOG_SIZE)"
            fi
        else
            print_warn "✗ 后端服务未运行 (PID 文件存在但进程不存在)"
            rm -f "$PID_FILE"
        fi
    else
        PID=$(ps aux | grep "run_server.py" | grep -v grep | awk '{print $2}')
        if [[ -n "$PID" ]]; then
            print_info "✓ 后端服务正在运行 (PID: $PID，但无 PID 文件)"
            print_info "✓ 端口: $BACKEND_PORT"
        else
            print_info "✗ 后端服务未运行"
        fi
    fi
}

# 查看日志
view_logs() {
    print_info "查看后端日志..."
    
    if [[ -f "$LOG_FILE" ]]; then
        tail -50 "$LOG_FILE"
    else
        print_warn "日志文件不存在: $LOG_FILE"
    fi
}

# 创建 systemd 服务
create_systemd_service() {
    print_info "创建 systemd 服务..."
    
    SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=眼科注射预约系统后端服务
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
ExecStart=$PYTHON_CMD $BACKEND_DIR/run_server.py
Restart=always
RestartSec=10
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载 systemd
    systemctl daemon-reload
    
    print_info "✓ systemd 服务已创建: $SERVICE_FILE"
    print_info "管理命令:"
    print_info "  sudo systemctl start $APP_NAME"
    print_info "  sudo systemctl stop $APP_NAME"
    print_info "  sudo systemctl restart $APP_NAME"
    print_info "  sudo systemctl status $APP_NAME"
    print_info "  sudo systemctl enable $APP_NAME (开机自启)"
}

# 主函数
main() {
    echo "=========================================="
    echo "   眼科注射预约系统 - 后端服务管理"
    echo "   版本: $APP_VERSION"
    echo "   端口: $BACKEND_PORT"
    echo "=========================================="
    
    case "${1:-}" in
        start)
            check_root
            check_dependencies
            setup_logging
            install_dependencies
            start_backend
            ;;
        stop)
            check_root
            stop_backend
            ;;
        restart)
            check_root
            stop_backend
            sleep 2
            check_dependencies
            setup_logging
            start_backend
            ;;
        status)
            status_backend
            ;;
        logs)
            view_logs
            ;;
        install)
            check_root
            check_dependencies
            setup_logging
            install_dependencies
            create_systemd_service
            print_info "安装完成！"
            print_info "启动服务: sudo systemctl start $APP_NAME"
            print_info "开机自启: sudo systemctl enable $APP_NAME"
            ;;
        *)
            echo "用法: $0 {start|stop|restart|status|logs|install}"
            echo ""
            echo "命令说明:"
            echo "  start    - 启动后端服务"
            echo "  stop     - 停止后端服务"
            echo "  restart  - 重启后端服务"
            echo "  status   - 查看服务状态"
            echo "  logs     - 查看日志"
            echo "  install  - 安装为 systemd 服务"
            echo ""
            echo "示例:"
            echo "  sudo bash $0 start     # 启动服务"
            echo "  sudo bash $0 install   # 安装为系统服务"
            echo "  sudo bash $0 status    # 查看状态"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"