#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL Server 连接检测工具
"""
import pymssql
import sys
import os
import subprocess

# 连接配置
SERVER = "192.168.20.3"
PORT = 1433
USER = "sqldy"
PASSWORD = "sqldy"
DATABASE = "portal_his"
VIEW = "V_YDHL_BRXX"

def print_header():
    print("=" * 50)
    print("SQL Server 连接检测工具")
    print("=" * 50)

def test_ping():
    """测试服务器是否可达"""
    print(f"1. 检测服务器 {SERVER} 是否可达...")
    try:
        result = subprocess.run(['ping', '-n', '1', SERVER], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("[成功] 服务器可以 ping 通")
            return True
        else:
            print("[失败] 服务器无法 ping 通")
            return False
    except Exception as e:
        print(f"[错误] ping 测试失败: {e}")
        return False

def test_port():
    """测试端口是否开放"""
    print(f"2. 检测端口 {PORT}...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((SERVER, PORT))
        sock.close()
        
        if result == 0:
            print("[成功] 端口可用")
            return True
        else:
            print("[失败] 端口不可用")
            return False
    except Exception as e:
        print(f"[错误] 端口测试失败: {e}")
        return False

def test_connection():
    """测试 SQL Server 连接"""
    print("3. 检测 SQL Server 连接...")
    try:
        # 方式1：host:port 格式
        conn = pymssql.connect(
            host=f"{SERVER}:{PORT}",
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            charset='cp936',
            timeout=10
        )
        print("[成功] SQL Server 连接成功 (host:port 方式)")
        conn.close()
        return True
    except Exception as e1:
        print(f"[失败] host:port 方式连接失败: {e1}")
        
        # 方式2：分别传 host 和 port
        try:
            conn = pymssql.connect(
                host=SERVER,
                port=PORT,
                user=USER,
                password=PASSWORD,
                database=DATABASE,
                charset='cp936',
                timeout=10
            )
            print("[成功] SQL Server 连接成功 (分别传参方式)")
            conn.close()
            return True
        except Exception as e2:
            print(f"[失败] 分别传参方式也失败: {e2}")
            return False

def test_database():
    """测试数据库是否存在"""
    print("4. 检测数据库是否存在...")
    try:
        conn = pymssql.connect(
            host=f"{SERVER}:{PORT}",
            user=USER,
            password=PASSWORD,
            charset='cp936',
            timeout=10
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{DATABASE}'")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            print(f"[成功] 数据库 {DATABASE} 存在")
            return True
        else:
            print(f"[失败] 数据库 {DATABASE} 不存在")
            return False
    except Exception as e:
        print(f"[错误] 数据库检测失败: {e}")
        return False

def test_view():
    """测试视图是否存在"""
    print("5. 检测视图是否存在...")
    try:
        conn = pymssql.connect(
            host=f"{SERVER}:{PORT}",
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            charset='cp936',
            timeout=10
        )
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.VIEWS 
            WHERE TABLE_NAME = '{VIEW}'
        """)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            print(f"[成功] 视图 {VIEW} 存在")
            return True
        else:
            print(f"[失败] 视图 {VIEW} 不存在")
            return False
    except Exception as e:
        print(f"[错误] 视图检测失败: {e}")
        return False

def test_query():
    """测试查询数据"""
    print("6. 尝试查询数据...")
    try:
        conn = pymssql.connect(
            host=f"{SERVER}:{PORT}",
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            charset='cp936',
            timeout=10
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP 1 * FROM {VIEW}")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            print(f"[成功] 查询成功，视图有数据")
            print(f"        第一行数据: {result}")
            return True
        else:
            print(f"[警告] 查询成功，但视图无数据")
            return True
    except Exception as e:
        print(f"[错误] 查询失败: {e}")
        return False

def main():
    print_header()
    print(f"服务器: {SERVER}:{PORT}")
    print(f"用户: {USER}")
    print(f"数据库: {DATABASE}")
    print(f"视图: {VIEW}")
    print("=" * 50)
    
    tests = [
        test_ping,
        test_port,
        test_connection,
        test_database,
        test_view,
        test_query
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"检测完成: {passed}/{len(tests)} 项通过")
    print("=" * 50)
    
    if passed == len(tests):
        print("✅ 所有检测通过，连接正常")
    else:
        print("❌ 部分检测失败，请检查配置")
    
    input("按任意键退出...")

if __name__ == "__main__":
    main()