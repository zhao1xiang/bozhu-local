#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包和部署脚本
用法: python build_and_deploy.py
"""
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

# 设置输出编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)

def print_success(text):
    """打印成功信息"""
    print(f"[OK] {text}")

def print_error(text):
    """打印错误信息"""
    print(f"[ERROR] {text}")

def print_warning(text):
    """打印警告信息"""
    print(f"[WARN] {text}")

def safe_rmtree(path, max_retries=3):
    """安全删除目录，处理权限问题"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                return True
        except PermissionError:
            if attempt < max_retries - 1:
                print_warning(f"权限被拒绝，等待后重试... ({attempt + 1}/{max_retries})")
                time.sleep(1)
            else:
                print_error(f"无法删除 {path}，请手动删除后重试")
                return False
    return False

def main():
    print_header("眼科注射预约系统 - 打包和部署脚本")
    
    # 检查 PyInstaller
    print("\n检查 PyInstaller...")
    try:
        result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True)
        print_success(f"PyInstaller 已安装: {result.stdout.strip()}")
    except FileNotFoundError:
        print_error("PyInstaller 未安装，请先安装: pip install pyinstaller")
        sys.exit(1)
    
    # 清理旧的构建文件
    print("\n清理旧的构建文件...")
    for dir_name in ["build", "dist", "bozhu-client-win"]:
        if os.path.exists(dir_name):
            if safe_rmtree(dir_name):
                print_success(f"已删除 {dir_name} 目录")
            else:
                print_warning(f"跳过删除 {dir_name}（可能被占用）")
    
    # 开始打包
    print("\n开始打包...")
    result = subprocess.run(["pyinstaller", "build_web_server.spec"], capture_output=False)
    
    if result.returncode != 0:
        print_error("打包失败！")
        sys.exit(1)
    
    print_success("打包成功！")
    
    # 创建最终的发布目录结构
    print("\n创建发布目录结构...")
    release_dir = "bozhu-client-win"
    os.makedirs(release_dir, exist_ok=True)
    print_success(f"已创建目录: {release_dir}")
    
    # 查找 exe 文件
    print("\n查找 exe 文件...")
    exe_source = None
    
    # 尝试多个可能的位置
    possible_paths = [
        os.path.join("dist", "backend_server.exe"),
        os.path.join("dist", "backend_server", "backend_server.exe"),
        os.path.join("dist", "眼科注射预约系统-Web版.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            exe_source = path
            print_success(f"找到 exe: {path}")
            break
    
    if not exe_source:
        print_error(f"找不到 exe 文件，已尝试的位置:")
        for path in possible_paths:
            print(f"  - {path}")
        print_error("请检查 dist 目录中的文件")
        sys.exit(1)
    
    # 复制 exe 文件
    print("\n复制 exe 文件...")
    exe_dest = os.path.join(release_dir, "backend_server.exe")
    
    try:
        shutil.copy2(exe_source, exe_dest)
        print_success(f"已复制 exe: {exe_dest}")
    except Exception as e:
        print_error(f"复制 exe 失败: {e}")
        sys.exit(1)
    
    # 复制前端文件
    print("\n复制前端文件...")
    frontend_source = os.path.join("..", "frontend", "dist")
    frontend_dest = os.path.join(release_dir, "frontend")
    
    if os.path.exists(frontend_source):
        if os.path.exists(frontend_dest):
            safe_rmtree(frontend_dest)
        try:
            shutil.copytree(frontend_source, frontend_dest)
            print_success(f"前端文件已复制到: {frontend_dest}")
        except Exception as e:
            print_error(f"复制前端文件失败: {e}")
            sys.exit(1)
    else:
        print_error(f"前端文件不存在: {frontend_source}")
        sys.exit(1)
    
    # 复制数据库文件（如果存在）
    print("\n复制数据库文件...")
    db_source = "database.db"
    db_dest = os.path.join(release_dir, "database.db")
    
    if os.path.exists(db_source):
        try:
            shutil.copy2(db_source, db_dest)
            print_success(f"数据库已复制到: {db_dest}")
        except Exception as e:
            print_warning(f"复制数据库失败: {e}")
    else:
        print_warning(f"数据库文件不存在: {db_source}（首次运行时会自动创建）")
    
    # 显示最终目录结构
    print("\n最终目录结构:")
    for root, dirs, files in os.walk(release_dir):
        level = root.replace(release_dir, "").count(os.sep)
        indent = " " * 2 * level
        dir_name = os.path.basename(root) if os.path.basename(root) else release_dir
        print(f"{indent}[DIR] {dir_name}/")
        subindent = " " * 2 * (level + 1)
        for file in sorted(files):
            file_size = os.path.getsize(os.path.join(root, file))
            size_str = f"{file_size / (1024*1024):.1f}MB" if file_size > 1024*1024 else f"{file_size / 1024:.1f}KB"
            print(f"{subindent}[FILE] {file} ({size_str})")
    
    print_header("打包完成！")
    print(f"发布目录: {release_dir}")
    print(f"  ├── backend_server.exe")
    print(f"  ├── frontend/")
    print(f"  └── database.db (可选)")
    print("\n使用方法:")
    print(f"  1. 进入 {release_dir} 目录")
    print(f"  2. 双击 backend_server.exe 运行")
    print("=" * 50)

if __name__ == "__main__":
    main()
