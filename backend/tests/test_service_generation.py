"""
服务生成功能测试
"""
import pytest
from unittest.mock import AsyncMock, patch

from backend.services.service_manager import ServiceManager
from backend.services.cost_calculator import CostCalculator


@pytest.mark.asyncio
async def test_service_manager_initialization():
    """测试ServiceManager初始化"""
    manager = ServiceManager()
    assert manager.workflow is not None
    assert isinstance(manager.active_tasks, dict)


@pytest.mark.asyncio
async def test_cost_estimation():
    """测试成本估算"""
    calculator = CostCalculator()
    
    result = calculator.estimate_generation_cost(
        requirement="我需要一个简单的订单查询工具",
        model="gemini-2.5-pro"
    )
    
    assert "estimated_cost_usd" in result
    assert "estimated_tokens" in result
    assert result["estimated_cost_usd"] > 0
    assert result["model"] == "gemini-2.5-pro"


@pytest.mark.asyncio
@patch('backend.services.service_manager.create_mcp_swe_workflow')
async def test_start_generation(mock_workflow):
    """测试启动服务生成"""
    # Mock workflow
    mock_workflow.return_value.ainvoke = AsyncMock(return_value={
        "server_code": "# Generated code",
        "server_file_path": "/path/to/server.py",
        "api_name": "test_service",
        "readme_content": "# README",
        "requirements_content": "fastapi==0.109.0",
        "statistics_summary": {"total_cost": 0.25}
    })
    
    manager = ServiceManager()
    
    task_id = await manager.start_generation(
        user_input="创建一个订单查询工具",
        farmer_id="test_farmer_001",
        product_category="订单管理"
    )
    
    assert task_id.startswith("service_test_farmer_001_")
    assert task_id in manager.active_tasks


@pytest.mark.asyncio
async def test_pricing_tiers():
    """测试定价层级"""
    calculator = CostCalculator()
    
    assert calculator.PRICING_TIERS["free"]["max_services"] == 3
    assert calculator.PRICING_TIERS["basic"]["price"] == 9.9
    assert calculator.PRICING_TIERS["professional"]["max_services"] == 50
