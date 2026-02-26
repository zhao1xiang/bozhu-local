# 眼科注射预约系统 v2.1.1

一个支持**EXE桌面版**和**Web网页版**的双端应用系统。

## 📚 文档导航

### 👩‍💻 前端开发者
- **[前端开发指南](./前端开发指南.md)** - 详细的开发文档（必读）
- **[前端开发速查表](./前端开发速查表.md)** - 快速参考卡片

### 🔧 系统管理员
- **[路由修复总结](./路由修复总结.md)** - 最近的修复记录
- **[Web部署说明](./web-dist/部署说明.txt)** - Web版本部署指南
- **[EXE部署说明](./dist-package/部署说明_v2.1.1.txt)** - EXE版本部署指南

## 🎯 项目特点

- **双端支持**：同一套代码，支持EXE桌面版和Web网页版
- **智能环境检测**：自动识别运行环境，调整行为
- **统一API配置**：通过环境变量灵活配置后端地址
- **完整的打包工具**：提供快速打包和完整打包脚本

## 🚀 快速开始

### 本地开发

**启动后端：**
```bash
cd backend
python run_server.py
```

验证：访问 http://127.0.0.1:8000/api/health

**启动前端：**
```bash
cd frontend
npm install
npm run dev
```

访问：`http://localhost:5173`

### 打包EXE版本

```bash
# 快速打包（推荐）
快速重新打包前端.bat

# 完整打包
完整打包流程-v2.1.1.bat
```

### 打包Web版本

```bash
重新打包Web前端.bat
```

## 📁 项目结构

```
bozhu_local/
├── frontend/                    # 前端代码
│   ├── src/
│   │   ├── api/                # API配置
│   │   ├── pages/              # 页面组件
│   │   ├── layouts/            # 布局组件
│   │   ├── components/         # 通用组件
│   │   └── App.tsx             # 路由配置
│   ├── src-tauri/              # Tauri配置（EXE）
│   └── package.json
├── backend/                     # 后端代码
│   ├── main.py                 # FastAPI主文件
│   ├── routers/                # API路由
│   ├── models/                 # 数据模型
│   └── requirements.txt
├── dist-package/               # EXE打包产物
├── web-dist/                   # Web部署文件
├── 前端开发指南.md             # 前端开发文档
├── 前端开发速查表.md           # 快速参考
└── README.md                   # 本文件
```

## 🔑 核心概念

### 双端架构

| 特性 | EXE桌面版 | Web网页版 |
|------|----------|----------|
| 运行环境 | Windows应用 | 浏览器 |
| 后端地址 | 本地 (127.0.0.1:8000) | 服务器 (HTTPS) |
| 启动流程 | Splash → 登录 | 直接登录 |
| 打包工具 | Tauri | Vite |

### 环境变量

- `VITE_API_URL` - 后端API地址
- `VITE_SKIP_SPLASH` - 是否跳过Splash页面

### 路由结构

```
/ → Splash（EXE）或登录（Web）
/login → 登录页
/debug → 调试信息
/app/* → 主应用（需登录）
  ├── /app/dashboard
  ├── /app/patients
  ├── /app/appointments
  ├── /app/daily-work
  ├── /app/print-center
  └── /app/system-config
```

## ⚠️ 重要提醒

### 前端开发者必读

1. **路由跳转必须加 `/app` 前缀**
   ```typescript
   navigate('/app/appointments');  // ✅ 正确
   navigate('/appointments');      // ❌ 错误
   ```

2. **API请求必须使用 `apiClient`**
   ```typescript
   apiClient.get('/patients');     // ✅ 正确
   axios.get('http://...');        // ❌ 错误
   ```

3. **不要随意修改环境检测逻辑**
   - 修改前请阅读 `前端开发指南.md`
   - 修改后必须测试EXE和Web两个版本

## 🐛 调试工具

- **调试页面**：访问 `/debug` 查看环境信息
- **开发者工具**：按 `F12` 打开浏览器控制台
- **打包进度**：运行 `查看打包进度.bat`

## 📦 打包产物

### EXE版本
- 位置：`dist-package/`
- 主文件：`眼科注射预约系统.exe`
- 包含：主程序、后端服务、数据库

### Web版本
- 位置：`frontend/dist/` 或 `web-frontend-only.zip`
- 部署：上传到服务器 `/work/local-show/frontend/`

## 🔄 版本历史

### v2.1.1 (2026-02-24)
- ✅ 修复所有路由问题
- ✅ 修复API路径配置
- ✅ 改进Tauri环境检测
- ✅ 添加调试页面
- ✅ 创建Web后台运行脚本
- ✅ 完善开发文档

## 📞 技术支持

遇到问题？请查看：
1. [前端开发指南](./前端开发指南.md) - 详细文档
2. [前端开发速查表](./前端开发速查表.md) - 快速参考
3. `/debug` 页面 - 环境信息
4. 浏览器控制台 - 错误日志

---

**开发团队**  
版本：v2.1.1  
最后更新：2026-02-24
