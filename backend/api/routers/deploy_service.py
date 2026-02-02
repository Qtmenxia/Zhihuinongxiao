"""
MCP服务部署API路由
实现根据产品信息自动生成并部署MCP服务

核心流程：
1. 农户提交产品信息
2. PromptBuilder构造提示词
3. MCPybarra生成服务代码
4. DeploymentService部署服务
5. 返回可调用的API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional, List
import logging

from backend.api.dependencies import (
    get_session,
    get_current_farmer,
    check_service_quota,
    get_request_id
)
from backend.api.schemas.service import (
    ServiceDeploymentRequest,
    DeploymentResponse,
    ServiceStatusResponse
)
from backend.models.mcp_service import MCPService, ServiceStatus
from backend.models.farmer import Farmer
from backend.services.service_manager import ServiceManager, PromptBuilder
from backend.services.deployment_service import DeploymentService

router = APIRouter()
logger = logging.getLogger(__name__)

# 应用级单例，避免重复创建
_service_manager: Optional[ServiceManager] = None
_deployment_service: Optional[DeploymentService] = None


def get_service_manager() -> ServiceManager:
    """获取ServiceManager单例"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager


def get_deployment_service() -> DeploymentService:
    """获取DeploymentService单例"""
    global _deployment_service
    if _deployment_service is None:
        _deployment_service = DeploymentService()
    return _deployment_service


@router.post(
    "/deploy-product-service",
    response_model=DeploymentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="生成并部署产品MCP服务",
    description="根据农户提交的产品信息，自动生成并部署MCP服务"
)
async def deploy_product_service(
    request: ServiceDeploymentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(check_service_quota()),
    request_id: str = Depends(get_request_id)
):
    """
    农户提交产品信息，自动生成并部署MCP服务
    
    流程：
    1. 验证农户配额
    2. 使用PromptBuilder构造提示词
    3. 调用MCPybarra生成服务代码
    4. 部署服务并返回端点
    
    注意：服务生成是异步的，返回任务ID后可轮询状态
    """
    service_manager = get_service_manager()
    
    logger.info(f"[{request_id}] Received deployment request for product '{request.name}' from farmer {current_farmer.id}")
    
    try:
        # 构建产品信息字典
        product_info = {
            "name": request.name,
            "category": request.category,
            "price": request.price,
            "stock": request.stock,
            "description": request.description,
            "origin": request.origin,
            "certifications": request.certifications
        }
        
        # 启动服务生成任务
        task_id = await service_manager.generate_product_service(
            farmer_id=current_farmer.id,
            product_info=product_info,
            service_type=request.service_type or "full",
            model=request.model,
            request_id=request_id
        )
        
        logger.info(f"[{request_id}] Service generation started: {task_id}")
        
        # 后台任务：等待生成完成后自动部署
        background_tasks.add_task(
            _auto_deploy_when_ready,
            task_id,
            request_id
        )
        
        return DeploymentResponse(
            service_id=task_id,
            status="generating",
            endpoints=[],
            message=f"服务生成已启动，任务ID: {task_id}。请通过 /deploy/status/{task_id} 查询进度。"
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Failed to start service generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务生成启动失败: {str(e)}"
        )


async def _auto_deploy_when_ready(task_id: str, request_id: str):
    """后台任务：等待服务生成完成后自动部署"""
    service_manager = get_service_manager()
    deployment_service = get_deployment_service()
    
    logger.info(f"[{request_id}] Waiting for service {task_id} to be ready...")
    
    # 等待生成任务完成
    if task_id in service_manager.active_tasks:
        try:
            await service_manager.active_tasks[task_id]
        except Exception as e:
            logger.error(f"[{request_id}] Generation task failed: {e}")
            return
    
    # 检查服务状态并部署
    from backend.database.connection import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MCPService).where(MCPService.id == task_id)
        )
        service = result.scalar_one_or_none()
        
        if not service:
            logger.error(f"[{request_id}] Service {task_id} not found after generation")
            return
        
        if service.status != ServiceStatus.READY:
            logger.warning(f"[{request_id}] Service {task_id} not ready, status: {service.status}")
            return
        
        # 部署服务
        try:
            deployment_result = await deployment_service.deploy_service(
                service_id=task_id,
                file_path=service.file_path
            )
            
            # 更新数据库
            service.status = ServiceStatus.DEPLOYED
            service.is_deployed = True
            service.deployed_at = datetime.now(timezone.utc)
            service.endpoints = deployment_result.get("endpoints", [])
            
            await db.commit()
            logger.info(f"[{request_id}] Service {task_id} deployed successfully")
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to deploy service {task_id}: {e}")


