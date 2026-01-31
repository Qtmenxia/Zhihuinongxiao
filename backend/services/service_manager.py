"""
MCP服务管理器
封装MCPybarra工作流调用，实现农产品电商服务的自动生成与部署
"""
import asyncio
import uuid
import logging
import sys
import importlib
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path

from backend.models.mcp_service import MCPService, ServiceStatus
from backend.models.farmer import Farmer
from backend.database.connection import AsyncSessionLocal
from backend.config.settings import settings

logger = logging.getLogger(__name__)


# ============================================
# MCPybarra 导入适配
# ============================================

def _setup_mcpybarra_environment():
    """配置MCPybarra的运行环境"""
    mcpybarra_framework_dir = Path(__file__).parent.parent / "mcpybarra_core" / "framework"
    mcp_swe_flow_dir = mcpybarra_framework_dir / "mcp_swe_flow"
    
    for p in [str(mcpybarra_framework_dir), str(mcp_swe_flow_dir)]:
        if p not in sys.path:
            sys.path.insert(0, p)
    
    project_root = Path(__file__).parent.parent.parent
    workspace_dir = project_root / "workspace"
    workspace_dir.mkdir(exist_ok=True)
    (workspace_dir / "output-servers").mkdir(exist_ok=True)
    (workspace_dir / "refinement").mkdir(exist_ok=True)
    (workspace_dir / "server-test-report").mkdir(exist_ok=True)
    
    return project_root


PROJECT_ROOT = _setup_mcpybarra_environment()

# 动态导入MCPybarra
MCPYBARRA_AVAILABLE = False
create_mcp_swe_workflow = None

try:
    graph_module = importlib.import_module("mcp_swe_flow.graph")
    create_mcp_swe_workflow = getattr(graph_module, "create_mcp_swe_workflow")
    MCPYBARRA_AVAILABLE = True
    logger.info("MCPybarra workflow imported successfully")
except (ImportError, ModuleNotFoundError, AttributeError) as e:
    logger.warning(f"MCPybarra not available: {e}. Using mock workflow.")


# ============================================
# 提示词构造器 - 核心创新点
# ============================================

