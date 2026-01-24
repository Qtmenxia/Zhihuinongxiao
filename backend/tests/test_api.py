"""
API端点测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查端点"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_farmer(client: AsyncClient):
    """测试农户注册"""
    payload = {
        "name": "测试农户",
        "phone": "13900000001",
        "password": "test123456",
        "email": "test@example.com",
        "province": "山西省",
        "city": "临汾市",
        "county": "蒲县",
        "village": "测试村"
    }
    
    response = await client.post("/api/v1/farmers/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["farmer"]["phone"] == "13900000001"


@pytest.mark.asyncio
async def test_login_farmer(client: AsyncClient):
    """测试农户登录"""
    # 先注册
    register_payload = {
        "name": "登录测试",
        "phone": "13900000002",
        "password": "test123456",
        "email": "login@example.com",
        "province": "山西省",
        "city": "临汾市",
        "county": "蒲县",
        "village": "测试村"
    }
    await client.post("/api/v1/farmers/register", json=register_payload)
    
    # 登录
    login_payload = {
        "phone": "13900000002",
        "password": "test123456"
    }
    
    response = await client.post("/api/v1/farmers/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_get_products(client: AsyncClient):
    """测试获取产品列表（公开访问）"""
    response = await client.get("/api/v1/products?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_estimate_cost(client: AsyncClient, auth_headers: dict):
    """测试成本估算"""
    payload = {
        "user_input": "我需要一个订单查询工具",
        "model": "gemini-2.5-pro"
    }
    
    response = await client.post(
        "/api/v1/services/estimate-cost",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "estimated_cost_usd" in data
    assert "estimated_tokens" in data


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """测试未授权访问"""
    response = await client.get("/api/v1/farmers/me")
    assert response.status_code == 401
