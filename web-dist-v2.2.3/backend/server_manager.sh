#!/bin/bash

# 眼科注射预约系统 - 服务器管理脚本 v2.2.3
# 支持启动、停止、重启、状态检查功能

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SERVICE_NAME="眼科注射预约系统"
PYTHON_CMD="python3"
MAIN_SCRIPT="main.py"
PID_FILE="backend.pid"
LOG_FILE="logs/backend.log"
PORT=8031

# 创建日志目录
mkdir -p logs

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查端口是否被占用
check_port() {
    if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 获取占用端口的进程
get_port_process() {
    netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1
}

# 检查服务是否运行
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # 运行中
        else
            rm -f "$PID_FILE"  # 清理无效的PID文件
            return 1  # 未运行
        fi
    else
        return 1  # 未运行
    fi
}

# 启动服务
start_service() {
    print_info "正在启动 $SERVICE_NAME..."
    
    # 检查是否已经运行
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_warning "服务已经在运行中 (PID: $pid)"
        return 0
    fi
    
    # 检查 Python 环境
    print_info "检查 Python 环境..."
    if ! command -v $PYTHON_CMD &> /dev/null; then
        print_error "Python3 未安装或不在 PATH 中"
        return 1
    fi
    
    $PYTHON_CMD --version
    
    # 检查端口占用
    if check_port; then
        local process_pid=$(get_port_process)
        print_warning "端口 $PORT 被占用 (PID: $process_pid)"
        print_info "尝试停止占用端口的进程..."
        
        if [ -n "$process_pid" ]; then
            kill -TERM "$process_pid" 2>/dev/null
            sleep 2
            
            # 检查是否成功停止
            if check_port; then
                print_warning "强制停止占用端口的进程..."
                kill -KILL "$process_pid" 2>/dev/null
                sleep 1
            fi
        fi
        
        # 再次检查端口
        if check_port; then
            print_error "无法释放端口 $PORT，请手动处理"
            return 1
        fi
    fi
    
    # 安装依赖
    print_info "检查并安装依赖..."
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            print_warning "依赖安装可能有问题，但继续启动..."
        fi
    fi
    
    # 启动服务
    print_info "启动后台服务..."
    nohup $PYTHON_CMD $MAIN_SCRIPT > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # 保存PID
    echo $pid > "$PID_FILE"
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否成功启动
    if is_running; then
        print_success "服务启动成功 (PID: $pid)"
        print_success "监听地址：0.0.0.0:$PORT"
        print_success "日志文件：$LOG_FILE"
        
        # 显示最近的日志
        if [ -f "$LOG_FILE" ]; then
            print_info "最近日志:"
            tail -n 5 "$LOG_FILE"
        fi
        
        return 0
    else
        print_error "服务启动失败"
        print_info "最近日志:"
        if [ -f "$LOG_FILE" ]; then
            tail -n 10 "$LOG_FILE"
        fi
        return 1
    fi
}

# 停止服务
stop_service() {
    print_info "正在停止 $SERVICE_NAME..."
    
    if ! is_running; then
        print_warning "服务未运行"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    print_info "停止服务进程 (PID: $pid)..."
    
    # 优雅停止
    kill -TERM "$pid" 2>/dev/null
    
    # 等待进程停止
    local count=0
    while [ $count -lt 10 ]; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            break
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # 如果还在运行，强制停止
    if ps -p "$pid" > /dev/null 2>&1; then
        print_warning "强制停止服务进程..."
        kill -KILL "$pid" 2>/dev/null
        sleep 1
    fi
    
    # 清理PID文件
    rm -f "$PID_FILE"
    
    print_success "服务已停止"
    return 0
}

# 重启服务
restart_service() {
    print_info "正在重启 $SERVICE_NAME..."
    stop_service
    sleep 2
    start_service
}

# 查看服务状态
status_service() {
    print_info "检查 $SERVICE_NAME 状态..."
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "服务正在运行 (PID: $pid)"
        print_info "监听地址：0.0.0.0:$PORT"
        print_info "日志文件：$LOG_FILE"
        
        # 检查端口监听状态
        if check_port; then
            print_success "端口 $PORT 正在监听"
        else
            print_warning "端口 $PORT 未监听，服务可能有问题"
        fi
        
        # 显示进程信息
        print_info "进程信息:"
        ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null || print_warning "无法获取进程信息"
        
    else
        print_warning "服务未运行"
        
        # 检查端口是否被其他进程占用
        if check_port; then
            local process_pid=$(get_port_process)
            print_warning "端口 $PORT 被其他进程占用 (PID: $process_pid)"
        fi
    fi
    
    # 显示最近的日志
    if [ -f "$LOG_FILE" ]; then
        print_info "最近日志 (最后5行):"
        tail -n 5 "$LOG_FILE"
    else
        print_warning "日志文件不存在"
    fi
}

# 显示日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_info "显示实时日志 (按 Ctrl+C 退出):"
        tail -f "$LOG_FILE"
    else
        print_error "日志文件不存在: $LOG_FILE"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "眼科注射预约系统 - 服务器管理脚本 v2.2.3"
    echo ""
    echo "用法: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "命令说明:"
    echo "  start   - 启动服务"
    echo "  stop    - 停止服务"
    echo "  restart - 重启服务"
    echo "  status  - 查看服务状态"
    echo "  logs    - 显示实时日志"
    echo "  help    - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start    # 启动服务"
    echo "  $0 status   # 查看状态"
    echo "  $0 logs     # 查看日志"
}

# 主函数
main() {
    case "$1" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            status_service
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "无效的命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 检查参数
if [ $# -eq 0 ]; then
    print_error "缺少命令参数"
    echo ""
    show_help
    exit 1
fi

# 执行主函数
main "$1"
exit $?