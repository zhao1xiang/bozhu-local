# 眼科注射预约系统 Web版 构建指南

## 概述

本指南说明如何构建和运行眼科注射预约系统的Web版本。Web版本包含前端（React + TypeScript）和后端（FastAPI + Python）。

## 系统要求

### 必需软件
- **Node.js** >= 18.0.0 (用于前端构建)
- **npm** >= 9.0.0 (Node包管理器)
- **Python** >= 3.8 (用于后端)
- **pip** (Python包管理器)

### 可选软件
- **Git** (用于版本控制)
- **Visual Studio Code** (推荐的代码编辑器)

## 快速开始

### Windows 用户

#### 方法1：使用PowerShell脚本（推荐）

```powershell
# 进入项目根目录
cd path\to\bozhu_local

# 执行构建脚本
.\build_web_server.ps1

# 启动服务器
cd backend
python web_server.py
```

#### 方法2：手动构建

```powershell
# 1. 构建前端
cd frontend
npm install
npm run build
cd ..

# 2. 复制前端文件到后端
Copy-Item -Path "frontend/dist/*" -Destination "backend/frontend" -Recurse -Force

# 3. 安装后端依赖
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. 启动服务器
python web_server.py
```

### Linux/Mac 用户

#### 方法1：使用Bash脚本（推荐）

```bash
# 进入项目根目录
cd path/to/bozhu_local

# 赋予脚本执行权限
chmod +x build_web_server.sh

# 执行构建脚本
./build_web_server.sh

# 启动服务器
cd backend
python web_server.py
```

#### 方法2：手动构建

```bash
# 1. 构建前端
cd frontend
npm install
npm run build
cd ..

# 2. 复制前端文件到后端
cp -r frontend/dist/* backend/frontend/

# 3. 安装后端依赖
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. 启动服务器
python web_server.py
```

## 构建脚本选项

### PowerShell 脚本 (Windows)

```powershell
# 完整构建（默认）
.\build_web_server.ps1

# 跳过前端构建
.\build_web_server.ps1 -SkipFrontend

# 跳过后端构建
.\build_web_server.ps1 -SkipBackend

# 清理旧文件后构建
.\build_web_server.ps1 -Clean

# 组合选项
.\build_web_server.ps1 -Clean -SkipBackend
```

### Bash 脚本 (Linux/Mac)

```bash
# 完整构建（默认）
./build_web_server.sh

# 跳过前端构建
./build_web_server.sh --skip-frontend

# 跳过后端构建
./build_web_server.sh --skip-backend

# 清理旧文件后构建
./build_web_server.sh --clean

# 组合选项
./build_web_server.sh --clean --skip-backend
```

## 启动服务器

### 自动启动（推荐）

```bash
# Windows
cd backend
python web_server.py

# Linux/Mac
cd backend
python web_server.py
```

服务器启动后会自动打开浏览器，访问 `http://localhost:8000`

### 手动启动

如果自动打开浏览器失败，请手动访问：
- **URL**: http://localhost:8000
- **默认用户名**: admin
- **默认密码**: admin123

## 项目结构

```
bozhu_local/
├── frontend/                    # 前端项目
│   ├── src/                    # 源代码
│   ├── public/                 # 公共资源
│   ├── dist/                   # 构建输出（生产版本）
│   ├── package.json            # 前端依赖配置
│   ├── vite.config.ts          # Vite构建配置
│   └── tsconfig.json           # TypeScript配置
│
├── backend/                     # 后端项目
│   ├── frontend/               # 前端静态文件（由构建脚本复制）
│   ├── routers/                # API路由
│   ├── models/                 # 数据模型
│   ├── main_web.py             # Web版本主应用
│   ├── web_server.py           # Web服务器启动脚本
│   ├── database.py             # 数据库配置
│   ├── requirements.txt        # Python依赖
│   └── database.db             # SQLite数据库
│
├── build_web_server.ps1        # Windows构建脚本
├── build_web_server.sh         # Linux/Mac构建脚本
└── WEB_BUILD_GUIDE.md          # 本文件
```

