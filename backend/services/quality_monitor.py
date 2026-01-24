"""
质量监控服务
监控已部署服务的质量指标，自动触发优化
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import numpy as np

from backend.database.connection import AsyncSessionLocal
from backend.models.mcp_service import MCPService, ServiceStatus
from backend.models.service_log import ServiceLog

logger = logging.getLogger(__name__)


class QualityMonitor:
    """质量监控器"""
    
    # 质量阈值配置
    THRESHOLDS = {
        "error_rate": 0.05,      # 5%错误率
        "p99_latency": 1000,     # 1秒P99延迟
        "avg_latency": 500       # 500ms平均延迟
    }
    
    def __init__(self):
        """初始化质量监控器"""
        self.metrics_cache: Dict[str, dict] = {}
        logger.info("QualityMonitor initialized")
    
    async def collect_metrics(
        self,
        service_id: str,
        window: str = "1h"
    ) -> dict:
        """
        收集服务指标
        
        Args:
            service_id: 服务ID
            window: 时间窗口(1h, 6h, 24h, 7d)
            
        Returns:
            dict: 指标数据
        """
        # 解析时间窗口
        window_seconds = self._parse_time_window(window)
        start_time = datetime.utcnow() - timedelta(seconds=window_seconds)
        
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select, and_
            
            # 查询日志
            stmt = select(ServiceLog).where(
                and_(
                    ServiceLog.service_id == service_id,
                    ServiceLog.created_at >= start_time
                )
            )
            result = await db.execute(stmt)
            logs = result.scalars().all()
            
            if not logs:
                return {
                    "service_id": service_id,
                    "window": window,
                    "total_requests": 0,
                    "error_rate": 0.0,
                    "p99_latency": 0.0,
                    "avg_latency": 0.0,
                    "qps": 0.0
                }
            
            # 计算指标
            total_requests = len(logs)
            errors = [l for l in logs if l.status == "error"]
            error_rate = len(errors) / total_requests if total_requests > 0 else 0
            
            # 延迟统计
            latencies = [l.latency for l in logs if l.latency is not None]
            p99_latency = np.percentile(latencies, 99) if latencies else 0
            avg_latency = np.mean(latencies) if latencies else 0
            
            # QPS计算
            qps = total_requests / window_seconds if window_seconds > 0 else 0
            
            metrics = {
                "service_id": service_id,
                "window": window,
                "total_requests": total_requests,
                "error_rate": round(error_rate, 4),
                "p99_latency": round(p99_latency, 2),
                "avg_latency": round(avg_latency, 2),
                "qps": round(qps, 2),
                "success_count": total_requests - len(errors),
                "error_count": len(errors),
                "collected_at": datetime.utcnow().isoformat()
            }
            
            # 缓存结果
            self.metrics_cache[service_id] = metrics
            
            return metrics
    
    async def auto_refine_if_needed(self, service_id: str) -> Optional[str]:
        """
        当质量指标低于阈值时，自动触发MCPybarra重新优化
        
        Args:
            service_id: 服务ID
            
        Returns:
            Optional[str]: 新服务ID(如果触发了优化)
        """
        logger.info(f"Checking quality metrics for service {service_id}")
        
        # 收集最近1小时的指标
        metrics = await self.collect_metrics(service_id, window="1h")
        
        # 检查是否需要优化
        should_refine = (
            metrics["error_rate"] > self.THRESHOLDS["error_rate"] or
            metrics["p99_latency"] > self.THRESHOLDS["p99_latency"]
        )
        
        if not should_refine:
            logger.info(f"Service {service_id} quality is acceptable")
            return None
        
        logger.warning(
            f"Service {service_id} quality degraded. "
            f"Error rate: {metrics['error_rate']*100:.1f}%, "
            f"P99 latency: {metrics['p99_latency']:.0f}ms"
        )
        
        # 获取原始服务配置
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(select(MCPService).where(MCPService.id == service_id))
            service = result.scalar_one_or_none()
            
            if not service:
                logger.error(f"Service {service_id} not found")
                return None
            
            # 构建增强的优化需求
            enhanced_requirement = f"""
原始需求：
{service.original_requirement}

当前问题分析：
- 错误率：{metrics['error_rate']*100:.1f}% (阈值：{self.THRESHOLDS['error_rate']*100}%)
- P99延迟：{metrics['p99_latency']:.0f}ms (阈值：{self.THRESHOLDS['p99_latency']}ms)
- 平均延迟：{metrics['avg_latency']:.0f}ms