@router.get(
    "/deploy/status/{task_id}",
    response_model=ServiceStatusResponse,
    summary="查询服务生成/部署状态"
)
async def get_deployment_status(
    task_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer),
    request_id: str = Depends(get_request_id)
):
    """
    查询服务生成和部署状态
    
    返回：
    - generating: 生成中
    - testing: 测试中
    - ready: 生成完成，待部署
    - deployed: 已部署
    - failed: 失败
    """
    result = await db.execute(
        select(MCPService).where(
            MCPService.id == task_id,
            MCPService.farmer_id == current_farmer.id
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在或无权访问"
        )
    
    # 获取实时进度
    service_manager = get_service_manager()
    progress_info = await service_manager.get_current_progress(task_id)
    
    return ServiceStatusResponse(
        service_id=task_id,
        status=service.status.value,
        progress=progress_info.get("progress", 0),
        current_stage=progress_info.get("current_stage"),
        message=progress_info.get("message"),
        cost=service.generation_cost,
        quality_score=service.quality_score,
        generation_time=service.generation_time
    )


@router.post(
    "/deploy/{service_id}",
    response_model=DeploymentResponse,
    summary="手动部署已生成的服务"
)
async def deploy_existing_service(
    service_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer),
    request_id: str = Depends(get_request_id)
):
    """
    手动部署已生成但未部署的服务
    """
    deployment_service = get_deployment_service()
    
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
            detail="服务不存在或无权访问"
        )
    
    if service.status not in [ServiceStatus.READY, ServiceStatus.DEPLOYED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"服务状态不允许部署: {service.status.value}"
        )
    
    if service.status == ServiceStatus.DEPLOYED and service.is_deployed:
        # 已部署，返回现有端点
        return DeploymentResponse(
            service_id=service_id,
            status="deployed",
            endpoints=service.endpoints or [],
            message="服务已部署"
        )
    
    try:
        # 执行部署
        deployment_result = await deployment_service.deploy_service(
            service_id=service_id,
            file_path=service.file_path
        )
        
        # 更新数据库
        service.status = ServiceStatus.DEPLOYED
        service.is_deployed = True
        service.deployed_at = datetime.now(timezone.utc)
        service.endpoints = deployment_result.get("endpoints", [])
        
        await db.commit()
        
        logger.info(f"[{request_id}] Service {service_id} deployed manually")
        
        return DeploymentResponse(
            service_id=service_id,
            status="deployed",
            endpoints=deployment_result.get("endpoints", []),
            message="服务部署成功"
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Manual deployment failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"部署失败: {str(e)}"
        )


@router.delete(
    "/deploy/{service_id}",
    summary="停止已部署的服务"
)
async def stop_deployed_service(
    service_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer),
    request_id: str = Depends(get_request_id)
):
    """
    停止并下线已部署的服务
    """
    deployment_service = get_deployment_service()
    
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
            detail="服务不存在或无权访问"
        )
    
    if not service.is_deployed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="服务未部署"
        )
    
    try:
        # 停止服务
        await deployment_service.stop_service(service_id)
        
        # 更新数据库
        service.status = ServiceStatus.READY
        service.is_deployed = False
        
        await db.commit()
        
        logger.info(f"[{request_id}] Service {service_id} stopped")
        
        return {"message": "服务已停止", "service_id": service_id}
        
    except Exception as e:
        logger.error(f"[{request_id}] Failed to stop service: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止服务失败: {str(e)}"
        )


@router.get(
    "/deployed-services",
    summary="获取已部署服务列表"
)
async def list_deployed_services(
    db: AsyncSession = Depends(get_session),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    获取当前农户所有已部署的服务
    """
    result = await db.execute(
        select(MCPService).where(
            MCPService.farmer_id == current_farmer.id,
            MCPService.is_deployed == True
        )
    )
    services = result.scalars().all()
    
    return {
        "total": len(services),
        "services": [
            {
                "service_id": s.id,
                "name": s.name,
                "status": s.status.value,
                "endpoints": s.endpoints or [],
                "deployed_at": s.deployed_at.isoformat() if s.deployed_at else None,
                "quality_score": s.quality_score
            }
            for s in services
        ]
    }
