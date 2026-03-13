# 眼科注射预约系统 - 服务器版 v2.2.3

## 系统要求
- Python 3.7 或更高版本
- Linux/Unix 系统（推荐 Ubuntu 18.04+）
- 至少 512MB 内存
- 100MB 磁盘空间

## 快速启动

### 方法一：使用管理脚本（推荐）
```bash
cd backend
chmod +x server_manager.sh
./server_manager.sh start
```

### 方法二：手动启动
```bash
cd backend
pip3 install -r requirements.txt
python3 main.py
```

## 服务器管理

### 启动服务
```bash
./server_manager.sh start
```

### 停止服务
```bash
./server_manager.sh stop
```

### 重启服务
```bash
./server_manager.sh restart
```

### 查看状态
```bash
./server_manager.sh status
```

## 访问系统
- 默认端口：8031
- 访问地址：http://服务器IP:8031
- 默认管理员账号：admin / admin123

## 配置说明

### 端口配置
如需修改端口，编辑 `backend/main.py` 文件中的端口设置：
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8031)
```

### 数据库
- 数据库文件：`backend/database.db`
- 自动备份：系统会在重要操作前自动备份数据库
- 手动备份：复制 `database.db` 文件即可

## 故障排除

### 端口被占用
```bash
# 查看端口占用
netstat -tlnp | grep 8031
# 或使用管理脚本自动处理
./server_manager.sh restart
```

### 数据库问题
如遇到数据库字段类型错误，运行修复脚本：
```bash
cd backend
python3 fix_database_schema.py
```

### 查看日志
```bash
tail -f backend/logs/backend.log
```

## 安全建议
1. 修改默认管理员密码
2. 配置防火墙，仅开放必要端口
3. 定期备份数据库文件
4. 使用 HTTPS（需要配置反向代理）

## 更新说明
- v2.2.3 新增自动数据库迁移功能
- 支持登录状态缓存
- 优化用户界面
- 修复 FastAPI lifespan 事件处理（解决启动警告）
- 详细更新内容请查看 `功能更新说明-v2.2.3.md`

## 技术支持
如遇问题，请检查：
1. Python 版本是否符合要求
2. 依赖包是否正确安装
3. 端口是否被占用
4. 数据库文件权限是否正确