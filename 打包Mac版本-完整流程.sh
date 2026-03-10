#!/bin/bash
# Mac系统打包脚本
# 用于将应用打包成Mac独立运行版本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "开始打包Mac版本"
echo "=========================================="
echo ""

# 检查Python版本
echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Python版本: $PYTHON_VERSION"
echo ""

# 检查Node.js
echo "2. 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "Node.js版本: $NODE_VERSION"
echo ""

# 构建前端
echo "3. 构建前端..."
cd frontend
echo "安装前端依赖..."
npm install
echo "构建前端项目..."
npm run build
cd ..
echo "前端构建完成"
echo ""

# 安装后端依赖
echo "4. 安装后端依赖..."
cd backend
pip3 install -r requirements.txt
pip3 install pyinstaller
echo "后端依赖安装完成"
echo ""

# 打包后端
echo "5. 打包后端服务..."
pyinstaller build_mac.spec --clean --noconfirm
echo "后端打包完成"
echo ""

# 创建发布目录
echo "6. 创建发布包..."
RELEASE_DIR="../simple-web-package-mac-v2.1.8"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# 复制后端可执行文件
echo "复制后端文件..."
cp dist/backend_server "$RELEASE_DIR/"
chmod +x "$RELEASE_DIR/backend_server"

# 复制前端文件
echo "复制前端文件..."
cp -r ../frontend/dist "$RELEASE_DIR/frontend"

cd ..

# 创建启动脚本
echo "7. 创建启动脚本..."
cat > "$RELEASE_DIR/启动服务.sh" << 'EOF'
#!/bin/bash
# 玻注预约系统 - Mac版启动脚本

echo "=========================================="
echo "玻注预约系统 v2.1.8 - Mac版"
echo "=========================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查frontend目录
if [ ! -d "frontend" ]; then
    echo "错误: 未找到frontend目录"
    echo "请确保frontend目录与程序在同一目录下"
    read -p "按回车键退出..."
    exit 1
fi

echo "正在启动服务..."
echo "服务启动后将自动打开浏览器"
echo "如果浏览器未自动打开，请手动访问: http://127.0.0.1:8000"
echo ""
echo "按 Ctrl+C 可以停止服务"
echo "=========================================="
echo ""

# 启动服务
./backend_server

# 如果服务异常退出
echo ""
echo "服务已停止"
read -p "按回车键退出..."
EOF

chmod +x "$RELEASE_DIR/启动服务.sh"

# 创建说明文件
echo "8. 创建说明文件..."
cat > "$RELEASE_DIR/使用说明.txt" << 'EOF'
玻注预约系统 - Mac版 v2.1.8
========================================

一、系统要求
----------------------------------------
- macOS 10.13 (High Sierra) 或更高版本
- 无需安装Python或其他依赖

二、使用方法
----------------------------------------
1. 双击运行 "启动服务.sh"
2. 等待服务启动（约5-10秒）
3. 浏览器会自动打开系统页面
4. 如果浏览器未自动打开，请手动访问: http://127.0.0.1:8000

三、首次使用
----------------------------------------
默认管理员账号：
- 用户名: admin
- 密码: admin123

首次登录后请立即修改密码！

四、停止服务
----------------------------------------
在终端窗口按 Ctrl+C 即可停止服务

五、数据备份
----------------------------------------
重要数据保存在 database.db 文件中
建议定期备份此文件

六、常见问题
----------------------------------------
Q: 提示"无法打开，因为无法验证开发者"？
A: 右键点击"启动服务.sh"，选择"打开"，然后点击"打开"按钮

Q: 提示权限不足？
A: 在终端执行: chmod +x 启动服务.sh

Q: 浏览器显示空白页？
A: 按 Cmd+Shift+R 强制刷新浏览器缓存

Q: 端口被占用？
A: 关闭其他占用8000端口的程序，或修改配置文件

七、技术支持
----------------------------------------
如有问题，请联系技术支持
EOF

cat > "$RELEASE_DIR/更新日志-v2.1.8.txt" << 'EOF'
更新日志 v2.1.8
========================================

新增功能：
1. 门诊号改为非必填字段
2. 支持软删除功能（患者和预约）
3. 打印电话号码可配置
4. 前4针注射间隔可配置
5. 优化患者重复检查逻辑

修复问题：
1. 修复JSON序列化错误
2. 修复重复检查时的数据过滤
3. 优化前端表单验证

界面优化：
1. 隐藏预约列表的取消按钮
2. 优化门诊号字段显示
3. 改进打印位置精度

技术改进：
1. 数据库自动迁移支持
2. 优化查询性能
3. 改进错误处理
EOF

cat > "$RELEASE_DIR/重要-请先阅读.txt" << 'EOF'
重要提示
========================================

Mac版本特别说明：

1. 首次运行可能需要授权
   - 系统可能提示"无法验证开发者"
   - 请右键点击程序，选择"打开"
   - 在弹出的对话框中点击"打开"按钮

2. 权限设置
   - 如果无法运行，请在终端执行：
     chmod +x 启动服务.sh
     chmod +x backend_server

3. 防火墙设置
   - 首次运行可能提示防火墙警告
   - 请选择"允许"以便程序正常运行

4. 数据安全
   - 所有数据保存在本地 database.db 文件
   - 请定期备份此文件
   - 不要删除或修改此文件

5. 系统兼容性
   - 支持 macOS 10.13 及以上版本
   - 建议使用 macOS 10.15 或更高版本

6. 浏览器兼容性
   - 推荐使用 Safari、Chrome 或 Firefox
   - 如遇显示问题，请清除浏览器缓存

如有问题，请查看"使用说明.txt"
EOF

echo ""
echo "=========================================="
echo "打包完成！"
echo "=========================================="
echo ""
echo "发布包位置: $RELEASE_DIR"
echo ""
echo "包含文件:"
echo "  - backend_server (后端可执行文件)"
echo "  - frontend/ (前端文件)"
echo "  - 启动服务.sh (启动脚本)"
echo "  - 使用说明.txt"
echo "  - 更新日志-v2.1.8.txt"
echo "  - 重要-请先阅读.txt"
echo ""
echo "请将整个 $RELEASE_DIR 目录打包分发"
echo ""
