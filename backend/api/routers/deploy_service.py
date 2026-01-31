"""
MCP服务部署API路由  
实现根据产品信息自动生成并部署MCP服务
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import logging

from backend.api.dependencies import (
    get_session,
    get_current_farmer,
    check_service_quota,
    get_request_id
)
from backend.api.schemas.service import ServiceDeploymentRequest, DeploymentResponse
from backend.models.mcp_service import MCPService, ServiceStatus
from backend.models.service_deployment import ServiceDeployment
from backend.services.service_manager import ServiceManager,PromptBuilder
from backend.services.deployment_service import DeploymentService

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化服务（应用级单例，避免重复创建）
_service_manager: ServiceManager = None
_deployment_service: DeploymentService = None

def get_service_manager() -> ServiceManager:
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager


def get_deployment_service() -> DeploymentService:
    global _deployment_service
    if _deployment_service is None:
        _deployment_service = DeploymentService()
    return _deployment_service

@router.post("/deploy-service/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED,
             summary="生成并部署MCP服务", description="根据产品信息自动生成并部署MCP服务")
async def deploy_product_service(
    request: ServiceDeploymentRequest,
    db: AsyncSession = Depends(get_session),
    current_farmer = Depends(check_service_quota()),
    request_id: str = Depends(get_request_id)
):
    """
    提交产品信息，自动生成并部署MCP服务
    
    流程：
    1. 构建提示词
    2. 调用MCPybarra生成服务代码
    3. 部署服务
    4. 返回服务端点
    """
    service_manager = get_service_manager()
    deployment_service = get_deployment_service()
    
    # 1. 构建提示词（使用静态方法）
    prompt = PromptBuilder.build_product_service_prompt(
        product_name=request.name,
        product_category=request.category,
        price=request.price,
        stock=request.stock,
        description=request.description or "",
        farmer_name=current_farmer.name,
        orchard_location=request.origin,
        certifications=request.certifications or [],
        service_type="full"
    )
    logger.info(f"[{request_id}] Built prompt for '{request.name}'")
    
    try:
        # 2. 启动服务生成
        task_id = await service_manager.start_generation(
            user_input=prompt,
            farmer_id=current_farmer.id,
            product_category=request.category,
            request_id=request_id
        )
        logger.info(f"[{request_id}] Generation started: {task_id}")
        
        # 等待生成完成
        if task_id in service_manager.active_tasks:
            await service_manager.active_tasks[task_id]
        
        # 3. 获取生成结果
        result = await db.execute(
            select(MCPService).where(MCPService.id == task_id)
        )
        service = result.scalar_one_or_none()
        
        if not service or service.status == ServiceStatus.FAILED:
            raise RuntimeError("服务生成失败")
        
        if service.status != ServiceStatus.READY:
            raise RuntimeError(f"服务状态异常: {service.status.value}")
        
        # 4. 部署服务
        deployment_result = await deployment_service.deploy_service(
            service_id=task_id,
            file_path=service.file_path
        )
        
        # 5. 更新数据库
        service.status = ServiceStatus.DEPLOYED
        service.is_deployed = True
        service.deployed_at = datetime.now(timezone.utc)
        service.endpoints = deployment_result.get("endpoints", [])
        service.deploy_port = deployment_result.get("port")
        
        # 保存部署记录
        deployment_record = ServiceDeployment(
            service_id=task_id,
            farmer_id=current_farmer.id,
            product_name=request.name,
            product_category=request.category,
            price=request.price,
            origin=request.origin,
            stock=request.stock,
            description=request.description,
            certifications=request.certifications,
            deployed_at=service.deployed_at
        )
        db.add(deployment_record)
        await db.commit()
        
        logger.info(f"[{request_id}] Service {task_id} deployed at port {deployment_result.get('port')}")
        
        return DeploymentResponse(
            service_id=task_id,
            status="deployed",
            endpoints=deployment_result.get("endpoints", []),
            message=f"服务已部署，可通过 {deployment_result.get('base_url')} 访问"
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Deployment failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务部署失败: {str(e)}"
        )

async def deploy_service_endpoint(
    request: ServiceDeploymentRequest,
    db: AsyncSession = Depends(get_session),
    current_farmer = Depends(check_service_quota()),  # 确认农户身份及配额
    request_id: str = Depends(get_request_id)
):
    """
    提交产品信息，自动生成并部署MCP服务，并保存部署记录。
    """
    # 1. 构建提示词 Prompt
    prompt = ServiceManager.PromptBuilder.build_product_service_prompt(
        product_name=request.name,
        product_category=request.category,
        price=request.price,
        stock=request.stock,
        description=request.description or "",
        farmer_name=current_farmer.name,
        orchard_location=request.origin,
        certifications=request.certifications or []
    )
    logger.info(f"[{request_id}] Built prompt for product '{request.name}': {prompt[:80]}...")
    
    try:
        # 2. 启动服务生成任务
        task_id = await _service_manager.start_generation(
            user_input=prompt,
            farmer_id=current_farmer.id,
            product_category=request.category,
            model=None,
            request_id=request_id
        )
        logger.info(f"[{request_id}] Service generation task started: {task_id}")
        
        # 等待服务生成完成
        if task_id in _service_manager.active_tasks:
            await _service_manager.active_tasks[task_id]  # 等待后台生成任务完成
        else:
            raise RuntimeError("Generation task not found or failed to start.")
        
        # 获取生成完成的服务记录
        result = await db.execute(select(MCPService).where(MCPService.id == task_id))
        service = result.scalar_one_or_none()
        if not service or service.status != ServiceStatus.READY:
            raise RuntimeError("Service generation failed or not completed.")
        
        # 3. 部署生成的服务
        deployment_result = await _deployment_service.deploy_service(
            service_id=task_id,
            file_path=service.file_path
        )
        
        # 更新服务状态并记录部署信息
        service.status = ServiceStatus.DEPLOYED
        service.is_deployed = True
        service.deployed_at = datetime.now(timezone.utc)
        service.endpoints = deployment_result.get("endpoints", [])
        # 保存历史记录到ServiceDeployment表
        deployment_record = ServiceDeployment(
            service_id=task_id,
            farmer_id=current_farmer.id,
            product_name=request.name,
            product_category=request.category,
            price=request.price,
            origin=request.origin,
            stock=request.stock,
            description=request.description,
            certifications=request.certifications,
            deployed_at=service.deployed_at
        )
        db.add(deployment_record)
        await db.commit()
        logger.info(f"[{request_id}] Service {task_id} deployed successfully.")
        
        # 4. 返回部署结果
        return DeploymentResponse(
            service_id=task_id,
            status="deployed",
            endpoints=deployment_result.get("endpoints", []),
            message="Service deployed successfully and ready to use"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Service deployment failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务部署失败: {str(e)}"
        )

@router.get(
    "/deployed-services",
    summary="获取已部署服务列表"
)
async def list_deployed_services(
    current_farmer = Depends(check_service_quota()),
):
    """获取当前农户的所有已部署服务"""
    deployment_service = get_deployment_service()
    services = await deployment_service.list_deployed_services()
    return {"services": services}


@router.delete(
    "/deployed-services/{service_id}",
    summary="停止已部署服务"
)
async def stop_deployed_service(
    service_id: str,
    db: AsyncSession = Depends(get_session),
    current_farmer = Depends(check_service_quota()),
):
    """停止并移除已部署的服务"""
    deployment_service = get_deployment_service()
    
    success = await deployment_service.stop_service(service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务未找到或已停止"
        )
    
    # 更新数据库状态
    result = await db.execute(
        select(MCPService).where(MCPService.id == service_id)
    )
    service = result.scalar_one_or_none()
    if service:
        service.status = ServiceStatus.READY
        service.is_deployed = False
        await db.commit()
    
    return {"message": "服务已停止", "service_id": service_id}