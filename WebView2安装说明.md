# WebView2 运行时安装说明

## 问题描述

如果您在启动"眼科注射预约系统"时遇到以下错误：
- "找不到 WebView2 运行时环境"
- "无法启动应用程序"
- 应用闪退或无法打开

这是因为系统缺少 Microsoft Edge WebView2 运行时组件。

## 解决方案

### 方式一：自动安装（推荐）

1. 双击运行 `安装WebView2.bat` 文件
2. 等待安装完成
3. 重新启动"眼科注射预约系统"

### 方式二：手动下载安装

1. 访问 Microsoft 官方下载页面：
   https://developer.microsoft.com/zh-cn/microsoft-edge/webview2/

2. 下载"常青版独立安装程序"（Evergreen Standalone Installer）
   - 64位系统：MicrosoftEdgeWebview2Setup.exe
   - 32位系统：MicrosoftEdgeWebview2Setup_x86.exe

3. 运行安装程序，按提示完成安装

4. 重新启动"眼科注射预约系统"

### 方式三：在线安装

运行以下命令（需要管理员权限）：

```cmd
powershell -Command "& {Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile 'MicrosoftEdgeWebview2Setup.exe'; Start-Process -FilePath '.\MicrosoftEdgeWebview2Setup.exe' -Wait; Remove-Item '.\MicrosoftEdgeWebview2Setup.exe'}"
```

## 系统要求

- Windows 7 SP1 或更高版本
- Windows Server 2008 R2 或更高版本
- 需要联网（首次安装时）

## 常见问题

### Q: 为什么需要 WebView2？
A: 眼科注射预约系统使用现代 Web 技术构建界面，WebView2 是 Microsoft 提供的浏览器引擎，用于在桌面应用中显示网页内容。

### Q: WebView2 安全吗？
A: 是的，WebView2 是 Microsoft 官方提供的组件，与 Microsoft Edge 浏览器使用相同的技术，定期更新以确保安全性。

### Q: 安装后占用多少空间？
A: 约 100-150 MB，会自动更新以保持最新版本。

### Q: 可以卸载吗？
A: 可以，但卸载后本系统将无法运行。建议保留。

### Q: 已经安装了 Microsoft Edge，还需要安装吗？
A: 是的，WebView2 运行时是独立的组件，即使已安装 Edge 浏览器也需要单独安装。

## 技术支持

如果按照以上步骤仍无法解决问题，请联系技术支持：
- 提供错误截图
- 提供系统版本信息（Win+R 输入 winver 查看）
