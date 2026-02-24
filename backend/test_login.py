import requests

# 测试登录接口
url = "http://localhost:8000/api/auth/token"
data = {
    "username": "admin",
    "password": "admin"
}

try:
    response = requests.post(url, data=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 登录成功！")
        print(f"Token: {response.json().get('access_token', 'N/A')}")
    else:
        print("❌ 登录失败！")
except Exception as e:
    print(f"❌ 请求失败: {e}")