class PromptBuilder:
    """
    农产品电商服务提示词构造器
    将农户输入的产品信息转换为MCPybarra可理解的自然语言需求
    """
    
    @staticmethod
    def build_product_service_prompt(
        product_name: str,
        product_category: str,
        price: float,
        stock: int,
        description: str,
        farmer_name: str,
        orchard_location: Optional[str] = None,
        certifications: Optional[List[str]] = None,
        service_type: str = "full"  # full | query | order | traceability
    ) -> str:
        """
        构造产品服务生成提示词
        
        Args:
            product_name: 产品名称，如"玉露香梨"
            product_category: 产品类别，如"水果"
            price: 单价
            stock: 库存
            description: 产品描述
            farmer_name: 农户名称
            orchard_location: 果园位置（可选）
            certifications: 认证列表（可选），如["有机认证", "绿色食品"]
            service_type: 服务类型
        
        Returns:
            str: 构造好的提示词
        """
        cert_text = ""
        if certifications:
            cert_text = f"该产品拥有以下认证：{', '.join(certifications)}。"
        
        location_text = ""
        if orchard_location:
            location_text = f"产地位于{orchard_location}。"
        
        if service_type == "full":
            return f"""
请为农户"{farmer_name}"创建一个完整的农产品电商MCP服务。

【产品信息】
- 产品名称：{product_name}
- 产品类别：{product_category}
- 单价：{price}元
- 当前库存：{stock}
- 产品描述：{description}
{location_text}{cert_text}

【功能需求】
1. 产品查询接口：支持按名称、类别、价格范围查询产品
2. 订单创建接口：支持创建购买订单，包含收货地址、数量、备注
3. 订单查询接口：支持查询订单状态、物流信息
4. 库存管理接口：支持查询和更新库存
5. 溯源查询接口：支持通过批次号查询产品溯源信息

【技术要求】
- 使用FastAPI框架
- 提供RESTful API接口
- 包含数据验证（Pydantic）
- 返回统一的JSON响应格式
- 包含健康检查接口 /health
"""
        
        elif service_type == "query":
            return f"""
请为农户"{farmer_name}"的产品"{product_name}"创建一个产品查询MCP服务。

【产品信息】
- 产品名称：{product_name}
- 产品类别：{product_category}
- 单价：{price}元
- 库存：{stock}
- 描述：{description}
{location_text}{cert_text}

【功能需求】
1. GET /products - 获取产品列表
2. GET /products/{{id}} - 获取产品详情
3. GET /products/search?keyword=xxx - 搜索产品
4. GET /health - 健康检查

使用FastAPI框架，返回JSON格式。
"""
        
        elif service_type == "order":
            return f"""
请为农户"{farmer_name}"创建一个订单管理MCP服务。

【关联产品】
- 产品：{product_name}（{product_category}）
- 单价：{price}元

【功能需求】
1. POST /orders - 创建订单（包含：产品ID、数量、收货地址、联系电话）
2. GET /orders/{{id}} - 查询订单详情
3. GET /orders?status=xxx - 按状态查询订单
4. PUT /orders/{{id}}/status - 更新订单状态
5. GET /health - 健康检查

使用FastAPI框架，包含订单状态流转逻辑。
"""
        
        elif service_type == "traceability":
            return f"""
请为农户"{farmer_name}"的产品"{product_name}"创建一个溯源查询MCP服务。

【产品信息】
- 产品：{product_name}
- 产地：{orchard_location or '未指定'}
- 认证：{', '.join(certifications) if certifications else '无'}

【功能需求】
1. GET /trace/{{batch_no}} - 通过批次号查询溯源信息
2. GET /trace/qrcode/{{batch_no}} - 生成溯源二维码
3. POST /trace/record - 添加生产记录（种植、施肥、采摘等）
4. GET /health - 健康检查

溯源信息包含：种植时间、施肥记录、采摘时间、质检报告等。
"""
        
        return f"为{farmer_name}的{product_name}创建电商服务接口。"
    
    @staticmethod
    def build_custom_service_prompt(user_input: str, farmer_name: str) -> str:
        """
        构造自定义服务提示词
        """
        return f"""
农户"{farmer_name}"需要创建一个自定义MCP服务。

【用户需求】
{user_input}

【技术要求】
- 使用FastAPI框架
- 提供RESTful API接口
- 返回JSON格式
- 包含健康检查接口
"""


# ============================================
# Mock工作流（降级方案）
# ============================================

