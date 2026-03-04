#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 API 接口"""

import urllib.request
import urllib.parse
import json

print("=" * 60)
print("测试后端 API")
print("=" * 60)

# 测试健康检查
print("\n1. 测试健康检查接口")
try:
    with urllib.request.urlopen("http://localhost:8000/api/health") as response:
        data = json.loads(response.read().decode())
        print(f"   ✅ 健康检查成功: {data}")
except Exception as e:
    print(f"   ❌ 健康检查失败: {e}")

# 测试登录接口
print("\n2. 测试登录接口")
try:
    url = "http://localhost:8000/api/auth/token"
    data = urllib.parse.urlencode({
        'username': 'admin',
        'password': 'admin'
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"   ✅ 登录成功!")
        print(f"   Token: {result.get('access_token', 'N/A')[:50]}...")
        print(f"   Token 类型: {result.get('token_type', 'N/A')}")
except urllib.error.HTTPError as e:
    print(f"   ❌ 登录失败!")
    print(f"   状态码: {e.code}")
    print(f"   错误信息: {e.read().decode()}")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

print("\n" + "=" * 60)
