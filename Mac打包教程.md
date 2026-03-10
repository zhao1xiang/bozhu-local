# Mac版本打包教程

## 前提条件

在Mac系统上打包需要以下环境：

### 1. 安装Homebrew（如果还没有）
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装Python 3.7+
```bash
brew install python@3.9
```

验证安装：
```bash
python3 --version
```

### 3. 安装Node.js
```bash
brew install node
```

验证安装：
```bash
node --version
npm --version
```

### 4. 安装Git（如果还没有）
```bash
brew install git
```

## 打包步骤

### 方法一：使用自动化脚本（推荐）

1. **克隆代码仓库**
```bash
git clone <你的仓库地址>
cd bozhu_local
```

2. **赋予脚本执行权限**
```bash
chmod +x 打包Mac版本-完整流程.sh
```

3. **运行打包脚本**
```bash
./打包Mac版本-完整流程.sh
```

4. **等待打包完成**
   - 脚本会自动完成所有步骤
   - 打包完成后会在项目根目录生成 `simple-web-package-mac-v2.1.8` 目录

5. **测试打包结果**
```bash
cd simple-web-package-mac-v2.1.8
./启动服务.sh
```

### 方法二：手动打包

如果自动化脚本遇到问题，可以手动执行以下步骤：

#### 步骤1：构建前端
```bash
cd frontend
npm install
npm run build
cd ..
```

#### 步骤2：安装后端依赖
```bash
cd backend
pip3 install -r requirements.txt
pip3 install pyinstaller
```

#### 步骤3：打包后端
```bash
pyinstaller build_mac.spec --clean --noconfirm
```

#### 步骤4：创建发布目录
```bash
cd ..
mkdir -p simple-web-package-mac-v2.1.8
```

#### 步骤5：复制文件
```bash
# 复制后端可执行文件
cp backend/dist/backend_server simple-web-package-mac-v2.1.8/
chmod +x simple-web-package-mac-v2.1.8/backend_server

# 复制前端文件
cp -r frontend/dist simple-web-package-mac-v2.1.8/frontend
```

#### 步骤6：创建启动脚本
参考自动化脚本中的启动脚本内容，手动创建 `启动服务.sh`

## 打包后的目录结构

```
simple-web-package-mac-v2.1.8/
├── backend_server          # 后端可执行文件
├── frontend/               # 前端静态文件
│   ├── assets/
│   ├── index.html
│   ├── logo.png
│   └── print-template.png
├── 启动服务.sh             # 启动脚本
├── 使用说明.txt
├── 更新日志-v2.1.8.txt
└── 重要-请先阅读.txt
```

## 分发打包

### 创建DMG镜像（可选）

如果想创建Mac标准的DMG安装包：

1. **安装create-dmg工具**
```bash
brew install create-dmg
```

2. **创建DMG**
```bash
create-dmg \
  --volname "玻注预约系统 v2.1.8" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  "玻注预约系统-v2.1.8.dmg" \
  "simple-web-package-mac-v2.1.8/"
```

### 创建ZIP压缩包

```bash
zip -r simple-web-package-mac-v2.1.8.zip simple-web-package-mac-v2.1.8/
```

## 代码签名（可选）

如果你有Apple Developer账号，可以对应用进行代码签名：

```bash
# 查看可用的签名证书
security find-identity -v -p codesigning

# 签名应用
codesign --force --deep --sign "Developer ID Application: Your Name" simple-web-package-mac-v2.1.8/backend_server

# 验证签名
codesign --verify --deep --strict --verbose=2 simple-web-package-mac-v2.1.8/backend_server
```

## 公证（Notarization）

对于macOS 10.15+，建议进行公证：

```bash
# 1. 创建ZIP
ditto -c -k --keepParent simple-web-package-mac-v2.1.8 simple-web-package-mac-v2.1.8.zip

# 2. 上传公证
xcrun altool --notarize-app \
  --primary-bundle-id "com.yourcompany.bozhu" \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD" \
  --file simple-web-package-mac-v2.1.8.zip

# 3. 检查公证状态
xcrun altool --notarization-info <RequestUUID> \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD"

# 4. 装订公证票据
xcrun stapler staple simple-web-package-mac-v2.1.8/backend_server
```

## 常见问题

### Q1: PyInstaller打包失败
**A:** 确保安装了所有依赖：
```bash
pip3 install --upgrade pip
pip3 install --upgrade pyinstaller
pip3 install -r backend/requirements.txt
```

### Q2: 前端构建失败
**A:** 清除缓存重新构建：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Q3: 可执行文件无法运行
**A:** 检查权限：
```bash
chmod +x simple-web-package-mac-v2.1.8/backend_server
chmod +x simple-web-package-mac-v2.1.8/启动服务.sh
```

### Q4: 提示"无法验证开发者"
**A:** 右键点击程序，选择"打开"，在弹出的对话框中点击"打开"按钮

### Q5: M1/M2芯片兼容性
**A:** 在Apple Silicon Mac上打包会自动生成ARM64版本。如需同时支持Intel和ARM：
```bash
# 安装Rosetta 2
softwareupdate --install-rosetta

# 使用universal2打包
arch -x86_64 pyinstaller build_mac.spec --clean --noconfirm
```

## 测试清单

打包完成后，请测试以下功能：

- [ ] 双击启动脚本能正常启动
- [ ] 浏览器自动打开系统页面
- [ ] 能正常登录（admin/admin123）
- [ ] 能添加患者信息
- [ ] 能创建预约
- [ ] 能打印预约单
- [ ] 能修改系统配置
- [ ] 数据能正常保存
- [ ] 重启后数据不丢失

## 版本兼容性

| macOS版本 | 支持状态 | 备注 |
|----------|---------|------|
| 10.13 (High Sierra) | ✅ 支持 | 最低要求 |
| 10.14 (Mojave) | ✅ 支持 | |
| 10.15 (Catalina) | ✅ 支持 | 需要授权 |
| 11.x (Big Sur) | ✅ 支持 | |
| 12.x (Monterey) | ✅ 支持 | |
| 13.x (Ventura) | ✅ 支持 | |
| 14.x (Sonoma) | ✅ 支持 | 推荐 |

## 技术支持

如果在打包过程中遇到问题，请提供以下信息：

1. macOS版本
2. Python版本
3. Node.js版本
4. 错误日志
5. 打包步骤截图

## 更新日志

### v2.1.8 (2024-03-10)
- 首次发布Mac版本
- 支持Apple Silicon (M1/M2)
- 优化启动速度
- 改进错误提示

## 许可证

本软件仅供内部使用，未经授权不得分发。
