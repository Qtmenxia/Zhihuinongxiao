"""
MCP服务管理器
核心服务管理逻辑，封装MCPybarra工作流的调用

适配层设计：
- 不修改MCPybarra框架本身
- 通过配置PYTHONPATH解决导入问题
- 提供Mock降级方案
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
        """构造自定义服务提示词"""
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
# MCPybarra 导入适配
# ============================================

def _setup_mcpybarra_path():
    """配置MCPybarra的导入路径"""
    mcpybarra_root = Path(__file__).parent.parent / "mcpybarra_core" / "framework"
    mcp_swe_flow_dir = mcpybarra_root / "mcp_swe_flow"
    
    paths_to_add = [
        str(mcpybarra_root),
        str(mcp_swe_flow_dir),
    ]
    
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)
            logger.debug(f"Added to sys.path: {p}")
    
    # 确保workspace目录存在
    project_root = Path(__file__).parent.parent.parent
    workspace_dir = project_root / "workspace"
    workspace_dir.mkdir(exist_ok=True)
    (workspace_dir / "output-servers").mkdir(exist_ok=True)
    (workspace_dir / "refinement").mkdir(exist_ok=True)
    (workspace_dir / "server-test-report").mkdir(exist_ok=True)
    
    return project_root


# 设置路径
PROJECT_ROOT = _setup_mcpybarra_path()

# 使用importlib动态导入，避免IDE静态分析报错
MCPYBARRA_AVAILABLE = False
create_mcp_swe_workflow = None

try:
    graph_module = importlib.import_module("mcp_swe_flow.graph")
    create_mcp_swe_workflow = getattr(graph_module, "create_mcp_swe_workflow")
    MCPYBARRA_AVAILABLE = True
    logger.info("MCPybarra workflow imported successfully via importlib")
except (ImportError, ModuleNotFoundError, AttributeError) as e:
    logger.warning(f"MCPybarra not available: {e}. Using mock workflow.")


# ============================================
# Mock工作流（降级方案）
# ============================================

class MockCompiledWorkflow:
    """
    Mock工作流，用于MCPybarra未安装时的降级处理
    提供与LangGraph CompiledGraph相同的接口
    """
    
    def __init__(self):
        self.name = "MockMCPWorkflow"
        logger.info("MockCompiledWorkflow initialized (MCPybarra not available)")
    
    async def ainvoke(self, state: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        """异步执行工作流（模拟）"""
        logger.info(f"MockWorkflow.ainvoke: {state.get('user_input', '')[:50]}...")
        
        await asyncio.sleep(2)  # 模拟处理时间
        
        user_input = state.get("user_input", "")
        model_name = state.get("model_name", "mock-model")
        output_dir = state.get("output_dir", "/tmp/mock-output")
        
        # 生成API名称
        api_name = self._generate_api_name(user_input)
        server_code = self._generate_mock_code(api_name, user_input)
        
        # 保存文件
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        server_file = output_path / f"{api_name}.py"
        server_file.write_text(server_code, encoding="utf-8")
        
        return {
            **state,
            "api_name": api_name,
            "server_code": server_code,
            "server_file_path": str(server_file),
            "readme_content": f"# {api_name}\n\nAI-generated service.\n\n## Requirement\n{user_input}",
            "requirements_content": "fastapi>=0.100.0\nuvicorn>=0.23.0",
            "test_report_content": "All tests passed (mock)",
            "deliverability_assessment": "DELIVERABLE",
            "statistics_summary": {
                "total_cost": 0.05,
                "total_tokens": 1000,
                "model": model_name
            },
            "error": None,
            "next_step": "end"
        }
    
    def invoke(self, state: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        """同步执行"""
        return asyncio.get_event_loop().run_until_complete(self.ainvoke(state, config))
    
    def _generate_api_name(self, user_input: str) -> str:
        keywords = ["product", "order", "customer", "inventory", "price", "query"]
        for kw in keywords:
            if kw in user_input.lower():
                return f"{kw}_service"
        return "custom_service"
    
    def _generate_mock_code(self, api_name: str, user_input: str) -> str:
        return f'''"""
{api_name} - 农产品电商MCP服务
Auto-generated by MCPybarra / Mock Workflow
Requirement: {user_input[:100]}
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="{api_name}",
    description="农产品电商服务接口",
    version="1.0.0"
)

# ==================== 数据模型 ====================

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None
    origin: Optional[str] = None
    certifications: List[str] = []

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    address: str
    phone: str
    remark: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str
    product_name: str
    quantity: int
    total_amount: float
    status: OrderStatus
    created_at: str

class TraceInfo(BaseModel):
    batch_no: str
    product_name: str
    origin: str
    plant_date: str
    harvest_date: str
    certifications: List[str]
    records: List[dict]

