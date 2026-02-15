# -*- coding: utf-8 -*-
"""
测试登录API
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录"""
    print("\n" + "=" * 80)
    print("测试登录API")
    print("=" * 80)
    
    # 登录数据
    login_data = {
        "phone": "13800138000",
        "password": "demo123456"
    }
    
    print(f"\n发送登录请求...")
    print(f"URL: {BASE_URL}/farmers/login")
    print(f"数据: {json.dumps(login_data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/farmers/login",
            json=login_data,
            timeout=10
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] 登录成功！")
            print(f"Token: {result['access_token'][:50]}...")
            print(f"农户信息:")
            print(f"  - ID: {result['farmer']['id']}")
            print(f"  - 姓名: {result['farmer']['name']}")
            print(f"  - 手机: {result['farmer']['phone']}")
            print(f"  - 等级: {result['farmer']['tier']}")
            print(f"  - 邮箱: {result['farmer']['email']}")
            
            # 测试获取用户信息
            print("\n" + "=" * 80)
            print("测试获取用户信息API")
            print("=" * 80)
            
            headers = {
                "Authorization": f"Bearer {result['access_token']}"
            }
            
            me_response = requests.get(
                f"{BASE_URL}/farmers/me",
                headers=headers,
                timeout=10
            )
            
            print(f"\n响应状态码: {me_response.status_code}")
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                print("\n[SUCCESS] 获取用户信息成功！")
                print(f"用户信息: {json.dumps(me_data, ensure_ascii=False, indent=2)}")
            else:
                print(f"\n[ERROR] 获取用户信息失败")
                print(f"错误: {me_response.text}")
                
        else:
            print(f"\n[ERROR] 登录失败")
            print(f"错误: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] 无法连接到后端服务")
        print("请确保后端服务正在运行: python -m uvicorn backend.api.main:app --reload")
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_login()

