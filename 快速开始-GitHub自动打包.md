# 快速开始：使用GitHub Actions自动打包Mac版本

## 🎯 目标
在不需要Mac电脑的情况下，自动打包Mac版本。

## ⏱️ 预计时间
首次设置：10分钟  
后续打包：5分钟（点击按钮即可）

## 📋 前提条件
- [x] 代码已在阿里云CodeUp上
- [ ] 需要一个GitHub账号（免费）

## 🚀 三步完成设置

### 步骤1：创建GitHub仓库（3分钟）

1. 访问 https://github.com/new
2. 填写：
   - Repository name: `bozhu_local`
   - 选择 **Public**（公开才能免费使用Actions）
   - 不要勾选任何初始化选项
3. 点击 "Create repository"

### 步骤2：推送代码到GitHub（2分钟）

在你的项目目录打开PowerShell，执行：

```powershell
# 添加GitHub远程仓库（替换<your-username>为你的GitHub用户名）
git remote add github https://github.com/<your-username>/bozhu_local.git

# 推送代码
git push github master
```

如果提示输入用户名和密码：
- 用户名：你的GitHub用户名
- 密码：使用Personal Access Token（不是GitHub密码）
  - 获取Token：GitHub -> Settings -> Developer settings -> Personal access tokens -> Generate new token
  - 勾选 `repo` 权限

### 步骤3：触发自动打包（5分钟）

1. 打开你的GitHub仓库页面
2. 点击顶部的 **"Actions"** 标签
3. 如果看到提示，点击 **"I understand my workflows, go ahead and enable them"**
4. 点击左侧的 **"Build Mac Version"**
5. 点击右侧的 **"Run workflow"** 按钮
6. 选择 **"master"** 分支
7. 点击绿色的 **"Run workflow"** 按钮

## ⏳ 等待构建

- 构建时间：10-15分钟
- 可以点击workflow查看实时日志
- 看到绿色✅表示成功

## 📦 下载打包结果

构建完成后：

1. 点击workflow运行记录
2. 滚动到底部，找到 **"Artifacts"** 部分
3. 点击 **"mac-package"** 下载
4. 解压ZIP文件
5. 得到 `simple-web-package-mac-v2.1.8` 目录

## ✅ 完成！

现在你有了Mac版本的打包文件，可以分发给Mac用户了。

## 📝 日常使用

### 方式1：手动触发打包

每次需要打包时：
```powershell
# 1. 提交代码
git add .
git commit -m "更新功能"

# 2. 推送到GitHub
git push github master

# 3. 在GitHub Actions页面点击"Run workflow"
```

### 方式2：自动打包（推荐）

推送版本tag时自动打包：
```powershell
# 1. 创建版本tag
git tag v2.1.9

# 2. 推送tag到GitHub
git push github v2.1.9

# 3. GitHub Actions自动开始打包
# 4. 打包完成后自动创建Release
# 5. 在Releases页面直接下载
```

## 🎁 额外福利

### 同时推送到CodeUp和GitHub

配置一次，以后一个命令推送到两个仓库：

```powershell
# 配置
git remote set-url --add --push origin https://codeup.aliyun.com/63914d8e75a504a00af19331/bozhu_local.git
git remote set-url --add --push origin https://github.com/<your-username>/bozhu_local.git

# 以后只需要
git push origin master  # 同时推送到CodeUp和GitHub
```

## ❓ 常见问题

### Q: 构建失败了怎么办？
A: 点击失败的workflow，查看日志找到错误原因。常见问题：
- 依赖安装失败：检查requirements.txt
- 前端构建失败：检查package.json

### Q: 能打包Windows版本吗？
A: 可以！修改workflow配置，添加Windows构建任务。

### Q: 需要付费吗？
A: 公开仓库完全免费，无限制使用。

### Q: 构建太慢了？
A: 首次构建需要下载依赖，约15分钟。后续构建有缓存，约5-8分钟。

### Q: 能在私有仓库使用吗？
A: 可以，但免费账户每月只有2000分钟配额。Mac构建消耗10倍，即每月约20次。

## 📚 更多信息

- [GitHub-Actions自动打包说明.md](./GitHub-Actions自动打包说明.md) - 详细教程
- [添加GitHub远程仓库指南.md](./添加GitHub远程仓库指南.md) - 仓库配置
- [阿里云云效打包说明.md](./阿里云云效打包说明.md) - 使用云效的方案

## 🎉 总结

使用GitHub Actions打包Mac版本：
- ✅ 无需Mac电脑
- ✅ 完全免费
- ✅ 全自动化
- ✅ 只需点击按钮

3步设置，5分钟打包，就这么简单！

---

**需要帮助？** 查看详细文档或联系技术支持。
