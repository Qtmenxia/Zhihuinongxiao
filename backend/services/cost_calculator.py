"""
成本计算服务
提供成本估算和账单生成功能
"""
import logging
from typing import Optional, Dict
from datetime import datetime
from dateutil.relativedelta import relativedelta

from backend.mcpybarra_core.framework.mcp_swe_flow.config import COST_PER_MILLION_TOKENS

logger = logging.getLogger(__name__)


class CostCalculator:
    """成本计算器"""
    
    # 定价策略(参考MCPybarra论文数据)
    PRICING_TIERS = {
        "free": {
            "max_services": 3,
            "max_requests_per_day": 100,
            "price": 0,
            "features": ["基础功能"]
        },
        "basic": {
            "max_services": 10,
            "max_requests_per_day": 1000,
            "price": 9.9,  # 美元/月
            "features": ["智能客服", "订单管理", "库存同步"]
        },
        "professional": {
            "max_services": 50,
            "max_requests_per_day": 10000,
            "price": 49.9,
            "features": ["全功能", "优先支持", "自定义集成", "数据分析"]
        }
    }
    
    # 汇率(应从实时API获取)
    USD_TO_CNY = 7.2
    
    def estimate_generation_cost(
        self,
        requirement: str,
        model: str = "gemini-2.5-pro"
    ) -> dict:
        """
        估算服务生成成本(基于需求复杂度)
        
        Args:
            requirement: 需求描述
            model: LLM模型
            
        Returns:
            dict: 成本估算结果
        """
        # 简化版本：根据需求长度估算token消耗
        # 实际应该使用tokenizer进行精确计算
        requirement_tokens = len(requirement) * 2  # 粗略估算
        
        # MCPybarra工作流大约会扩展50-100倍的token
        estimated_total_tokens = requirement_tokens * 75
        
        # 分配输入输出token(假设3:7比例)
        input_tokens = int(estimated_total_tokens * 0.3)
        output_tokens = int(estimated_total_tokens * 0.7)
        
        # 获取模型价格
        if model not in COST_PER_MILLION_TOKENS:
            logger.warning(f"Unknown model {model}, using gemini-2.5-pro pricing")
            model = "gemini-2.5-pro"
        
        pricing = COST_PER_MILLION_TOKENS[model]
        
        # 计算成本
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost_usd = input_cost + output_cost
        
        return {
            "estimated_cost_usd": round(total_cost_usd, 4),
            "estimated_cost_cny": round(total_cost_usd * self.USD_TO_CNY, 2),
            "estimated_tokens": estimated_total_tokens,
            "model": model,
            "breakdown": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": round(input_cost, 4),
                "output_cost": round(output_cost, 4)
            }
        }
    
    async def generate_monthly_bill(
        self,
        farmer_id: str,
        month: str  # 格式: "2026-01"
    ) -> dict:
        """
        生成农户月度账单
        
        Args:
            farmer_id: 农户ID
            month: 月份(YYYY-MM格式)
            
        Returns:
            dict: 账单详情
        """
        from backend.database.connection import AsyncSessionLocal
        from backend.models.farmer import Farmer
        from backend.models.mcp_service import MCPService
        from backend.models.order import Order
        from sqlalchemy import select, func, and_
        
        # 解析月份
        year, month_num = map(int, month.split('-'))
        start_date = datetime(year, month_num, 1)
        end_date = start_date + relativedelta(months=1)
        
        async with AsyncSessionLocal() as db:
            # 获取农户信息
            result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
            farmer = result.scalar_one()
            
            # 1. 统计服务生成成本
            stmt = select(func.sum(MCPService.generation_cost)).where(
                and_(
                    MCPService.farmer_id == farmer_id,
                    MCPService.created_at >= start_date,
                    MCPService.created_at < end_date
                )
            )
            result = await db.execute(stmt)
            total_generation_cost = result.scalar() or 0.0
            
            # 2. 统计API调用费用(假设每次$0.001)
            # 实际应该从service_logs表统计
            api_calls = 0  # 简化处理
            api_cost = api_calls * 0.001
            
            # 3. 订阅费用
            subscription_fee = self.PRICING_TIERS[farmer.tier.value]["price"]
            
            # 4. 计算交易抽成(如果开启)
            commission = 0.0
            if farmer.enable_commission:
                stmt = select(func.sum(Order.total_amount)).where(
                    and_(
                        Order.farmer_id == farmer_id,
                        Order.created_at >= start_date,
                        Order.created_at < end_date,
                        Order.status == "completed"
                    )
                )
                result = await db.execute(stmt)
                total_sales = result.scalar() or 0.0
                commission = total_sales * (farmer.commission_rate / 1000)
            
            # 计算总计
            total_usd = total_generation_cost + api_cost + subscription_fee + commission
            
            return {
                "farmer_id": farmer_id,
                "farmer_name": farmer.name,
                "month": month,
                "tier": farmer.tier.value,
                "breakdown": {
                    "service_generation": round(total_generation_cost, 2),
                    "api_calls": round(api_cost, 2),
                    "subscription": round(subscription_fee, 2),
                    "commission": round(commission, 2)
                },
                "total_usd": round(total_usd, 2),
                "total_cny": round(total_usd * self.USD_TO_CNY, 2),
                "currency": "USD",
                "generated_at": datetime.utcnow().isoformat()
            }
