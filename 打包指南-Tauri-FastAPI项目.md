# Tauri + FastAPI 项目完整打包指南

本指南适用于将 Tauri (前端) + FastAPI (后端) 项目打包成独立的 Windows 可执行文件。

## 目录结构

```
项目根目录/
├── frontend/          # React + TypeScript 前端
├── backend/           # FastAPI 后端
└── tauri-app/         # Tauri 应用（包含前端和 Tauri 配置）
```

---

## 第一部分：后端打包 (FastAPI → EXE)

### 1. 创建后端启动脚本

在 `backend/` 目录下创建 `run_server.py`：

```python
"""
后端服务器启动脚本
用于 PyInstaller 打包后的独立运行
"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # 确保在正确的目录下运行
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe
        os.chdir(os.path.dirname(sys.executable))
    
    # 启动 Uvicorn 服务器
    # 使用简单的日志配置，避免在打包环境中出现问题
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_config=None,  # 禁用默认日志配置
        access_log=False  # 禁用访问日志
    )
```

### 2. 创建 PyInstaller 配置文件

在 `backend/` 目录下创建 `build_backend.spec`：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_server.py'],  # 入口文件
    pathex=[],
    binaries=[],
    datas=[
        ('models', 'models'),      # 包含 models 文件夹
        ('routers', 'routers'),    # 包含 routers 文件夹
    ],
    hiddenimports=[
        # Uvicorn 相关
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # SQLAlchemy 相关
        'sqlalchemy.sql.default_comparator',
        # 密码加密
        'passlib.handlers.bcrypt',
        # 你的应用模块（重要！）
        'main',
        'database',
        'security',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='backend_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../tauri-app/src-tauri/icons/icon.ico',  # 图标路径
)
```

### 3. 创建打包脚本

在 `backend/` 目录下创建 `打包后端.bat`：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo   打包 FastAPI 后端
echo ========================================
echo.

echo 正在打包...
python -m PyInstaller build_backend.spec --clean

if exist "dist\backend_server.exe" (
    echo.
    echo ========================================
    echo   打包成功！
    echo ========================================
    echo.
    echo 输出文件: dist\backend_server.exe
    dir dist\backend_server.exe
) else (
    echo.
    echo [错误] 打包失败
)

echo.
pause
```

### 4. 执行打包

```bash
cd backend
python -m PyInstaller build_backend.spec --clean
```

输出文件：`backend/dist/backend_server.exe`

---

## 第二部分：前端打包 (React + Tauri → EXE)

### 1. 配置 API 地址

在 `tauri-app/src/api/client.ts` 中：

```typescript
import axios from 'axios';

// 使用 127.0.0.1 而不是 localhost
const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### 2. 配置后端自动启动

在 `tauri-app/src-tauri/src/lib.rs` 中：

```rust
use std::process::{Command, Stdio};
use std::sync::Mutex;
use std::fs::OpenOptions;
use tauri::{Manager, State};

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

struct BackendProcess(Mutex<Option<std::process::Child>>);