优化要求：
1. 加强错误处理和输入验证
2. 优化性能，减少延迟
3. 添加重试机制和熔断器
4. 改进日志记录以便调试

请基于以上问题重新生成高质量的服务代码。
"""
            
            # 启动新的生成任务
            from backend.services.service_manager import ServiceManager
            service_manager = ServiceManager()
            
            new_task_id = await service_manager.start_generation(
                user_input=enhanced_requirement,
                farmer_id=service.farmer_id,
                model=service.model_used,
                request_id=f"auto_refine_{service_id}"
            )
            
            # 标记新服务为优化版本
            async with AsyncSessionLocal() as db2:
                from sqlalchemy import select
                stmt = select(MCPService).where(MCPService.id == new_task_id)
                result = await db2.execute(stmt)
                new_service = result.scalar_one()
                
                new_service.parent_service_id = service_id
                new_service.description = f"Auto-refined version of {service_id}"
                
                # 更新原服务的优化计数
                service.refinement_count += 1
                
                await db2.commit()
            
            logger.info(f"Auto-refinement triggered for {service_id}, new service: {new_task_id}")
            return new_task_id
    
    async def generate_quality_report(
        self,
        service_id: str,
        window: str = "7d"
    ) -> str:
        """
        生成质量评估报告(Markdown格式)
        
        Args:
            service_id: 服务ID
            window: 统计周期
            
        Returns:
            str: Markdown格式报告
        """
        metrics = await self.collect_metrics(service_id, window)
        
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(select(MCPService).where(MCPService.id == service_id))
            service = result.scalar_one_or_none()
            
            if not service:
                return f"# 错误\n\n服务 {service_id} 不存在"
        
        # 生成报告
        report = f"""# 服务质量报告

**服务名称**: {service.name}  
**服务ID**: {service_id}  
**生成时间**: {service.created_at.strftime('%Y-%m-%d %H:%M:%S')}  
**统计周期**: {window}  
**报告生成时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

---

## 性能指标概览

| 指标 | 数值 | 状态 | 阈值 |
|------|------|------|------|
| 总请求数 | {metrics['total_requests']} | - | - |
| 成功请求 | {metrics['success_count']} | - | - |
| 失败请求 | {metrics['error_count']} | - | - |
| 错误率 | {metrics['error_rate']*100:.2f}% | {self._get_status_emoji(metrics['error_rate'], self.THRESHOLDS['error_rate'])} | <{self.THRESHOLDS['error_rate']*100}% |
| P99延迟 | {metrics['p99_latency']:.0f}ms | {self._get_status_emoji(metrics['p99_latency'], self.THRESHOLDS['p99_latency'])} | <{self.THRESHOLDS['p99_latency']}ms |
| 平均延迟 | {metrics['avg_latency']:.0f}ms | {self._get_status_emoji(metrics['avg_latency'], self.THRESHOLDS['avg_latency'])} | <{self.THRESHOLDS['avg_latency']}ms |
| QPS | {metrics['qps']:.2f} | - | - |

---

## 详细分析

### 1. 可用性分析

- **可用性**: {((1 - metrics['error_rate']) * 100):.2f}%
- **评级**: {self._get_availability_rating(metrics['error_rate'])}

{self._get_availability_analysis(metrics['error_rate'])}

### 2. 性能分析

{self._get_performance_analysis(metrics)}

### 3. 优化建议

{self._generate_recommendations(metrics)}

---

## 历史趋势

*注：完整的历史趋势分析需要时序数据库支持，当前版本显示当前快照*

- **当前状态**: {"🟢 健康" if self._is_healthy(metrics) else "🔴 需要关注"}
- **上次优化**: {service.refinement_count} 次
- **部署状态**: {"✅ 已部署" if service.is_deployed else "⏸️ 未部署"}

---

