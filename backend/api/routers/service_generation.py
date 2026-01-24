"""
MCP服务生成API路由
核心功能：将农户的自然语言需求转化为可部署的MCP服务
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timezone
import logging

from backend.api.dependencies import (
    get_session,
    get_current_farmer,
    check_service_quota,
    get_pagination_params,
    PaginationParams,
    get_request_id
)
from backend.api.schemas.service import (
    ServiceGenerationRequest,
    ServiceGenerationResponse,
    ServiceDetail,
    ServiceStatusResponse,
    ServiceListResponse,
    DeploymentRequest,
    DeploymentResponse
)
from backend.models.farmer import Farmer
from backend.models.mcp_service import MCPService, ServiceStatus
from backend.services.service_manager import ServiceManager
from backend.services.deployment_service import DeploymentService
from backend.services.cost_calculator import CostCalculator

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化服务管理器(单例)
service_manager = ServiceManager()
deployment_service = DeploymentService()
cost_calculator = CostCalculator()


@router.post(
    "/generate",
    response_model=ServiceGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="生成MCP服务",
    description="""
    根据自然语言需求自动生成MCP服务
    
    **流程说明：**
    1. 提交需求后立即返回任务ID
    2. 后台异步执行MCPybarra工作流
    3. 通过WebSocket或轮询查询生成进度
    4. 生成完成后可部署使用
    
    **成本说明：**
    - 预估成本：$0.018-0.14
    - 实际成本在生成完成后计算
    - 免费用户有配额限制
    """
)
async def generate_service(
    request: ServiceGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(check_service_quota()),
    request_id: str = Depends(get_request_id)
):
    """
    创建MCP服务生成任务
    
    Args:
        request: 服务生成请求
        background_tasks: 后台任务管理器
        db: 数据库会话
        current_farmer: 当前农户
        request_id: 请求ID
    """
    logger.info(f"[{request_id}] Farmer {current_farmer.id} requested service generation")
    
    try:
        # 1. 估算成本
        estimate = cost_calculator.estimate_generation_cost(
            requirement=request.requirement,
            model=request.model or "gemini-2.5-pro"
        )
        
        logger.info(f"[{request_id}] Estimated cost: ${estimate['estimated_cost_usd']}")
        
        # 2. 启动服务生成任务
        task_id = await service_manager.start_generation(
            user_input=request.requirement,
            farmer_id=current_farmer.id,
            product_category=request.product_category,
            model=request.model,
            request_id=request_id
        )
        
        logger.info(f"[{request_id}] Service generation task created: {task_id}")
        
        # 3. 返回任务信息
        return ServiceGenerationResponse(
            service_id=task_id,
            status="generating",
            estimated_cost=estimate["estimated_cost_usd"],
            estimated_cost_cny=estimate["estimated_cost_cny"],
            estimated_time=300,  # 预估5分钟
            message="服务生成任务已创建，请通过WebSocket或轮询查询进度"
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Failed to start service generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start service generation: {str(e)}"
        )


@router.get(
    "/{service_id}/status",
    response_model=ServiceStatusResponse,
    summary="查询服务生成状态",
    description="查询指定服务的生成状态和进度"
)
async def get_service_status(
    service_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    查询服务生成状态
    
    Args:
        service_id: 服务ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询服务
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == service_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # 如果正在生成，尝试获取实时进度
    if service.status == ServiceStatus.GENERATING:
        try:
            progress = await service_manager.get_current_progress(service_id)
            return ServiceStatusResponse(
                service_id=service_id,
                status=service.status.value,
                progress=progress.get("progress", 0),
                current_stage=progress.get("current_stage"),
                message=progress.get("message"),
                cost=service.generation_cost,
                quality_score=service.quality_score
            )
        except:
            pass
    
    # 返回数据库中的状态
    return ServiceStatusResponse(
        service_id=service_id,
        status=service.status.value,
        progress=100 if service.status == ServiceStatus.READY else 0,
        current_stage="completed" if service.status == ServiceStatus.READY else "failed",
        message=_get_status_message(service.status),
        cost=service.generation_cost,
        quality_score=service.quality_score,
        generation_time=service.generation_time
    )


@router.get(
    "/{service_id}",
    response_model=ServiceDetail,
    summary="获取服务详情",
    description="获取服务的完整信息，包括代码、文档、端点等"
)
async def get_service_detail(
    service_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取服务详细信息
    
    Args:
        service_id: 服务ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == service_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceDetail(
        service_id=service.id,
        farmer_id=service.farmer_id,
        name=service.name,
        description=service.description,
        status=service.status.value,
        model_used=service.model_used,
        original_requirement=service.original_requirement,
        code=service.code,
        readme=service.readme,
        requirements=service.requirements,
        file_path=service.file_path,
        generation_cost=service.generation_cost,
        generation_time=service.generation_time,
        quality_score=service.quality_score,
        test_pass_rate=service.test_pass_rate,
        is_deployed=service.is_deployed,
        deployed_at=service.deployed_at,
        endpoints=service.endpoints or [],
        total_calls=service.total_calls,
        total_errors=service.total_errors,
        avg_latency=service.avg_latency,
        refinement_count=service.refinement_count,
        created_at=service.created_at,
        updated_at=service.updated_at
    )


@router.get(
    "",
    response_model=ServiceListResponse,
    summary="获取服务列表",
    description="获取当前农户的所有服务(支持分页和筛选)"
)
async def list_services(
    status_filter: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取服务列表
    
    Args:
        status_filter: 服务状态筛选(可选)
        pagination: 分页参数
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 构建查询
    query = select(MCPService).where(MCPService.farmer_id == current_farmer.id)
    
    if status_filter:
        try:
            status_enum = ServiceStatus(status_filter)
            query = query.where(MCPService.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # 计算总数
    count_query = select(func.count()).select_from(MCPService).where(
        MCPService.farmer_id == current_farmer.id
    )
    if status_filter:
        count_query = count_query.where(MCPService.status == status_enum)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(MCPService.created_at.desc())
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    services = result.scalars().all()
    
    # 转换为响应模型
    items = [
        ServiceDetail(
            service_id=s.id,
            farmer_id=s.farmer_id,
            name=s.name,
            description=s.description,
            status=s.status.value,
            model_used=s.model_used,
            original_requirement=s.original_requirement,
            generation_cost=s.generation_cost,
            quality_score=s.quality_score,
            is_deployed=s.is_deployed,
            endpoints=s.endpoints or [],
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in services
    ]
    
    return ServiceListResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        has_more=(pagination.offset + len(items)) < total
    )


@router.post(
    "/{service_id}/deploy",
    response_model=DeploymentResponse,
    summary="部署服务",
    description="将生成的MCP服务部署为可调用的API"
)
async def deploy_service(
    service_id: str,
    deployment_request: Optional[DeploymentRequest] = None,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    部署MCP服务
    
    Args:
        service_id: 服务ID
        deployment_request: 部署配置(可选)
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询服务
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == service_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # 检查服务状态
    if service.status != ServiceStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service is not ready for deployment. Current status: {service.status.value}"
        )
    
    # 如果已部署，检查是否强制重新部署
    if service.is_deployed and not (deployment_request and deployment_request.force_redeploy):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service is already deployed. Use force_redeploy=true to redeploy."
        )
    
    try:
        # 执行部署
        deployment_result = await deployment_service.deploy_service(
            service_id=service_id,
            file_path=service.file_path
        )
        
        # 更新数据库
        service.is_deployed = True
        service.deployed_at = datetime.now(timezone.utc)()
        service.endpoints = deployment_result["endpoints"]
        await db.commit()
        
        logger.info(f"Service {service_id} deployed successfully")
        
        return DeploymentResponse(
            service_id=service_id,
            status="deployed",
            endpoints=deployment_result["endpoints"],
            message="Service deployed successfully and ready to use"
        )
        
    except Exception as e:
        logger.error(f"Failed to deploy service {service_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment failed: {str(e)}"
        )


@router.post(
    "/{service_id}/stop",
    summary="停止服务",
    description="停止正在运行的MCP服务"
)
async def stop_service(
    service_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    停止MCP服务
    
    Args:
        service_id: 服务ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询服务
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == service_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    if not service.is_deployed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service is not deployed"
        )
    
    try:
        # 停止服务
        await deployment_service.stop_service(service_id)
        
        # 更新状态
        service.is_deployed = False
        await db.commit()
        
        logger.info(f"Service {service_id} stopped successfully")
        
        return {"message": "Service stopped successfully", "service_id": service_id}
        
    except Exception as e:
        logger.error(f"Failed to stop service {service_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop service: {str(e)}"
        )


@router.delete(
    "/{service_id}",
    summary="删除服务",
    description="删除MCP服务(如果正在运行会先停止)"
)
async def delete_service(
    service_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    删除MCP服务
    
    Args:
        service_id: 服务ID
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 查询服务
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == service_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    
    try:
        # 如果正在运行，先停止
        if service.is_deployed:
            await deployment_service.stop_service(service_id)
        
        # 删除数据库记录
        await db.delete(service)
        await db.commit()
        
        # 更新农户服务计数
        current_farmer.services_count = max(0, current_farmer.services_count - 1)
        await db.commit()
        
        logger.info(f"Service {service_id} deleted successfully")
        
        return {"message": "Service deleted successfully", "service_id": service_id}
        
    except Exception as e:
        logger.error(f"Failed to delete service {service_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete service: {str(e)}"
        )

@router.get(
    "/{service_id}/logs",
    summary="获取服务日志",
    description="获取服务的调用日志"
)
async def get_service_logs(
    service_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取服务调用日志
    
    Args:
        service_id: 服务ID
        limit: 返回记录数
        db: 数据库会话
        current_farmer: 当前农户
    """
    from backend.models.service_log import ServiceLog
    
    # 验证服务所有权
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == service_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # 查询日志
    query = select(ServiceLog).where(ServiceLog.service_id == service_id)
    query = query.order_by(ServiceLog.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return {
        "service_id": service_id,
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "tool_name": log.tool_name,
                "input_params": log.input_params,
                "output_result": log.output_result,
                "latency": log.latency,
                "status": log.status,
                "error_message": log.error_message,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }


@router.post(
    "/{service_id}/call",
    summary="调用服务工具",
    description="直接调用已部署服务的工具(用于测试)"
)
async def call_service_tool(
    service_id: str,
    tool_name: str,
    params: dict,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    调用服务工具
    
    Args:
        service_id: 服务ID
        tool_name: 工具名称
        params: 工具参数
        db: 数据库会话
        current_farmer: 当前农户
    """
    # 验证服务
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == service_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    if not service.is_deployed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service is not deployed"
        )
    
    try:
        # 调用服务
        start_time = datetime.now(timezone.utc)()
        result = await deployment_service.call_service_tool(
            service_id=service_id,
            tool_name=tool_name,
            params=params
        )
        latency = (datetime.now(timezone.utc)() - start_time).total_seconds() * 1000
        
        # 记录日志
        from backend.models.service_log import ServiceLog
        log_entry = ServiceLog(
            id=f"log_{service_id}_{datetime.now(timezone.utc)().timestamp()}",
            service_id=service_id,
            tool_name=tool_name,
            input_params=params,
            output_result=str(result),
            latency=latency,
            status="success",
            created_at=datetime.now(timezone.utc)()
        )
        db.add(log_entry)
        
        # 更新统计
        service.total_calls += 1
        await db.commit()
        
        return {
            "success": True,
            "result": result,
            "latency_ms": latency
        }
        
    except Exception as e:
        logger.error(f"Failed to call service tool: {e}", exc_info=True)
        
        # 记录错误日志
        from backend.models.service_log import ServiceLog
        log_entry = ServiceLog(
            id=f"log_{service_id}_{datetime.now(timezone.utc)().timestamp()}",
            service_id=service_id,
            tool_name=tool_name,
            input_params=params,
            status="error",
            error_message=str(e),
            created_at=datetime.now(timezone.utc)()
        )
        db.add(log_entry)
        
        # 更新错误统计
        service.total_errors += 1
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool call failed: {str(e)}"
        )


# ==================== 辅助函数 ====================

def _get_status_message(status: ServiceStatus) -> str:
    """获取状态描述信息"""
    messages = {
        ServiceStatus.GENERATING: "服务正在生成中...",
        ServiceStatus.TESTING: "正在执行质量测试...",
        ServiceStatus.READY: "服务已就绪，可以部署",
        ServiceStatus.DEPLOYED: "服务已部署并运行中",
        ServiceStatus.FAILED: "服务生成失败",
        ServiceStatus.ARCHIVED: "服务已归档"
    }
    return messages.get(status, "未知状态")