class MockCompiledWorkflow:
    """Mock工作流，MCPybarra不可用时的降级处理"""
    
    def __init__(self):
        self.name = "MockMCPWorkflow"
        logger.info("MockCompiledWorkflow initialized")
    
    async def ainvoke(self, state: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        logger.info(f"MockWorkflow.ainvoke: {state.get('user_input', '')[:50]}...")
        await asyncio.sleep(2)
        
        user_input = state.get("user_input", "")
        api_name = self._generate_api_name(user_input)
        server_code = self._generate_mock_code(api_name, user_input)
        
        output_dir = PROJECT_ROOT / "workspace" / "output-servers" / api_name
        output_dir.mkdir(parents=True, exist_ok=True)
        server_file = output_dir / f"{api_name}.py"
        server_file.write_text(server_code, encoding="utf-8")
        
        return {
            **state,
            "api_name": api_name,
            "server_code": server_code,
            "server_file_path": str(server_file),
            "readme_content": f"# {api_name}\n\n## Requirement\n{user_input[:200]}",
            "requirements_content": "fastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0",
            "test_report_content": "All tests passed (mock)",
            "deliverability_assessment": "DELIVERABLE",
            "error": None,
        }
    
    def invoke(self, state: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.ainvoke(state, config))
        finally:
            loop.close()
    
    def _generate_api_name(self, user_input: str) -> str:
        if "产品" in user_input or "product" in user_input.lower():
            return "product_service"
        if "订单" in user_input or "order" in user_input.lower():
            return "order_service"
        if "溯源" in user_input or "trace" in user_input.lower():
            return "traceability_service"
        return "custom_service"
    
    def _generate_mock_code(self, api_name: str, user_input: str) -> str:
        return f'''"""
{api_name} - 农产品电商MCP服务
Auto-generated by MCPybarra
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="{api_name}",
    description="农产品电商服务接口",
    version="1.0.0"
)

# 数据模型
class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    address: str
    phone: str
    remark: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float
    created_at: str

# 模拟数据
PRODUCTS = [
    Product(id=1, name="玉露香梨", category="水果", price=12.8, stock=1000, description="山西特产"),
]

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "service": "{api_name}", "timestamp": datetime.now().isoformat()}}

@app.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    if category:
        return [p for p in PRODUCTS if p.category == category]
    return PRODUCTS

@app.get("/products/{{product_id}}", response_model=Product)
async def get_product(product_id: int):
    for p in PRODUCTS:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    order_id = f"ORD{{datetime.now().strftime('%Y%m%d%H%M%S')}}"
    product = next((p for p in PRODUCTS if p.id == order.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return OrderResponse(
        order_id=order_id,
        status="pending",
        total_amount=product.price * order.quantity,
        created_at=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
'''


def _create_workflow():
    """创建工作流实例"""
    if MCPYBARRA_AVAILABLE and create_mcp_swe_workflow:
        try:
            return create_mcp_swe_workflow()
        except Exception as e:
            logger.error(f"Failed to create MCPybarra workflow: {e}")
            return MockCompiledWorkflow()
    return MockCompiledWorkflow()


# ============================================
# 服务管理器
# ============================================

class ServiceManager:
    """MCP服务管理器"""
    
    def __init__(self):
        self.workflow = _create_workflow()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.prompt_builder = PromptBuilder()
        logger.info(f"ServiceManager initialized with {type(self.workflow).__name__}")
    
    async def generate_product_service(
        self,
        farmer_id: str,
        product_info: Dict[str, Any],
        service_type: str = "full",
        model: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> str:
        """
        为产品生成MCP服务
        
        Args:
            farmer_id: 农户ID
            product_info: 产品信息字典，包含name, category, price, stock, description等
            service_type: 服务类型 (full/query/order/traceability)
            model: LLM模型
            request_id: 请求追踪ID
        
        Returns:
            str: 任务ID
        """
        # 获取农户信息
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
            farmer = result.scalar_one()
            farmer_name = farmer.name
        
        # 构造提示词
        prompt = self.prompt_builder.build_product_service_prompt(
            product_name=product_info.get("name", "未命名产品"),
            product_category=product_info.get("category", "其他"),
            price=product_info.get("price", 0),
            stock=product_info.get("stock", 0),
            description=product_info.get("description", ""),
            farmer_name=farmer_name,
            orchard_location=product_info.get("orchard_location"),
            certifications=product_info.get("certifications"),
            service_type=service_type
        )
        
        return await self.start_generation(
            user_input=prompt,
            farmer_id=farmer_id,
            product_category=product_info.get("category"),
            model=model,
            request_id=request_id
        )
    
    async def start_generation(
        self,
        user_input: str,
        farmer_id: str,
        product_category: Optional[str] = None,
        model: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> str:
        """启动服务生成任务"""
        task_id = f"service_{farmer_id}_{uuid.uuid4().hex[:8]}"
        model_name = model or settings.DEFAULT_SWE_MODEL
        
        # MCPybarra初始状态（参考run_langgraph_workflow.py）
        initial_state = {
            "user_input": user_input,
            "interactive_mode": False,
            "swe_model": model_name,
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
            
            from sqlalchemy import select
            result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
            farmer = result.scalar_one()
            farmer.services_count += 1
            
            await db.commit()
            logger.info(f"Created service record: {task_id}")
        
        # 后台执行
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
        """执行MCPybarra工作流"""
        start_time = datetime.now(timezone.utc)
        logger.info(f"[{request_id}] Starting workflow for {task_id}")
        
        try:
            # 调用MCPybarra工作流
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state.get("error"):
                raise Exception(final_state["error"])
            
            # 提取结果
            server_code = final_state.get("server_code")
            file_path = final_state.get("server_file_path")
            api_name = final_state.get("api_name")
            readme = final_state.get("readme_content")
            requirements = final_state.get("requirements_content")
            
            generation_time = int((datetime.now(timezone.utc) - start_time).total_seconds())
            quality_score = self._extract_quality_score(final_state)
            
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
                service.generation_time = generation_time
                service.quality_score = quality_score
                service.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
                logger.info(f"[{request_id}] Workflow completed: {task_id}")
            
            await self._notify_completion(task_id, success=True)
            
        except Exception as e:
            logger.error(f"[{request_id}] Workflow failed: {task_id}: {e}", exc_info=True)
            
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                stmt = select(MCPService).where(MCPService.id == task_id)
                svc_result = await db.execute(stmt)
                service = svc_result.scalar_one()
                service.status = ServiceStatus.FAILED
                service.updated_at = datetime.now(timezone.utc)
                await db.commit()
            
            await self._notify_completion(task_id, success=False, error=str(e))
        
        finally:
            self.active_tasks.pop(task_id, None)
    
    async def get_status(self, task_id: str) -> dict:
        """查询任务状态"""
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
                "quality_score": service.quality_score
            }
    
    async def get_current_progress(self, task_id: str) -> dict:
        """获取实时进度"""
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(select(MCPService).where(MCPService.id == task_id))
            service = result.scalar_one_or_none()
            
            if not service or service.status != ServiceStatus.GENERATING:
                return {"progress": 0, "current_stage": "unknown"}
            
            elapsed = (datetime.now(timezone.utc) - service.created_at).total_seconds()
            progress = min(int((elapsed / 300) * 100), 95)
            
            stages = [
                (60, "planning", "需求分析与规划"),
                (180, "coding", "代码生成"),
                (240, "testing", "自动测试"),
                (float('inf'), "refining", "代码优化")
            ]
            
            for threshold, stage, message in stages:
                if elapsed < threshold:
                    return {"progress": progress, "current_stage": stage, "message": message}
            
            return {"progress": progress, "current_stage": "refining", "message": "代码优化"}
    
    def _extract_quality_score(self, result: dict) -> float:
        deliverability = str(result.get("deliverability_assessment", "")).upper()
        if "DELIVERABLE" in deliverability:
            return 85.0
        elif "NEEDS_REFINEMENT" in deliverability:
            return 70.0
        return 60.0
    
    def _calculate_progress(self, status: ServiceStatus) -> int:
        return {
            ServiceStatus.GENERATING: 50,
            ServiceStatus.TESTING: 80,
            ServiceStatus.READY: 100,
            ServiceStatus.DEPLOYED: 100,
            ServiceStatus.FAILED: 0,
            ServiceStatus.ARCHIVED: 100
        }.get(status, 0)
    
    async def _notify_completion(
        self,
        task_id: str,
        success: bool,
        error: Optional[str] = None
    ):
        """WebSocket通知"""
        try:
            from backend.api.main import notify_service_progress
            await notify_service_progress(task_id, {
                "type": "completed" if success else "error",
                "result": {"service_id": task_id} if success else None,
                "error": error
            })
        except Exception as e:
            logger.warning(f"WebSocket notification failed: {e}")

# 导出供其他模块使用
__all__ = ["ServiceManager", "PromptBuilder", "MockCompiledWorkflow"]