# Web 演示环境部署指南

这是眼科注射预约系统的 Web 演示版本，独立于桌面应用（Tauri）打包。

## 目录结构

```
web-deploy/
├── backend/          # 后端部署文件（从主项目复制）
├── frontend/         # 前端构建产物
├── nginx.conf        # Nginx 配置示例
├── deploy.sh         # Linux 部署脚本
├── deploy.bat        # Windows 部署脚本
└── README.md         # 本文件
```

## 部署步骤

### 方式一：本地开发测试

1. 启动后端：
```bash
cd ../backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

2. 启动前端开发服务器：
```bash
cd ../frontend
npm install
npm run dev
```

3. 访问 http://localhost:5173

### 方式二：生产环境部署

#### Windows 部署

运行 `deploy.bat` 脚本：
```bash
deploy.bat
```

#### Linux 部署

运行 `deploy.sh` 脚本：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 生产环境配置

### 后端配置

后端默认运行在 `http://0.0.0.0:8000`

环境变量：
- `DATABASE_URL`: 数据库路径（默认：./database.db）
- `CORS_ORIGINS`: 允许的跨域来源（默认：*）

### 前端配置

前端需要配置后端 API 地址，在 `frontend/src/api/client.ts` 中修改：

```typescript
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';
```

构建时设置环境变量：
```bash
VITE_API_URL=https://your-api-domain.com npm run build
```

### Nginx 配置

参考 `nginx.conf` 文件配置反向代理。

## 注意事项

1. Web 版本不包含 Tauri 相关功能
2. 需要配置 CORS 允许前端访问后端 API
3. 生产环境建议使用 HTTPS
4. 数据库文件需要定期备份
5. 建议使用 Nginx 或 Apache 作为反向代理

## 与桌面版的区别

- 桌面版：Tauri + React，打包为独立 exe
- Web 版：纯 Web 应用，部署到服务器
- 两者共享相同的后端 API 和前端代码
- Web 版需要配置 CORS 和反向代理
