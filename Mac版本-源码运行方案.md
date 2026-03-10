# Mac版本 - 源码运行方案

由于Mac的架构兼容性问题（Intel vs Apple Silicon），推荐使用源码运行方式。

## 客户操作步骤

### 1. 安装Python（如果没有）
```bash
# 检查是否已安装Python
python3 --version

# 如果没有，从官网下载安装：
# https://www.python.org/downloads/macos/
```

### 2. 下载并解压代码
从GitHub下载代码压缩包或使用git克隆：
```bash
# 方法1：下载ZIP（推荐给不熟悉git的用户）
# 访问 https://github.com/zhao1xiang/bozhu-local
# 点击绿色的 "Code" 按钮 -> "Download ZIP"
# 解压到任意目录

# 方法2：使用git克隆
git clone https://github.com/zhao1xiang/bozhu-local.git
cd bozhu-local
```

### 3. 运行启动脚本
```bash
cd bozhu-local  # 进入项目目录
chmod +x Mac启动服务.sh  # 添加执行权限
./Mac启动服务.sh  # 运行
```

### 4. 访问系统
浏览器会自动打开 http://localhost:8000
默认账号：admin / admin123

## 优势
- 无需担心CPU架构兼容性
- 可以随时更新代码（git pull）
- 更容易调试问题
- 支持所有Mac系统（Intel和Apple Silicon）

## 注意事项
- 首次运行会自动安装依赖，需要几分钟
- 需要保持终端窗口打开
- 关闭终端会停止服务
