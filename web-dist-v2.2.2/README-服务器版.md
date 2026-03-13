# 眼科注射预约系统 v2.2.2 - 服务器版

## 部署说明

### 环境要求
- Python 3.7+
- Node.js 18+ (如需重新构建前端)

### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 启动服务

#### 前台启动（开发/调试模式）
```bash
# 给脚本添加执行权限
chmod +x *.sh

# 前台启动（可以看到实时日志）
./start_production.sh
```

#### 后台启动（生产模式）
```bash
# 后台启动服务
./start_background.sh

# 检查服务状态
./check_status.sh

# 停止服务
./stop_server.sh

# 重启服务
./restart_server.sh
```

#### 手动启动
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8031
```

### 访问地址
- 本地访问：http://localhost:8031
- 服务器访问：http://服务器IP:8031

### 版本更新内容 v2.2.2
- ✅ 修复局域网访问时前端路由 404 问题
- ✅ 修复局域网访问时 API 端口错误
- ✅ 修复患者新增预约时矫正视力没有带过去的问题
- ✅ 修复药物多选时批量预约功能消失的问题
- ✅ 修复预约时间段默认值，现在默认为"上午"
- ✅ 修复从患者列表点预约时批量预约提示不显示的问题
- ✅ 修复工作台约针率计算逻辑，现在更准确反映实际约针情况
- ✅ 调整打印页面复诊电话字体大小和位置
- ✅ 修复视力字段类型问题，支持字符串格式视力值
- ✅ 添加 SPA 路由回退机制，支持所有前端路由
- ✅ 后端监听 0.0.0.0，支持局域网多台电脑访问
- ✅ 前端自动检测访问 IP 类型（本地/局域网）
- ✅ 自动数据库迁移，保留所有历史数据

### 默认账号
- 用户名：admin
- 密码：admin

### 服务管理脚本

系统提供了完整的服务管理脚本：

- **start_production.sh** - 前台启动（开发/调试模式）
- **start_background.sh** - 后台启动（生产模式）
- **stop_server.sh** - 停止服务
- **restart_server.sh** - 重启服务
- **check_status.sh** - 检查服务状态

#### 生产环境推荐使用后台模式：
```bash
# 启动
./start_background.sh

# 检查状态
./check_status.sh

# 查看日志
tail -f backend/logs/server.log

# 停止
./stop_server.sh
```

### 注意事项
1. 首次部署时给脚本添加执行权限：`chmod +x *.sh`
2. 首次启动会自动创建数据库和默认用户
2. 请及时修改默认密码
3. 定期备份 database.db 文件
4. 确保防火墙开放 8031 端口