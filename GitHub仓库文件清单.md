# GitHub仓库文件清单

## 📋 必需文件（核心功能）

### 后端代码
```
backend/
├── models/              # 数据模型
│   ├── __init__.py
│   ├── patient.py
│   ├── appointment.py
│   ├── data_dictionary.py
│   ├── follow_up_record.py
│   ├── print_record.py
│   └── user.py
├── routers/             # API路由
│   ├── __init__.py
│   ├── patients.py
│   ├── appointments.py
│   ├── data_dictionary.py
│   ├── follow_ups.py
│   ├── dashboard.py
│   ├── auth.py
│   └── system_settings.py
├── database.py          # 数据库配置
├── security.py          # 安全相关
├── main.py             # 主程序入口
├── simple_web_server.py # Web服务器
├── requirements.txt     # Python依赖
└── build_mac.spec      # Mac打包配置 ⭐
```

### 前端代码
```
frontend/
├── src/
│   ├── pages/          # 页面组件
│   ├── types/          # TypeScript类型
│   ├── App.tsx
│   └── main.tsx
├── public/
│   ├── logo.png
│   └── print-template.png
├── package.json        # 依赖配置
├── tsconfig.json
├── vite.config.ts
└── index.html
```

### GitHub Actions配置 ⭐⭐⭐
```
.github/
└── workflows/
    └── build-mac.yml   # Mac自动打包配置
```

### 配置文件
```
.gitignore              # Git忽略规则
README.md               # 项目说明
```

## 📚 推荐文件（文档）

### 使用文档
```
快速开始-GitHub自动打包.md    # ⭐ 最重要的文档
GitHub-Actions自动打包说明.md
Mac打包教程.md
Mac打包方案对比.md
```

### 可选文档
```
添加GitHub远程仓库指南.md
Mac源码运行指南.md
Mac打包验证清单.md
README-Mac打包.md
```

## ❌ 不需要的文件（排除）

### 构建产物
```
❌ backend/dist/
❌ backend/build/
❌ frontend/dist/
❌ node_modules/
❌ __pycache__/
```

### 打包文件
```
❌ simple-web-package-win7-v*/
❌ simple-web-package-mac-v*/
❌ dist/
❌ *.exe
```

### 数据库文件
```
❌ *.db
❌ *.sqlite
❌ *.sqlite3
```

### 临时文件
```
❌ *.log
❌ *.tmp
❌ *.bak
❌ .DS_Store
```

### Windows特定文件
```
❌ 打包Web版本-完整流程.bat
❌ 打包Web版本-完整流程-v2.bat
❌ 完整打包流程-v2.1.2.bat
❌ 打包完成-测试说明.txt
❌ 打包教程-另一台电脑操作.md
```

### 测试和迁移脚本（可选）
```
⚠️ backend/test_*.py           # 测试脚本（可选保留）
⚠️ backend/migrate_*.py        # 迁移脚本（可选保留）
⚠️ backend/create_*.py         # 创建脚本（可选保留）
⚠️ backend/add_*.py            # 添加脚本（可选保留）
⚠️ backend/check_*.py          # 检查脚本（可选保留）
```

### 服务器部署文件（可选）
```
⚠️ web-dist/                   # 服务器部署版本（可选）
⚠️ backend/main_web.py         # Web版本入口（可选）
⚠️ backend/main_static.py      # 静态文件服务（可选）
⚠️ backend/web_server.py       # Web服务器（可选）
```

### Tauri桌面应用（可选）
```
⚠️ frontend/src-tauri/         # Tauri桌面应用（如果不需要桌面版可删除）
```

### 其他说明文件
```
⚠️ 最终方案-自动迁移.md
⚠️ 新功能实现说明-v2.1.8.md
⚠️ Mac版本说明.txt
⚠️ 阿里云云效打包说明.md
```

## 🎯 推荐的最小GitHub仓库结构

```
bozhu_local/
├── .github/
│   └── workflows/
│       └── build-mac.yml                    # ⭐ GitHub Actions配置
├── backend/
│   ├── models/                              # 数据模型
│   ├── routers/                             # API路由
│   ├── database.py
│   ├── security.py
│   ├── main.py
│   ├── simple_web_server.py
│   ├── requirements.txt
│   └── build_mac.spec                       # ⭐ Mac打包配置
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
├── .gitignore
├── README.md
└── 快速开始-GitHub自动打包.md              # ⭐ 使用说明
```

## 📝 创建干净仓库的步骤

### 方法1：使用新分支（推荐）

```powershell
# 1. 创建新的干净分支
git checkout --orphan github-clean

# 2. 删除所有文件
git rm -rf .

# 3. 只添加需要的文件（见下面的命令）
git add backend/models/
git add backend/routers/
git add backend/*.py
git add backend/requirements.txt
git add backend/build_mac.spec
git add frontend/src/
git add frontend/public/
git add frontend/*.json
git add frontend/*.ts
git add frontend/index.html
git add .github/
git add .gitignore
git add README.md
git add 快速开始-GitHub自动打包.md

# 4. 提交
git commit -m "Initial clean commit for GitHub"

# 5. 推送到GitHub
git remote add github https://github.com/<your-username>/bozhu_local.git
git push github github-clean:master
```

### 方法2：手动创建（更简单）

```powershell
# 1. 创建新目录
mkdir bozhu_github
cd bozhu_github

# 2. 初始化Git
git init

# 3. 从原项目复制需要的文件
# （手动复制上面列出的必需文件）

# 4. 添加并提交
git add .
git commit -m "Initial commit"

# 5. 推送到GitHub
git remote add origin https://github.com/<your-username>/bozhu_local.git
git push -u origin master
```

### 方法3：使用脚本自动复制（最推荐）

我可以帮你创建一个脚本来自动复制需要的文件。

## 🔧 更新.gitignore

确保你的.gitignore包含：

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
.venv/
venv/

# Node
node_modules/
npm-debug.log*

# Build
dist/
build/
backend/dist/
backend/build/
frontend/dist/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# 打包文件
simple-web-package-*/
*.exe
*.dmg
*.zip

# 临时文件
*.tmp
*.bak
```

## ✅ 检查清单

推送到GitHub前检查：

- [ ] 删除了所有.db数据库文件
- [ ] 删除了所有打包产物（.exe, dist/等）
- [ ] 删除了node_modules/
- [ ] 删除了__pycache__/
- [ ] 保留了.github/workflows/build-mac.yml
- [ ] 保留了backend/build_mac.spec
- [ ] 保留了README.md和使用文档
- [ ] .gitignore配置正确

## 🎯 推荐操作

我建议使用**方法3（自动脚本）**，我可以帮你创建一个脚本来：
1. 自动复制所有需要的文件
2. 排除不需要的文件
3. 创建干净的GitHub仓库

需要我创建这个脚本吗？