#[tauri::command]
async fn start_backend(state: State<'_, BackendProcess>) -> Result<String, String> {
    let mut process_guard = state.0.lock().unwrap();
    
    if process_guard.is_some() {
        return Ok("Backend is already running".to_string());
    }

    let app_dir = std::env::current_exe()
        .map_err(|e| format!("Failed to get current exe path: {}", e))?
        .parent()
        .ok_or("Failed to get parent directory")?
        .to_path_buf();

    let backend_dir = app_dir.join("backend");
    
    if !backend_dir.exists() {
        return Err(format!("Backend directory not found: {:?}", backend_dir));
    }
    
    let log_file = backend_dir.join("backend.log");
    let log_output = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_file)
        .map_err(|e| format!("Failed to create log file: {}", e))?;
    
    let backend_exe = backend_dir.join("backend_server.exe");
    
    let mut cmd = Command::new(&backend_exe);
    cmd.current_dir(&backend_dir)
        .stdout(Stdio::from(log_output.try_clone().unwrap()))
        .stderr(Stdio::from(log_output));
    
    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);
    
    let child = cmd.spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?;

    *process_guard = Some(child);
    Ok("Backend started successfully".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(BackendProcess(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![start_backend])
        .setup(|app| {
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let state = app_handle.state::<BackendProcess>();
                match start_backend(state).await {
                    Ok(msg) => println!("Backend startup: {}", msg),
                    Err(e) => eprintln!("Backend startup error: {}", e),
                }
                std::thread::sleep(std::time::Duration::from_secs(3));
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 3. 配置 Tauri

在 `tauri-app/src-tauri/tauri.conf.json` 中：

```json
{
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "resources": ["../backend/**/*"],
    "externalBin": []
  }
}
```

### 4. 构建 Tauri 应用

```bash
cd tauri-app
npm run build
npm run tauri build
```

输出文件：`tauri-app/src-tauri/target/release/your-app.exe`

---

## 第三部分：创建分发包

### 1. 文件结构

```
dist-package/
├── your-app.exe              # Tauri 主程序
├── backend/
│   ├── backend_server.exe    # 后端服务
│   └── database.db           # 数据库（如果有）
├── 安全启动.bat              # 启动脚本
├── 诊断工具.bat              # 诊断工具
└── 使用说明.txt              # 用户指南
```

### 2. 创建安全启动脚本

`安全启动.bat`：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo   应用启动中...
echo ========================================
echo.

echo [1/3] 启动后端服务...
cd backend
start /B "" backend_server.exe
cd ..
echo ✓ 后端服务已启动

echo.
echo [2/3] 等待后端就绪...
set /a count=0
:wait_loop
set /a count+=1
if %count% gtr 30 goto start_app

timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 后端已就绪！
    goto start_app
)
echo 等待中... (%count%/30)
goto wait_loop

:start_app
echo.
echo [3/3] 启动应用...
start "" your-app.exe
echo ✓ 应用已启动

timeout /t 5
exit
```

### 3. 创建诊断工具

`诊断工具.bat`：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo   系统诊断工具
echo ========================================
echo.

echo [1] 检查文件...
if exist "your-app.exe" (echo ✓ 主程序存在) else (echo ✗ 主程序不存在)
if exist "backend\backend_server.exe" (echo ✓ 后端存在) else (echo ✗ 后端不存在)

echo.
echo [2] 检查端口...
netstat -ano | findstr ":8000"

echo.
echo [3] 启动后端测试...
cd backend
start "后端服务器" backend_server.exe
cd ..
timeout /t 5 /nobreak >nul

echo.
echo [4] 测试连接...
curl http://127.0.0.1:8000/

echo.
pause
```

---

## 第四部分：完整打包流程脚本

创建 `完整打包流程.bat`：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo   完整打包流程
echo ========================================
echo.

echo [1/4] 打包后端...
cd backend
call 打包后端.bat
cd ..

echo.
echo [2/4] 构建前端...
cd tauri-app
call npm run build

echo.
echo [3/4] 构建 Tauri 应用...
call npm run tauri build

echo.
echo [4/4] 创建分发包...
cd ..
if not exist "dist-package" mkdir "dist-package"
if not exist "dist-package\backend" mkdir "dist-package\backend"

copy "tauri-app\src-tauri\target\release\your-app.exe" "dist-package\"
copy "backend\dist\backend_server.exe" "dist-package\backend\"
copy "backend\database.db" "dist-package\backend\"

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 分发包位置: dist-package\
pause
```

---

## 常见问题和解决方案

### 1. 后端无法启动

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**: 在 `build_backend.spec` 的 `hiddenimports` 中添加缺失的模块

### 2. 日志配置错误

**问题**: `AttributeError: 'NoneType' object has no attribute 'isatty'`

**解决**: 在 `run_server.py` 中设置 `log_config=None`

### 3. CORS 错误

**问题**: 前端无法连接后端

**解决**: 在 FastAPI 中设置 `allow_origins=["*"]`

### 4. 端口被占用

**问题**: 后端启动失败

**解决**: 检查端口 8000 是否被占用，或修改端口号

---

## 依赖要求

### Python 依赖
```txt
fastapi
uvicorn
sqlmodel
passlib[bcrypt]==3.2.2
python-jose[cryptography]
python-multipart
PyInstaller
```

### Node.js 依赖
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "axios": "^1.0.0",
    "antd": "^5.0.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "vite": "^6.0.0",
    "typescript": "^5.0.0"
  }
}
```

### 系统要求
- Windows 10 或更高版本
- Rust 1.70+ (用于 Tauri)
- Node.js 18+ (用于前端构建)
- Python 3.10+ (用于后端开发)

---

## 最佳实践

1. **使用 127.0.0.1 而不是 localhost**
   - 在 Tauri 环境中更可靠

2. **禁用后端日志配置**
   - 避免打包后的日志问题

3. **隐藏后端控制台窗口**
   - 在 spec 文件中设置 `console=False`

4. **添加启动等待时间**
   - 后端需要时间启动，前端应等待 3-5 秒

5. **提供诊断工具**
   - 帮助用户快速定位问题

6. **定期备份数据库**
   - 提醒用户备份 database.db

---

## 版本控制建议

将以下文件添加到 `.gitignore`：

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
dist/
*.egg-info/

# Node
node_modules/
dist/

# Tauri
src-tauri/target/

# 数据库
*.db
*.sqlite

# 日志
*.log

# 打包文件
dist-package/
```

---

## 更新流程

### 仅更新后端
1. 修改后端代码
2. 运行 `backend/打包后端.bat`
3. 复制 `backend_server.exe` 到分发包

### 仅更新前端
1. 修改前端代码
2. 运行 `npm run build` 和 `npm run tauri build`
3. 复制新的 exe 到分发包

### 完整更新
1. 运行 `完整打包流程.bat`
2. 测试分发包
3. 发送给用户

---

## 总结

这个打包方案的优点：
- ✅ 用户无需安装 Python 或 Node.js
- ✅ 单个 exe 文件即可运行
- ✅ 后端自动启动和隐藏
- ✅ 包含完整的诊断工具
- ✅ 易于分发和部署

记住：每次修改代码后都要重新打包相应的部分！