*本报告由智农链销质量监控系统自动生成*
"""
        
        return report
    
    def _parse_time_window(self, window: str) -> int:
        """
        解析时间窗口为秒数
        
        Args:
            window: 时间窗口字符串(如"1h", "7d")
            
        Returns:
            int: 秒数
        """
        window_map = {
            "1h": 3600,
            "6h": 21600,
            "24h": 86400,
            "7d": 604800,
            "30d": 2592000
        }
        return window_map.get(window, 3600)
    
    def _get_status_emoji(self, value: float, threshold: float) -> str:
        """获取状态表情"""
        if value < threshold:
            return "✅"
        elif value < threshold * 1.5:
            return "⚠️"
        else:
            return "❌"
    
    def _get_availability_rating(self, error_rate: float) -> str:
        """获取可用性评级"""
        availability = (1 - error_rate) * 100
        if availability >= 99.9:
            return "优秀 (Three 9s)"
        elif availability >= 99.0:
            return "良好 (Two 9s)"
        elif availability >= 95.0:
            return "及格"
        else:
            return "不合格"
    
    def _get_availability_analysis(self, error_rate: float) -> str:
        """获取可用性分析文本"""
        if error_rate < 0.01:
            return "✅ 服务可用性优秀，错误率控制良好。"
        elif error_rate < 0.05:
            return "⚠️ 服务可用性良好，但仍有优化空间。建议关注错误日志。"
        else:
            return "❌ 服务可用性不达标，需要立即优化。建议启用自动优化功能。"
    
    def _get_performance_analysis(self, metrics: dict) -> str:
        """获取性能分析文本"""
        analysis = []
        
        if metrics['p99_latency'] < self.THRESHOLDS['p99_latency']:
            analysis.append("- ✅ P99延迟表现优秀")
        else:
            analysis.append(f"- ❌ P99延迟过高({metrics['p99_latency']:.0f}ms)，建议优化数据库查询或增加缓存")
        
        if metrics['avg_latency'] < self.THRESHOLDS['avg_latency']:
            analysis.append("- ✅ 平均延迟表现良好")
        else:
            analysis.append(f"- ⚠️ 平均延迟偏高({metrics['avg_latency']:.0f}ms)，建议进行性能分析")
        
        if metrics['qps'] > 0:
            analysis.append(f"- 📊 当前QPS为 {metrics['qps']:.2f}，服务负载正常")
        
        return "\n".join(analysis)
    
    def _generate_recommendations(self, metrics: dict) -> str:
        """生成优化建议"""
        recommendations = []
        
        if metrics['error_rate'] > self.THRESHOLDS['error_rate']:
            recommendations.append("### 🔴 错误率优化")
            recommendations.append("- 加强输入验证和异常处理")
            recommendations.append("- 添加重试机制(带指数退避)")
            recommendations.append("- 实现熔断器模式防止级联失败")
            recommendations.append("- 详细记录错误日志以便排查")
        
        if metrics['p99_latency'] > self.THRESHOLDS['p99_latency']:
            recommendations.append("### ⚡ 性能优化")
            recommendations.append("- 优化数据库查询(添加索引、减少N+1查询)")
            recommendations.append("- 引入缓存层(Redis)减少重复计算")
            recommendations.append("- 使用异步I/O提升并发能力")
            recommendations.append("- 考虑使用CDN加速静态资源")
        
        if metrics['total_requests'] < 10:
            recommendations.append("### 📊 数据不足")
            recommendations.append("- 当前请求量较少，建议增加测试用例")
            recommendations.append("- 可以使用压力测试工具模拟真实负载")
        
        if not recommendations:
            recommendations.append("### ✅ 当前服务质量良好")
            recommendations.append("- 继续保持，定期监控指标变化")
            recommendations.append("- 建议设置自动告警，及时发现问题")
        
        return "\n".join(recommendations)
    
    def _is_healthy(self, metrics: dict) -> bool:
        """判断服务是否健康"""
        return (
            metrics['error_rate'] <= self.THRESHOLDS['error_rate'] and
            metrics['p99_latency'] <= self.THRESHOLDS['p99_latency']
        )

    async def check_service_quality(self, service_id: str) -> bool:
        """
        检查服务质量是否达标
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: True表示质量达标，False表示需要优化
        """
        try:
            metrics = await self.collect_metrics(service_id, window="1h")
            
            # 如果请求量太少，默认认为质量OK
            if metrics['total_requests'] < 5:
                return True
            
            is_healthy = self._is_healthy(metrics)
            
            if not is_healthy:
                logger.warning(
                    f"Service {service_id} quality check failed. "
                    f"Error rate: {metrics['error_rate']*100:.1f}%, "
                    f"P99 latency: {metrics['p99_latency']:.0f}ms"
                )
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Failed to check quality for {service_id}: {e}")
            return True  # 出错时不触发优化
