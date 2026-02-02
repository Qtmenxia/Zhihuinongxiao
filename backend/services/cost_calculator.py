"""
成本计算服务
计算服务生成成本、订阅费用、API调用成本等
"""
from typing import Dict, Optional
from datetime import datetime, timezone
import logging

from backend.mcpybarra_core.framework.mcp_swe_flow.config import calculate_cost
from backend.mcpybarra_core.framework.mcp_swe_flow.config import get_provider_config
from backend.mcpybarra_core.framework.mcp_swe_flow.config import MODEL_CONFIG
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class CostCalculator:
    """成本计算器"""
    
    # 定价层级配置
    PRICING_TIERS = {
        "free": {
            "price": 0,
            "max_services": 3,
            "max_requests_per_day": 100,
            "features": ["基础功能", "3个免费服务"]
        },
        "basic": {
            "price": 9.9,
            "max_services": 10,
            "max_requests_per_day": 1000,
            "features": ["所有基础功能", "10个服务", "优先支持"]
        },
        "professional": {
            "price": 49.9,
            "max_services": 50,
            "max_requests_per_day": 10000,
            "features": ["所有功能", "50个服务", "专属客服", "数据分析"]
        }
    }
    
    def __init__(self):
        """初始化成本计算器"""
        self.default_model = settings.DEFAULT_SWE_MODEL
        logger.info(f"CostCalculator initialized with default model: {self.default_model}")
        
    def get_supported_models(self) -> list:
        """获取所有支持的模型列表"""
        models = []
        for pattern, config in MODEL_CONFIG.items():
            if pattern != "default":
                models.extend(config["costs"].keys())
        return [m for m in models if m != "default"]
    
    def validate_model(self, model: str) -> bool:
        """验证模型是否支持"""
        try:
            config = get_provider_config(model)
            return config is not None
        except Exception as e:
            logger.error(f"Error validating model {model}: {e}")
            return False
    
    def estimate_generation_cost(
        self,
        requirement: str,
        model: Optional[str] = None
    ) -> Dict:
        """
        估算服务生成成本
        
        Args:
            requirement: 用户需求描述
            model: 使用的LLM模型
            
        Returns:
            Dict: 包含估算成本和Token数量的字典
        """
        model = model or self.default_model
        
        # 根据需求长度粗略估算Token数量
        requirement_length = len(requirement)
        
        # Token估算规则（经验值）
        # 中文: 1字 ≈ 2 tokens
        # 英文: 1词 ≈ 1.3 tokens
        # MCPybarra工作流会有多轮对话，总Token数约为需求Token的30-50倍
        
        # 估算用户输入Token
        if any('\u4e00' <= char <= '\u9fff' for char in requirement):
            # 包含中文
            estimated_input_tokens = requirement_length * 2
        else:
            # 纯英文
            estimated_input_tokens = int(requirement_length / 4 * 1.3)
        
        # MCPybarra四阶段工作流的Token放大倍数
        # Planning: 5-10倍
        # Coding: 10-20倍
        # Testing: 5-10倍
        # Refining: 10-20倍（如果触发）
        # 总计约30-60倍，取中位数40倍
        total_input_tokens = estimated_input_tokens * 40
        
        # 输出Token约为输入Token的1.5倍（生成代码、测试报告等）
        total_output_tokens = int(total_input_tokens * 1.5)
        
        # ✅ 修正：config.py 的 calculate_cost 签名是 (model_name, prompt_tokens, completion_tokens)
        cost_result = calculate_cost(
            model_name=model,
            prompt_tokens=total_input_tokens,
            completion_tokens=total_output_tokens
        )
        
        estimated_cost = cost_result["total_cost"]
        
        logger.info(
            f"Cost estimation: requirement_length={requirement_length}, "
            f"prompt_tokens={total_input_tokens}, completion_tokens={total_output_tokens}, "
            f"model={model}, cost=${estimated_cost:.4f}"
        )
        
        return {
            "estimated_cost_usd": round(estimated_cost, 4),
            "estimated_cost_cny": round(estimated_cost * 7.2, 2),  # 汇率约7.2
            "estimated_tokens": total_input_tokens + total_output_tokens,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "model": model,
            "breakdown": {
                "planning_tokens": int(total_input_tokens * 0.15),
                "coding_tokens": int(total_input_tokens * 0.40),
                "testing_tokens": int(total_input_tokens * 0.20),
                "refining_tokens": int(total_input_tokens * 0.25),
                "prompt_cost": cost_result["prompt_cost"],
                "completion_cost": cost_result["completion_cost"]
            }
        }
    
    def calculate_actual_cost(
        self,
        prompt_tokens: int,  # ✅ 修正：参数名从 input_tokens 改为 prompt_tokens
        completion_tokens: int,  # ✅ 修正：参数名从 output_tokens 改为 completion_tokens
        model: str
    ) -> float:
        """
        计算实际LLM调用成本
        
        Args:
            prompt_tokens: 提示词Token数量（输入）
            completion_tokens: 补全Token数量（输出）
            model: 使用的模型
            
        Returns:
            float: 实际成本（美元）
        """
        # ✅ 修正：使用正确的参数名调用 config.py 的 calculate_cost
        cost_result = calculate_cost(
            model_name=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )
        
        total_cost = cost_result["total_cost"]
        
        logger.info(
            f"Actual cost: prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens}, "
            f"model={model}, cost=${total_cost:.4f}"
        )
        
        return total_cost
    
    def get_tier_info(self, tier: str) -> Dict:
        """
        获取订阅层级信息
        
        Args:
            tier: 订阅层级（free/basic/professional）
            
        Returns:
            Dict: 层级配置信息
        """
        return self.PRICING_TIERS.get(tier, self.PRICING_TIERS["free"])
    
    def check_quota_limit(
        self,
        current_count: int,
        tier: str,
        quota_type: str = "services"
    ) -> Dict:
        """
        检查配额限制
        
        Args:
            current_count: 当前使用量
            tier: 订阅层级
            quota_type: 配额类型（"services" 或 "requests"）
            
        Returns:
            Dict: 配额检查结果
        """
        tier_info = self.get_tier_info(tier)
        
        if quota_type == "services":
            max_quota = tier_info["max_services"]
        elif quota_type == "requests":
            max_quota = tier_info["max_requests_per_day"]
        else:
            raise ValueError(f"Unknown quota_type: {quota_type}")
        
        remaining = max_quota - current_count
        exceeded = current_count >= max_quota
        usage_percent = (current_count / max_quota) * 100 if max_quota > 0 else 0
        
        return {
            "current": current_count,
            "max": max_quota,
            "remaining": remaining,
            "exceeded": exceeded,
            "usage_percent": round(usage_percent, 2),
            "tier": tier,
            "quota_type": quota_type
        }
    
    def calculate_monthly_bill(
        self,
        tier: str,
        services_generated: int,
        avg_cost_per_service: float,
        api_calls: int
    ) -> Dict:
        """
        计算月度账单
        
        Args:
            tier: 订阅层级
            services_generated: 生成的服务数量
            avg_cost_per_service: 平均每个服务的成本
            api_calls: API调用次数
            
        Returns:
            Dict: 月度账单详情
        """
        tier_info = self.get_tier_info(tier)
        subscription_fee = tier_info["price"]
        
        # 服务生成成本（LLM调用）
        generation_cost_usd = services_generated * avg_cost_per_service
        generation_cost_cny = generation_cost_usd * 7.2
        
        # 订阅费
        subscription_cny = subscription_fee
        
        # API调用成本（假设超出配额后按¥0.001/次计费）
        max_free_calls = tier_info["max_requests_per_day"] * 30  # 月度免费额度
        excess_calls = max(0, api_calls - max_free_calls)
        api_cost_cny = excess_calls * 0.001
        
        # 总成本
        total_cny = subscription_cny + generation_cost_cny + api_cost_cny
        
        return {
            "tier": tier,
            "currency": "CNY",
            "breakdown": {
                "subscription_fee": round(subscription_cny, 2),
                "generation_cost": round(generation_cost_cny, 2),
                "api_call_cost": round(api_cost_cny, 2)
            },
            "total": round(total_cny, 2),
            "services_generated": services_generated,
            "api_calls": api_calls,
            "excess_calls": excess_calls,
            "month": datetime.now(timezone.utc).strftime("%Y-%m")
        }
    
    def compare_tiers(self) -> Dict:
        """
        对比不同订阅层级
        
        Returns:
            Dict: 层级对比数据
        """
        return {
            tier_name: {
                "price": tier_data["price"],
                "max_services": tier_data["max_services"],
                "max_requests_per_day": tier_data["max_requests_per_day"],
                "features": tier_data["features"],
                "cost_per_service": round(tier_data["price"] / tier_data["max_services"], 2) if tier_data["max_services"] > 0 else 0
            }
            for tier_name, tier_data in self.PRICING_TIERS.items()
        }
    
    def suggest_upgrade(
        self,
        current_tier: str,
        services_count: int,
        api_calls_today: int
    ) -> Optional[Dict]:
        """
        建议升级方案
        
        Args:
            current_tier: 当前层级
            services_count: 当前服务数量
            api_calls_today: 今日API调用次数
            
        Returns:
            Optional[Dict]: 升级建议（如果需要）
        """
        current_tier_info = self.get_tier_info(current_tier)
        
        # 检查是否接近配额上限
        services_usage = (services_count / current_tier_info["max_services"]) * 100
        api_usage = (api_calls_today / current_tier_info["max_requests_per_day"]) * 100
        
        # 如果任一指标超过80%，建议升级
        if services_usage > 80 or api_usage > 80:
            # 确定建议的目标层级
            if current_tier == "free":
                suggested_tier = "basic"
            elif current_tier == "basic":
                suggested_tier = "professional"
            else:
                return None  # 已经是最高层级
            
            suggested_tier_info = self.get_tier_info(suggested_tier)
            
            return {
                "current_tier": current_tier,
                "suggested_tier": suggested_tier,
                "reason": "approaching_quota_limit",
                "current_usage": {
                    "services": f"{services_usage:.1f}%",
                    "api_calls": f"{api_usage:.1f}%"
                },
                "upgrade_benefits": {
                    "additional_services": suggested_tier_info["max_services"] - current_tier_info["max_services"],
                    "additional_requests": suggested_tier_info["max_requests_per_day"] - current_tier_info["max_requests_per_day"],
                    "new_features": suggested_tier_info["features"]
                },
                "price_difference": suggested_tier_info["price"] - current_tier_info["price"]
            }
        
        return None