# ==================== 模拟数据 ====================

PRODUCTS = [
    Product(id=1, name="玉露香梨", category="水果", price=12.8, stock=1000, 
            description="山西蒲县特产，果肉细腻，汁多味甜", origin="山西省蒲县",
            certifications=["有机认证", "绿色食品"]),
    Product(id=2, name="红富士苹果", category="水果", price=8.5, stock=2000,
            description="脆甜可口，营养丰富", origin="山西省蒲县"),
]

ORDERS: dict = {{}}

# ==================== API接口 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {{"status": "healthy", "service": "{api_name}", "timestamp": datetime.now().isoformat()}}

@app.get("/products", response_model=List[Product])
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """获取产品列表"""
    results = PRODUCTS.copy()
    if category:
        results = [p for p in results if p.category == category]
    if min_price is not None:
        results = [p for p in results if p.price >= min_price]
    if max_price is not None:
        results = [p for p in results if p.price <= max_price]
    return results

@app.get("/products/{{product_id}}", response_model=Product)
async def get_product(product_id: int):
    """获取产品详情"""
    for p in PRODUCTS:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="产品不存在")

@app.get("/products/search")
async def search_products(keyword: str = Query(..., min_length=1)):
    """搜索产品"""
    results = [p for p in PRODUCTS if keyword.lower() in p.name.lower() or keyword.lower() in (p.description or "").lower()]
    return {{"keyword": keyword, "count": len(results), "products": results}}

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    """创建订单"""
    product = next((p for p in PRODUCTS if p.id == order.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="库存不足")
    
    order_id = f"ORD{{datetime.now().strftime('%Y%m%d%H%M%S')}}{{order.product_id:03d}}"
    total = product.price * order.quantity
    
    ORDERS[order_id] = {{
        "order_id": order_id,
        "product": product,
        "quantity": order.quantity,
        "total_amount": total,
        "address": order.address,
        "phone": order.phone,
        "status": OrderStatus.PENDING,
        "created_at": datetime.now().isoformat()
    }}
    
    # 扣减库存
    product.stock -= order.quantity
    
    return OrderResponse(
        order_id=order_id,
        product_name=product.name,
        quantity=order.quantity,
        total_amount=total,
        status=OrderStatus.PENDING,
        created_at=datetime.now().isoformat()
    )

@app.get("/orders/{{order_id}}")
async def get_order(order_id: str):
    """查询订单"""
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="订单不存在")
    return ORDERS[order_id]

