@echo off
chcp 65001 >nul
echo 启动后端服务...
cd backend
call .venv\Scripts\activate
python main.py
pause
