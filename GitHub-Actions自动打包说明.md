# 使用GitHub Actions自动打包Mac版本

## 什么是GitHub Actions？

GitHub Actions是GitHub提供的免费CI/CD服务，可以在云端的Mac虚拟机上自动打包你的应用。

## 优势

✅ **完全免费**（公开仓库）
✅ **无需Mac电脑**
✅ **自动化打包**
✅ **支持多平台**（可同时打包Windows、Mac、Linux）
✅ **可重复使用**

## 使用方法

### 方式1：手动触发打包

1. **推送配置文件到GitHub**
   ```bash
   git add .github/workflows/build-mac.yml
   git commit -m "添加GitHub Actions自动打包配置"
   git push
   ```

2. **在GitHub网站上触发**
   - 打开你的GitHub仓库
   - 点击 "Actions" 标签
   - 选择 "Build Mac Version"
   - 点击 "Run workflow"
   - 选择分支，点击 "Run workflow"

3. **等待打包完成**
   - 大约需要5-10分钟
   - 可以实时查看打包日志

4. **下载打包结果**
   - 打包完成后，点击workflow运行记录
   - 在 "Artifacts" 部分下载 `mac-package`
   - 解压即可得到Mac版本

### 方式2：自动打包（推送tag时）

1. **创建版本tag**
   ```bash
   git tag v2.1.8
   git push origin v2.1.8
   ```

2. **自动触发打包**
   - GitHub Actions会自动开始打包
   - 打包完成后自动创建Release
   - Mac版本会自动上传到Release

3. **下载Release**
   - 在GitHub仓库的 "Releases" 页面
   - 找到对应版本
   - 下载 `simple-web-package-mac-v2.1.8.zip`

## 配置说明

已创建的配置文件：`.github/workflows/build-mac.yml`

### 触发条件
```yaml
on:
  workflow_dispatch:  # 手动触发
  push:
    tags:
      - 'v*'  # 推送v开头的tag时自动触发
```

### 构建环境
- 运行在：`macos-latest`（最新的macOS）
- Python版本：3.9
- Node.js版本：18

### 构建步骤
1. 检出代码
2. 设置Python和Node.js环境
3. 构建前端（npm install & build）
4. 安装后端依赖
5. 使用PyInstaller打包后端
6. 创建发布包
7. 创建ZIP压缩包
8. 上传构建产物

## 查看构建日志

1. 打开GitHub仓库
2. 点击 "Actions" 标签
3. 点击具体的workflow运行记录
4. 可以看到每个步骤的详细日志

## 构建时间

- 首次构建：约10-15分钟（需要下载依赖）
- 后续构建：约5-8分钟（有缓存）

## 费用

- **公开仓库**：完全免费，无限制
- **私有仓库**：
  - 免费账户：每月2000分钟
  - Mac虚拟机：消耗10倍分钟数
  - 即：每次打包约消耗50-100分钟配额

## 同时打包多个平台

可以修改配置文件，同时打包Windows、Mac、Linux：

```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    # ... 其他配置
```

## 常见问题

### Q: 我的仓库是私有的，能用吗？
A: 可以，但会消耗GitHub Actions配额。免费账户每月2000分钟。

### Q: 打包失败怎么办？
A: 查看Actions日志，找到错误信息。常见问题：
   - 依赖安装失败：检查requirements.txt
   - 前端构建失败：检查package.json
   - PyInstaller失败：检查build_mac.spec

### Q: 能打包Intel和M1通用版本吗？
A: GitHub Actions的Mac虚拟机是Intel架构，生成的文件可以通过Rosetta 2在M1上运行。

### Q: 打包的文件在哪里？
A: 
   - 手动触发：在workflow运行记录的Artifacts中
   - Tag触发：在Releases页面

### Q: 能自动发布到其他地方吗？
A: 可以，修改workflow添加：
   - 上传到阿里云OSS
   - 上传到七牛云
   - 发送到企业微信/钉钉
   - 等等

## 高级配置

### 添加构建缓存
```yaml
- name: Cache pip
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

- name: Cache npm
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
```

### 添加通知
```yaml
- name: Send notification
  if: always()
  run: |
    curl -X POST "https://your-webhook-url" \
      -d "status=${{ job.status }}"
```

### 多版本打包
```yaml
strategy:
  matrix:
    python-version: ['3.7', '3.8', '3.9', '3.10']
```

## 示例：完整的多平台打包

创建 `.github/workflows/build-all.yml`：

```yaml
name: Build All Platforms

on:
  workflow_dispatch:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: windows-latest
            name: Windows
            artifact: windows-package
          - os: macos-latest
            name: Mac
            artifact: mac-package
          - os: ubuntu-latest
            name: Linux
            artifact: linux-package
    
    runs-on: ${{ matrix.os }}
    
    steps:
      # ... 构建步骤
      
      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.artifact }}
          path: package.zip
```

## 总结

使用GitHub Actions是**最推荐的方式**：
- ✅ 无需Mac电脑
- ✅ 完全免费（公开仓库）
- ✅ 自动化，可重复
- ✅ 支持多平台
- ✅ 有详细的构建日志

只需要：
1. 推送配置文件到GitHub
2. 在网页上点击"Run workflow"
3. 等待5-10分钟
4. 下载打包好的Mac版本

就这么简单！