@app.get("/trace/{{batch_no}}", response_model=TraceInfo)
async def get_trace_info(batch_no: str):
    """溯源查询"""
    # 模拟溯源数据
    return TraceInfo(
        batch_no=batch_no,
        product_name="玉露香梨",
        origin="山西省蒲县",
        plant_date="2024-03-15",
        harvest_date="2024-09-20",
        certifications=["有机认证", "绿色食品"],
        records=[
            {{"date": "2024-03-15", "action": "种植", "operator": "张三"}},
            {{"date": "2024-05-10", "action": "施肥", "operator": "李四"}},
            {{"date": "2024-09-20", "action": "采摘", "operator": "王五"}},
            {{"date": "2024-09-21", "action": "质检通过", "operator": "质检员"}}
        ]
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
        为产品生成MCP服务（核心入口方法）
        
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
        
        # 使用PromptBuilder构造提示词
        prompt = PromptBuilder.build_product_service_prompt(
            product_name=product_info.get("name", "未命名产品"),
            product_category=product_info.get("category", "其他"),
            price=product_info.get("price", 0),
            stock=product_info.get("stock", 0),
            description=product_info.get("description", ""),
            farmer_name=farmer_name,
            orchard_location=product_info.get("origin"),
            certifications=product_info.get("certifications"),
            service_type=service_type
        )
        
        logger.info(f"Built prompt for product '{product_info.get('name')}': {prompt[:100]}...")
        
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
        """启动异步服务生成任务"""
        task_id = f"service_{farmer_id}_{uuid.uuid4().hex[:8]}"
        
        model_name = model or settings.DEFAULT_SWE_MODEL
        output_base = Path(settings.WORKSPACE_DIR) / "pipeline-output-servers" / model_name / task_id
        
        # 准备初始状态（严格按照MCPybarra的state.py）
        initial_state = {
            "user_input": user_input,
            "api_name": None,
            "interactive_mode": False,
            "model_name": model_name,
            "resources_dir": str(Path(settings.WORKSPACE_DIR) / "resources"),
            "output_dir": str(output_base),
            "refinement_dir": str(Path(settings.WORKSPACE_DIR) / "refinement"),
            "test_report_dir": str(Path(settings.WORKSPACE_DIR) / "server-test-report"),
            "max_refine_loops": settings.MAX_REFINE_LOOPS,
            "max_planning_turns": settings.MAX_PLANNING_TURNS,
            "max_codegen_turns": settings.MAX_CODEGEN_TURNS,
            "max_planning_tool_calls": settings.MAX_PLANNING_TOOL_CALLS,
            "max_codegen_tool_calls": settings.MAX_CODEGEN_TOOL_CALLS,
            "planning_turns": 0,
            "codegen_turns": 0,
            "refine_loops": 0,
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
                created_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            db.add(service)
            
            from sqlalchemy import select
            result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
            farmer = result.scalar_one()
            farmer.services_count += 1
            
            await db.commit()
            logger.info(f"Created service record: {task_id}")
        
        # 后台启动工作流
        task = asyncio.create_task(self._execute_workflow(task_id, initial_state, request_id))
        self.active_tasks[task_id] = task
        
        return task_id
    
    async def _execute_workflow(
        self,
        task_id: str,
        initial_state: dict,
        request_id: Optional[str] = None
    ):
        """执行MCPybarra工作流并更新状态"""
        start_time = datetime.now(timezone.utc).replace(tzinfo=None)
        logger.info(f"[{request_id}] Starting workflow for {task_id}")
        
        try:
            # 调用工作流（MCPybarra或Mock）
            result = await self.workflow.ainvoke(initial_state)
            
            server_code = result.get("server_code")
            file_path = result.get("server_file_path")
            api_name = result.get("api_name")
            readme = result.get("readme_content")
            requirements = result.get("requirements_content")
            
            cost = self._calculate_cost_from_result(result)
            generation_time = int((datetime.now(timezone.utc).replace(tzinfo=None) - start_time).total_seconds())
            quality_score = self._extract_quality_score(result)
            
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
                service.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                
                await db.commit()
                logger.info(f"[{request_id}] Workflow completed for {task_id}")
            
            await self._notify_completion(task_id, success=True, cost=cost)
            
        except Exception as e:
            logger.error(f"[{request_id}] Workflow failed for {task_id}: {e}", exc_info=True)
            
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                stmt = select(MCPService).where(MCPService.id == task_id)
                svc_result = await db.execute(stmt)
                service = svc_result.scalar_one()
                service.status = ServiceStatus.FAILED
                service.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                await db.commit()
            
            await self._notify_completion(task_id, success=False, error=str(e))
        
        finally:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
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
                "cost": service.generation_cost,
                "quality_score": service.quality_score
            }
    
    async def get_current_progress(self, task_id: str) -> dict:
        """获取实时进度"""
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(select(MCPService).where(MCPService.id == task_id))
            service = result.scalar_one_or_none()
            
            if not service or service.status != ServiceStatus.GENERATING:
                return {"progress": 0, "current_stage": "unknown", "message": "Not generating"}
            
            elapsed = (datetime.now(timezone.utc).replace(tzinfo=None) - service.created_at).total_seconds()
            estimated_total = 300
            progress = min(int((elapsed / estimated_total) * 100), 95)
            
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
        stats = result.get("statistics_summary", {})
        return round(stats.get("total_cost", 0.0), 4)
    
    def _extract_quality_score(self, result: dict) -> float:
        deliverability = result.get("deliverability_assessment", "")
        if "DELIVERABLE" in deliverability.upper():
            return 85.0
        elif "NEEDS_REFINEMENT" in deliverability.upper():
            return 70.0
        return 60.0
    
    def _calculate_progress(self, status: ServiceStatus) -> int:
        progress_map = {
            ServiceStatus.GENERATING: 50,
            ServiceStatus.TESTING: 80,
            ServiceStatus.READY: 100,
            ServiceStatus.DEPLOYED: 100,
            ServiceStatus.FAILED: 0,
            ServiceStatus.ARCHIVED: 100
        }
        return progress_map.get(status, 0)
    
    async def _notify_completion(
        self,
        task_id: str,
        success: bool,
        cost: Optional[float] = None,
        error: Optional[str] = None
    ):
        """通过WebSocket通知前端"""
        try:
            from backend.api.main import notify_service_progress
            
            if success:
                await notify_service_progress(task_id, {
                    "type": "completed",
                    "result": {"service_id": task_id, "cost": cost}
                })
            else:
                await notify_service_progress(task_id, {
                    "type": "error",
                    "error": error
                })
        except Exception as e:
            logger.warning(f"Failed to send WebSocket notification: {e}")


# 导出供其他模块使用
__all__ = ["ServiceManager", "PromptBuilder", "MockCompiledWorkflow", "MCPYBARRA_AVAILABLE"]