## 构建流程说明

### 前端构建流程

1. **安装依赖**: `npm install`
   - 安装所有Node.js依赖包
   - 包括React、TypeScript、Vite等

2. **类型检查**: `tsc -b`
   - 检查TypeScript类型错误
   - 确保代码质量

3. **打包构建**: `vite build`
   - 使用Vite进行生产构建
   - 生成优化的静态文件
   - 输出到 `frontend/dist/` 目录

### 后端准备流程

1. **创建虚拟环境**: `python -m venv .venv`
   - 隔离Python环境
   - 避免依赖冲突

2. **安装依赖**: `pip install -r requirements.txt`
   - 安装FastAPI、SQLModel等依赖
   - 准备数据库驱动

3. **数据库初始化**
   - 首次启动时自动创建数据库
   - 自动执行数据库迁移
   - 创建默认管理员用户

## 常见问题

### Q: 构建前端时出现 "npm: command not found"

**A**: Node.js未安装或未添加到PATH。
- 下载安装: https://nodejs.org/
- 安装后重启终端

### Q: 构建前端时出现 "tsc: command not found"

**A**: TypeScript未安装。
- 运行: `npm install`
- 或全局安装: `npm install -g typescript`

### Q: 启动服务器时出现 "ModuleNotFoundError"

**A**: Python依赖未安装。
- 运行: `pip install -r requirements.txt`
- 确保虚拟环境已激活

### Q: 访问 http://localhost:8000 显示空白页面

**A**: 前端文件未正确复制。
- 检查 `backend/frontend/` 目录是否包含 `index.html`
- 重新运行构建脚本

### Q: 登录失败

**A**: 数据库可能损坏或用户不存在。
- 删除 `backend/database.db`
- 重启服务器，会自动创建新数据库
- 使用默认用户: admin / admin123

### Q: 端口8000已被占用

**A**: 修改 `backend/web_server.py` 中的端口号。
```python
port = 8001  # 改为其他端口
```

## 开发模式

### 前端开发

```bash
cd frontend
npm run dev
```

启动Vite开发服务器，支持热更新。
访问: http://localhost:5173

### 后端开发

```bash
cd backend
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\Activate.ps1  # Windows

python main_web.py
```

## 生产部署

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 使用Gunicorn启动

```bash
pip install gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 main_web:app
```

## 性能优化

### 前端优化

- 已启用代码分割和动态导入
- 已启用CSS压缩
- 已启用JavaScript压缩
- 已生成Source Map用于调试

### 后端优化

- 使用SQLModel进行ORM操作
- 启用数据库连接池
- 使用异步处理提高并发性能

## 故障排查

### 查看日志

```bash
# 查看服务器日志
tail -f backend/logs/web_server.log

# 查看数据库日志
sqlite3 backend/database.db ".log"
```

### 重置数据库

```bash
# 备份当前数据库
cp backend/database.db backend/database.db.backup

# 删除数据库（重启时会自动创建）
rm backend/database.db

# 重启服务器
python backend/web_server.py
```

## 获取帮助

- 查看日志文件: `backend/logs/web_server.log`
- 检查数据库: `sqlite3 backend/database.db`
- 查看API文档: http://localhost:8000/docs (Swagger UI)
- 查看API文档: http://localhost:8000/redoc (ReDoc)

## 版本信息

- **应用版本**: 2.1.3-web
- **前端框架**: React 18.3.1 + TypeScript 5.8.3
- **后端框架**: FastAPI + SQLModel
- **数据库**: SQLite
- **构建工具**: Vite 6.3.5

## 许可证

本项目遵循相关许可证。详见项目根目录的LICENSE文件。

## 更新日志

### v2.1.3-web
- 完整的Web版本构建脚本
- 自动数据库迁移
- 改进的错误处理
- 优化的前端性能

---

**最后更新**: 2026年5月8日
