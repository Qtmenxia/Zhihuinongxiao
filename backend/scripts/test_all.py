"""
完整测试脚本 - 验证登录和订单API
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✓ 后端服务正常: {response.json()}")
            return True
        else:
            print(f"   ✗ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 无法连接后端: {e}")
        return False

def test_login(phone, password):
    """测试登录"""
    print(f"\n2. 测试登录 ({phone})...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/farmers/login",
            json={"phone": phone, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 登录成功")
            print(f"   - 农户: {data['farmer']['name']}")
            print(f"   - Token: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"   ✗ 登录失败: {response.status_code}")
            print(f"   - 错误: {response.text}")
            return None
    except Exception as e:
        print(f"   ✗ 登录请求失败: {e}")
        return None

def test_orders(token):
    """测试订单列表"""
    print(f"\n3. 测试订单列表...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/orders",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 获取订单成功")
            print(f"   - 订单总数: {data.get('total', 0)}")
            print(f"   - 当前页订单: {len(data.get('items', []))}")
            
            if data.get('items'):
                print(f"\n   订单列表:")
                for order in data['items'][:3]:  # 只显示前3个
                    print(f"   - {order['id']}: {order['status']} - ¥{order['total_amount']}")
            return True
        else:
            print(f"   ✗ 获取订单失败: {response.status_code}")
            print(f"   - 错误: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ 订单请求失败: {e}")
        return False

def test_products(token):
    """测试产品列表"""
    print(f"\n4. 测试产品列表...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/products",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 获取产品成功")
            print(f"   - 产品总数: {data.get('total', 0)}")
            print(f"   - 当前页产品: {len(data.get('items', []))}")
            
            if data.get('items'):
                print(f"\n   产品列表:")
                for product in data['items'][:3]:  # 只显示前3个
                    print(f"   - {product['name']}: ¥{product['price']} (库存: {product['stock']})")
            return True
        else:
            print(f"   ✗ 获取产品失败: {response.status_code}")
            print(f"   - 错误: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ 产品请求失败: {e}")
        return False

def main():
    """主测试流程"""
    print("=" * 60)
    print("智农链销 - 完整功能测试")
    print("=" * 60)
    
    # 测试健康检查
    if not test_health():
        print("\n❌ 后端服务未启动，请先启动后端服务！")
        print("\n启动命令:")
        print("cd E:\\gitlab\\Zhihuinongxiao")
        print(".\\backend\\venv\\Scripts\\python.exe -m backend.api.main")
        return
    
    # 测试所有账号
    test_accounts = [
        ("13800138000", "demo123456", "蒲县被子垣果园"),
        ("13800138001", "demo123456", "临汾红富士果园"),
        ("13800138002", "demo123456", "吉县壶口苹果园"),
    ]
    
    success_count = 0
    for phone, password, name in test_accounts:
        print(f"\n{'=' * 60}")
        print(f"测试账号: {name} ({phone})")
        print(f"{'=' * 60}")
        
        # 登录
        token = test_login(phone, password)
        if not token:
            continue
        
        # 测试订单
        orders_ok = test_orders(token)
        
        # 测试产品
        products_ok = test_products(token)
        
        if orders_ok and products_ok:
            success_count += 1
            print(f"\n✅ {name} 所有测试通过！")
    
    print(f"\n{'=' * 60}")
    print(f"测试完成: {success_count}/{len(test_accounts)} 个账号测试通过")
    print(f"{'=' * 60}")
    
    if success_count == len(test_accounts):
        print("\n🎉 所有测试通过！系统运行正常！")
        print("\n现在可以在浏览器中登录使用了:")
        print("- 前端地址: http://localhost:3000")
        print("- 使用任意测试账号登录")
    else:
        print("\n⚠️ 部分测试失败，请检查后端日志")

if __name__ == "__main__":
    main()

