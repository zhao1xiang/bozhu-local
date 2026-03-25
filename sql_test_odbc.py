#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL Server 连接检测工具 (使用 pyodbc)
"""
import pyodbc
import sys
import os
import subprocess

# 连接配置
SERVER = "192.168.0.94"
PORT = 1433
USER = "bz"
PASSWORD = "BZBC@2026"
DATABASE = "BZ"
VIEW = "getPatientInfo"

def print_header():
    print("=" * 50)
    print("SQL Server 连接检测工具 (ODBC)")
    print("=" * 50)

def test_ping():
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

def list_drivers():
    print("3. 检测 ODBC 驱动...")
    try:
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_drivers:
            print(f"[成功] 找到 SQL Server 驱动: {sql_drivers}")
            return sql_drivers[0]
        else:
            print(f"[警告] 未找到 SQL Server 驱动，可用驱动: {drivers}")
            return None
    except Exception as e:
        print(f"[错误] 驱动检测失败: {e}")
        return None

def make_conn(driver, database=DATABASE):
    """尝试多种连接格式，返回成功的连接，失败抛出最后一个异常"""
    conn_strs = [
        f"DRIVER={{{driver}}};SERVER={SERVER},{PORT};DATABASE={database};UID={USER};PWD={PASSWORD};Timeout=10;",
        f"DRIVER={{{driver}}};SERVER={SERVER};PORT={PORT};DATABASE={database};UID={USER};PWD={PASSWORD};Timeout=10;",
        f"DRIVER={{{driver}}};SERVER=tcp:{SERVER},{PORT};DATABASE={database};UID={USER};PWD={PASSWORD};Timeout=10;",
        # 旧版 SQL Server 驱动（DBNETLIB）只认不带端口的 host
        f"DRIVER={{{driver}}};SERVER={SERVER};DATABASE={database};UID={USER};PWD={PASSWORD};Timeout=10;",
    ]
    last_err = None
    for conn_str in conn_strs:
        try:
            return pyodbc.connect(conn_str, timeout=10)
        except Exception as e:
            last_err = e
    raise last_err


def test_connection(driver):
    print("4. 检测 SQL Server 连接...")
    if not driver:
        print("[跳过] 无可用驱动")
        return False
    try:
        conn = make_conn(driver)
        print("[成功] SQL Server 连接成功")
        conn.close()
        return True
    except Exception as e:
        print(f"[失败] 连接失败: {e}")
        return False

def test_database(driver):
    print("5. 检测数据库是否存在...")
    if not driver:
        return False
    try:
        conn = make_conn(driver, database="master")
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

def test_view(driver):
    print("6. 检测视图是否存在...")
    if not driver:
        return False
    try:
        conn = make_conn(driver)
        cursor = conn.cursor()
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = '{VIEW}'")
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

def test_query(driver):
    print("7. 尝试查询数据...")
    if not driver:
        return False
    try:
        conn = make_conn(driver)
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP 1 * FROM {VIEW}")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            print(f"[成功] 查询成功，视图有数据")
            print(f"       第一行: {result}")
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

    passed = 0

    if test_ping(): passed += 1
    print()
    if test_port(): passed += 1
    print()

    driver = list_drivers()
    if driver: passed += 1
    print()

    if driver:
        if test_connection(driver): passed += 1
        print()
        if test_database(driver): passed += 1
        print()
        if test_view(driver): passed += 1
        print()
        if test_query(driver): passed += 1
        print()

    print("=" * 50)
    print(f"检测完成: {passed}/7 项通过")
    print("=" * 50)
    if passed == 7:
        print("✅ 所有检测通过，连接正常")
    else:
        print("❌ 部分检测失败，请检查配置")

    input("按任意键退出...")

if __name__ == "__main__":
    main()
