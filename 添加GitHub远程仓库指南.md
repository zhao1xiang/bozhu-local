# 添加GitHub作为第二个远程仓库

## 为什么要添加GitHub？

1. ✅ **免费的Mac构建环境**（GitHub Actions）
2. ✅ **无限制的构建次数**（公开仓库）
3. ✅ **自动化打包**
4. ✅ **保留阿里云CodeUp**（两个仓库同时使用）

## 操作步骤

### 1. 在GitHub上创建仓库

1. 访问 https://github.com
2. 登录你的GitHub账号（如果没有，先注册一个）
3. 点击右上角的 "+" -> "New repository"
4. 填写信息：
   - Repository name: `bozhu_local`（或其他名称）
   - Description: 玻注预约系统
   - Public（公开，才能免费使用Actions）
   - 不要勾选"Initialize this repository with a README"
5. 点击 "Create repository"

### 2. 添加GitHub为第二个远程仓库

在你的项目目录执行：

```powershell
# 添加GitHub远程仓库（将<your-username>替换为你的GitHub用户名）
git remote add github https://github.com/<your-username>/bozhu_local.git

# 查看所有远程仓库
git remote -v
```

你会看到：
```
origin  https://codeup.aliyun.com/63914d8e75a504a00af19331/bozhu_local.git (fetch)
origin  https://codeup.aliyun.com/63914d8e75a504a00af19331/bozhu_local.git (push)
github  https://github.com/<your-username>/bozhu_local.git (fetch)
github  https://github.com/<your-username>/bozhu_local.git (push)
```

### 3. 推送代码到GitHub

```powershell
# 首次推送
git push github master

# 如果需要设置上游分支
git push -u github master
```

### 4. 在GitHub上触发Actions

1. 打开你的GitHub仓库页面
2. 点击 "Actions" 标签
3. 如果看到提示，点击 "I understand my workflows, go ahead and enable them"
4. 选择 "Build Mac Version" workflow
5. 点击 "Run workflow"
6. 选择 "master" 分支
7. 点击绿色的 "Run workflow" 按钮

### 5. 等待构建完成

- 构建时间：约10-15分钟
- 可以实时查看构建日志
- 构建完成后，在 "Artifacts" 中下载 `mac-package`

## 日常使用

### 同时推送到两个仓库

方法1：分别推送
```powershell
git push origin master   # 推送到阿里云CodeUp
git push github master   # 推送到GitHub
```

方法2：创建一个推送所有的命令
```powershell
# 创建别名
git config alias.pushall '!git push origin master && git push github master'

# 使用
git pushall
```

方法3：配置push到多个仓库
```powershell
# 修改origin，让它推送到两个地方
git remote set-url --add --push origin https://codeup.aliyun.com/63914d8e75a504a00af19331/bozhu_local.git
git remote set-url --add --push origin https://github.com/<your-username>/bozhu_local.git

# 之后只需要
git push origin master  # 会同时推送到两个仓库
```

## 使用GitHub Actions打包

### 手动触发
1. 推送代码到GitHub
2. 访问 GitHub仓库 -> Actions
3. 选择 "Build Mac Version"
4. 点击 "Run workflow"
5. 下载构建产物

### 自动触发（推送tag时）
```powershell
# 创建tag
git tag v2.1.8

# 推送tag到GitHub
git push github v2.1.8

# GitHub Actions会自动开始构建
# 构建完成后会自动创建Release
```

## 安全建议

### 使用Personal Access Token

为了安全，建议使用Token而不是密码：

1. GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. Generate new token
3. 勾选 `repo` 权限
4. 生成并复制token

使用token推送：
```powershell
# 方式1：在URL中使用token
git remote set-url github https://<token>@github.com/<username>/bozhu_local.git

# 方式2：使用Git凭据管理器（推荐）
git push github master
# 输入用户名和token（而不是密码）
```

### 私有仓库

如果不想公开代码：
1. 创建私有仓库（Private）
2. 免费账户每月有2000分钟Actions配额
3. Mac构建消耗10倍分钟数
4. 即：每月可以构建约20次

## 常见问题

### Q: 必须同时维护两个仓库吗？
A: 不是必须的，但推荐：
   - CodeUp：主要开发仓库（国内访问快）
   - GitHub：用于自动打包（免费Mac构建）

### Q: 会不会很麻烦？
A: 不会，配置好后：
   ```powershell
   git add .
   git commit -m "更新"
   git push origin master   # 推送到CodeUp
   git push github master   # 推送到GitHub（触发自动打包）
   ```

### Q: GitHub Actions构建失败怎么办？
A: 查看Actions日志，常见问题：
   - 依赖安装失败：检查requirements.txt
   - 前端构建失败：检查package.json
   - 权限问题：检查文件权限

### Q: 能只在GitHub上开发吗？
A: 可以，但：
   - 国内访问GitHub较慢
   - 建议保留CodeUp作为主仓库

## 推荐配置

最佳实践：
1. **主仓库**：阿里云CodeUp（日常开发）
2. **镜像仓库**：GitHub（自动打包）
3. **推送策略**：
   - 日常提交：只推送到CodeUp
   - 需要打包时：推送到GitHub
   - 发布版本时：推送tag到GitHub（自动打包+发布）

## 总结

添加GitHub作为第二个远程仓库的优势：
- ✅ 免费的Mac自动打包
- ✅ 保留CodeUp的国内访问速度
- ✅ 两个仓库互为备份
- ✅ 灵活选择推送目标

只需要：
1. 在GitHub创建仓库
2. 添加GitHub为远程仓库
3. 推送代码
4. 在GitHub Actions中点击"Run workflow"
5. 下载打包好的Mac版本

就这么简单！
