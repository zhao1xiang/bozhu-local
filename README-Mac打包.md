# Mac版本快速打包指南

## 一键打包（推荐）

如果你有Mac电脑，只需3步：

### 1. 准备环境
```bash
# 安装Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装必要工具
brew install python@3.9 node git
```

### 2. 克隆代码并打包
```bash
# 克隆代码
git clone <你的仓库地址>
cd bozhu_local

# 赋予执行权限
chmod +x 打包Mac版本-完整流程.sh

# 一键打包
./打包Mac版本-完整流程.sh
```

### 3. 测试运行
```bash
cd simple-web-package-mac-v2.1.8
./启动服务.sh
```

就这么简单！

## 打包结果

打包完成后会生成 `simple-web-package-mac-v2.1.8` 目录，包含：

```
simple-web-package-mac-v2.1.8/
├── backend_server          # Mac可执行文件
├── frontend/               # 前端文件
├── 启动服务.sh             # 启动脚本
├── 使用说明.txt
├── 更新日志-v2.1.8.txt
└── 重要-请先阅读.txt
```

## 分发给用户

### 方式1：ZIP压缩包
```bash
zip -r 玻注预约系统-Mac-v2.1.8.zip simple-web-package-mac-v2.1.8/
```

### 方式2：DMG镜像（更专业）
```bash
brew install create-dmg
create-dmg \
  --volname "玻注预约系统 v2.1.8" \
  --window-pos 200 120 \
  --window-size 800 400 \
  "玻注预约系统-Mac-v2.1.8.dmg" \
  "simple-web-package-mac-v2.1.8/"
```

## 用户使用方法

Mac用户收到压缩包后：

1. 解压缩文件
2. 双击 `启动服务.sh`
3. 如果提示"无法验证开发者"：
   - 右键点击 `启动服务.sh`
   - 选择"打开"
   - 在弹出对话框中点击"打开"
4. 浏览器会自动打开系统页面
5. 使用 admin/admin123 登录

## 注意事项

### Apple Silicon (M1/M2) 支持
- 在M1/M2 Mac上打包会自动生成ARM64版本
- 该版本只能在M1/M2 Mac上运行
- 如需同时支持Intel Mac，需要在Intel Mac上打包

### 同时支持Intel和Apple Silicon
如果需要创建通用版本（Universal Binary）：

```bash
# 方法1：在Intel Mac上打包（推荐）
# 生成的文件可在所有Mac上运行

# 方法2：使用universal2（需要额外配置）
# 修改 build_mac.spec，添加：
# target_arch='universal2'
```

### 代码签名（可选）
如果你有Apple Developer账号，建议进行代码签名：

```bash
codesign --force --deep --sign "Developer ID Application: Your Name" \
  simple-web-package-mac-v2.1.8/backend_server
```

这样用户就不会看到"无法验证开发者"的警告。

## 常见问题

**Q: 我没有Mac电脑怎么办？**  
A: 可以：
1. 借用朋友的Mac打包
2. 使用云端Mac服务（如MacStadium、AWS Mac实例）
3. 提供源码版本，让Mac用户自行运行

**Q: 打包需要多长时间？**  
A: 首次打包约5-10分钟（包括下载依赖）

**Q: 打包后的文件有多大？**  
A: 约50-80MB（包含所有依赖）

**Q: 能在虚拟机中打包吗？**  
A: 理论上可以，但需要macOS虚拟机，配置较复杂

## 详细文档

更多详细信息请查看：
- [Mac打包教程.md](./Mac打包教程.md) - 完整的打包教程
- [使用说明.txt](./simple-web-package-mac-v2.1.8/使用说明.txt) - 用户使用说明

## 技术支持

如有问题，请提供：
1. macOS版本（系统偏好设置 > 关于本机）
2. 芯片类型（Intel 或 Apple Silicon）
3. 错误截图或日志

---

**提示**: 如果你只是想让Mac用户使用系统，最简单的方式是部署服务器Web版本，Mac用户通过浏览器访问即可，无需打包。
