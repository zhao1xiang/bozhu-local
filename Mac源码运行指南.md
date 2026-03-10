# Mac用户 - 源码运行指南

## 适用场景
如果没有Mac打包版本，Mac用户可以直接运行源码。

## 系统要求
- macOS 10.13 或更高版本
- 需要安装Python 3.7+和Node.js

## 安装步骤

### 1. 安装Homebrew（如果还没有）
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装Python和Node.js
```bash
brew install python@3.9 node
```

### 3. 克隆代码
```bash
git clone <仓库地址>
cd bozhu_local
```

### 4. 构建前端
```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. 安装后端依赖
```bash
cd backend
pip3 install -r requirements.txt
```

### 6. 创建启动脚本
```bash
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
cd backend
python3 simple_web_server.py
EOF

chmod +x start.sh
```

## 使用方法

### 启动服务
```bash
./start.sh
```

或者直接运行：
```bash
cd backend
python3 simple_web_server.py
```

### 访问系统
浏览器会自动打开，或手动访问：
```
http://127.0.0.1:8000
```

### 停止服务
在终端按 `Ctrl+C`

## 优点
- ✅ 无需Mac打包环境
- ✅ 可以随时更新代码
- ✅ 便于调试和开发
- ✅ 文件体积小（不包含Python运行时）

## 缺点
- ❌ 需要安装Python环境
- ❌ 需要手动安装依赖
- ❌ 不如打包版本方便

## 常见问题

### Q: 提示找不到Python？
A: 确保已安装Python 3.7+
```bash
python3 --version
```

### Q: 提示缺少模块？
A: 重新安装依赖
```bash
cd backend
pip3 install -r requirements.txt
```

### Q: 端口被占用？
A: 修改端口或关闭占用8000端口的程序

### Q: 前端显示空白？
A: 确保已构建前端
```bash
cd frontend
npm run build
```

## 自动化脚本

创建一个一键启动脚本：

```bash
cat > 一键启动.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "玻注预约系统 - Mac源码版"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    echo "请先安装: brew install python@3.9"
    exit 1
fi

# 检查依赖
if [ ! -d "backend/venv" ]; then
    echo "首次运行，正在安装依赖..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# 检查前端
if [ ! -d "backend/frontend" ]; then
    echo "正在构建前端..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# 启动服务
echo "正在启动服务..."
cd backend
source venv/bin/activate
python3 simple_web_server.py
EOF

chmod +x 一键启动.sh
```

然后用户只需运行：
```bash
./一键启动.sh
```
