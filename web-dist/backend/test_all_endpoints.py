#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试所有主要 API 接口"""

import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, method='GET', data=None, headers=None, token=None):
    """测试单个接口"""
    print(f"\n测试: {name}")
    print(f"URL: {url}")
    
    try:
        if headers is None:
            headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        if data:
            data = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"✅ 成功 (状态码: {response.status})")
            return result
    except urllib.error.HTTPError as e:
        print(f"❌ 失败 (状态码: {e.code})")
        try:
            error_body = e.read().decode()
            print(f"错误详情: {error_body}")
        except:
            pass
        return None
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

print("=" * 70)
print("测试后端 API 接口")
print("=" * 70)

# 1. 测试健康检查
test_endpoint("健康检查", f"{BASE_URL}/api/health")

# 2. 测试登录
print("\n" + "=" * 70)
url = f"{BASE_URL}/api/auth/token"
data = urllib.parse.urlencode({
    'username': 'admin',
    'password': 'admin'
}).encode('utf-8')

req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        token = result.get('access_token')
        print(f"✅ 登录成功")
        print(f"Token: {token[:50]}...")
except Exception as e:
    print(f"❌ 登录失败: {e}")
    token = None

if token:
    # 3. 测试获取当前用户信息
    test_endpoint("获取当前用户", f"{BASE_URL}/api/auth/me", token=token)
    
    # 4. 测试获取患者列表
    test_endpoint("获取患者列表", f"{BASE_URL}/api/patients", token=token)
    
    # 5. 测试获取预约列表
    test_endpoint("获取预约列表", f"{BASE_URL}/api/appointments", token=token)
    
    # 6. 测试获取数据字典
    test_endpoint("获取数据字典", f"{BASE_URL}/api/data-dictionary", token=token)
    
    # 7. 测试获取系统设置
    test_endpoint("获取系统设置", f"{BASE_URL}/api/system-settings", token=token)
    
    # 8. 测试获取仪表板数据
    test_endpoint("获取仪表板统计", f"{BASE_URL}/api/dashboard/stats", token=token)

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
