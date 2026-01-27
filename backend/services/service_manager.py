"""
MCP服务管理器
核心服务管理逻辑，封装MCPybarra工作流的调作流的调用
"""
import asyncio
import uuid
import logging
from typing import Optional, Dict
from datetime import datetime,timezone
from pathlib import Path

from backend.mcpybarra_core.framework.mcp_swe_flow.graph import create_mcp_swe_workflow
from backend.models.mcp_service import MCPService, ServiceStatus
from backend.models.farmer import Farmer
from backend.database.connection import AsyncSessionLocal
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class ServiceManager:
    """MCP服务管理器"""
    
    def __init__(self):
        """初始化服务管理器"""
        self.workflow = create_mcp_swe_workflow()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        logger.info("ServiceManager initialized")
    
    async def start_generation(
        self,
        user_input: str,
        farmer_id: str,
        product_category: Optional[str] = None,
        model: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> str:
        """
        启动异步服务生成任务
        
        Args:
            user_input: 用户自然语言需求
            farmer_id: 农户ID
            product_category: 产品类别
            model: 指定LLM模型
            request_id: 请求追踪ID
            
        Returns:
            str: 任务ID (service_id)
        """
        # 生成任务ID
        task_id = f"service_{farmer_id}_{uuid.uuid4().hex[:8]}"
        
        # 准备输出目录（按MCPybarra的结构）
        model_name = model or settings.DEFAULT_SWE_MODEL
        output_base = Path(settings.WORKSPACE_DIR) / "pipeline-output-servers" / model_name / task_id
        
        # 准备初始状态（严格按照MCPybarra的state.py）
        initial_state = {
            "user_input": user_input,
            "api_name": None,  # 由workflow内部的generate_server_name生成
            "interactive_mode": False,
            "model_name": model_name,
            "resources_dir": str(Path(settings.WORKSPACE_DIR) / "resources"),
            "output_dir": str(output_base),
            "refinement_dir": str(Path(settings.WORKSPACE_DIR) / "refinement"),
            "test_report_dir": str(Path(settings.WORKSPACE_DIR) / "server-test-report"),
            
            # 工作流配置
            "max_refine_loops": settings.MAX_REFINE_LOOPS,
            "max_planning_turns": settings.MAX_PLANNING_TURNS,
            "max_codegen_turns": settings.MAX_CODEGEN_TURNS,
            "max_planning_tool_calls": settings.MAX_PLANNING_TOOL_CALLS,
            "max_codegen_tool_calls": settings.MAX_CODEGEN_TOOL_CALLS,
            
            # 初始化计数器
            "planning_turns": 0,
            "codegen_turns": 0,
            "refine_loops": 0,
            
            # 错误处理
            "error": None,
            "next_step": "input_loader"
        }
        
        # 创建数据库记录
        async with AsyncSessionLocal() as db:
            service = MCPService(
                id=task_id,
                farmer_id=farmer_id,
                name=f"{product_category or 'Custom'} Service",
                description=user_input[:200],
                original_requirement=user_input,
                model_used=model_name,
                status=ServiceStatus.GENERATING,
                created_at=datetime.now(timezone.utc)
            )
            db.add(service)
            
            # 更新农户服务计数
            from sqlalchemy import select
            result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
            farmer = result.scalar_one()
            farmer.services_count += 1
            
            await db.commit()
            logger.info(f"Created service record: {task_id}")
        
        # 在后台启动工作流
        task = asyncio.create_task(
            self._execute_workflow(task_id, initial_state, request_id)
        )
        self.active_tasks[task_id] = task
        
        return task_id
    
    async def _execute_workflow(
        self,
        task_id: str,
        initial_state: dict,
        request_id: Optional[str] = None
    ):
        """
        执行MCPybarra工作流并更新状态
        
        Args:
            task_id: 任务ID
            initial_state: 初始状态
            request_id: 请求追踪ID
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"[{request_id}] Starting MCPybarra workflow for {task_id}")
        
        try:
            # 执行工作流（调用MCPybarra）
            result = await self.workflow.ainvoke(initial_state)
            
            # 从结果中提取关键信息（根据MCPybarra的state.py）
            server_code = result.get("server_code")
            file_path = result.get("server_file_path")
            api_name = result.get("api_name")
            readme = result.get("readme_content")
            requirements = result.get("requirements_content")
            test_report = result.get("test_report_content")
            
            # 计算成本（从统计日志中提取）
            cost = self._calculate_cost_from_result(result)
            
            # 计算耗时
            generation_time = int((datetime.now(timezone.utc) - start_time).total_seconds())
            
            # 提取质量评分
            quality_score = self._extract_quality_score(result)
            
            # 更新数据库
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                stmt = select(MCPService).where(MCPService.id == task_id)
                svc_result = await db.execute(stmt)
                service = svc_result.scalar_one()
                
                service.name = api_name or service.name
                service.status = ServiceStatus.READY
                service.code = server_code
                service.file_path = file_path
                service.readme = readme
                service.requirements = requirements
                service.generation_cost = cost
                service.generation_time = generation_time
                service.quality_score = quality_score
                service.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
                logger.info(f"[{request_id}] Workflow completed for {task_id}")
            
            # 通过WebSocket通知前端
            await self._notify_completion(task_id, success=True, cost=cost)
            
        except Exception as e:
            logger.error(f"[{request_id}] Workflow failed for {task_id}: {e}", exc_info=True)
            
            # 更新失败状态
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                stmt = select(MCPService).where(MCPService.id == task_id)
                svc_result = await db.execute(stmt)
                service = svc_result.scalar_one()
                
                service.status = ServiceStatus.FAILED
                service.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
            
            # 通知失败
            await self._notify_completion(task_id, success=False, error=str(e))
        
        finally:
            # 清理任务
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def get_status(self, task_id: str) -> dict:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 状态信息
        """
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(select(MCPService).where(MCPService.id == task_id))
            service = result.scalar_one_or_none()
            
            if not service:
                raise ValueError(f"Service {task_id} not found")
            
            return {
                "service_id": task_id,
                "status": service.status.value,
                "progress": self._calculate_progress(service.status),
                "cost": service.generation_cost,
                "quality_score": service.quality_score
            }
    
    async def get_current_progress(self, task_id: str) -> dict:
        """
        获取实时进度(从运行中的任务)
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 进度信息
        """
        # MCPybarra的工作流不提供实时进度跟踪
        # 这里返回基本的阶段估算
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(select(MCPService).where(MCPService.id == task_id))
            service = result.scalar_one_or_none()
            
            if not service or service.status != ServiceStatus.GENERATING:
                return {"progress": 0, "current_stage": "unknown", "message": "Not generating"}
            
            # 估算进度（基于时间）
            elapsed = (datetime.now(timezone.utc) - service.created_at).total_seconds()
            estimated_total = 300  # 假设5分钟
            progress = min(int((elapsed / estimated_total) * 100), 95)
            
            # 根据时间估算阶段
            if elapsed < 60:
                stage = "planning"
            elif elapsed < 180:
                stage = "coding"
            elif elapsed < 240:
                stage = "testing"
            else:
                stage = "refining"
            
            return {
                "progress": progress,
                "current_stage": stage,
                "message": f"MCPybarra正在执行{stage}阶段..."
            }
    
    def _calculate_cost_from_result(self, result: dict) -> float:
        """
        从MCPybarra结果中计算总成本
        
        Args:
            result: 工作流结果
            
        Returns:
            float: 总成本(美元)
        """
        # MCPybarra在statistics_summary中记录总成本
        stats = result.get("statistics_summary", {})
        total_cost = stats.get("total_cost", 0.0)
        
        return round(total_cost, 4)
    
    def _extract_quality_score(self, result: dict) -> float:
        """
        从结果中提取质量评分
        
        Args:
            result: 工作流结果
            
        Returns:
            float: 质量评分(0-100)
        """
        # 从测试报告中提取（如果有）
        test_report = result.get("test_report_content", "")
        deliverability = result.get("deliverability_assessment", "")
        
        # 简化版本：根据deliverability判断
        if "DELIVERABLE" in deliverability.upper():
            return 85.0
        elif "NEEDS_REFINEMENT" in deliverability.upper():
            return 70.0
        else:
            return 60.0
    
    def _calculate_progress(self, status: ServiceStatus) -> int:
        """
        根据状态计算进度百分比
        
        Args:
            status: 服务状态
            
        Returns:
            int: 进度(0-100)
        """
        progress_map = {
            ServiceStatus.GENERATING: 50,  # 生成中
            ServiceStatus.TESTING: 80,     # 测试中（MCPybarra已集成测试）
            ServiceStatus.READY: 100,      # 已就绪
            ServiceStatus.DEPLOYED: 100,   # 已部署
            ServiceStatus.FAILED: 0,       # 失败
            ServiceStatus.ARCHIVED: 100    # 归档
        }
        return progress_map.get(status, 0)
    
    async def _notify_completion(
        self,
        task_id: str,
        success: bool,
        cost: Optional[float] = None,
        error: Optional[str] = None
    ):
        """
        通过WebSocket通知前端任务完成
        
        Args:
            task_id: 任务ID
            success: 是否成功
            cost: 成本
            error: 错误信息
        """
        try:
            from backend.api.main import notify_service_progress
            
            if success:
                await notify_service_progress(task_id, {
                    "type": "completed",
                    "result": {
                        "service_id": task_id,
                        "cost": cost
                    }
                })
            else:
                await notify_service_progress(task_id, {
                    "type": "error",
                    "error": error
                })
        except Exception as e:
            logger.warning(f"Failed to send WebSocket notification: {e}")
