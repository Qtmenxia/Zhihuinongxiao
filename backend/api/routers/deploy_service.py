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
from backend.services.service_manager import ServiceManager
from backend.services.deployment_service import DeploymentService

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化服务管理器和部署管理器
service_manager = ServiceManager()
deployment_service = DeploymentService()

@router.post("/deploy-service/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED,
             summary="生成并部署MCP服务", description="根据提供的产品信息自动生成并部署一个MCP服务")
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
        task_id = await service_manager.start_generation(
            user_input=prompt,
            farmer_id=current_farmer.id,
            product_category=request.category,
            model=None,
            request_id=request_id
        )
        logger.info(f"[{request_id}] Service generation task started: {task_id}")
        
        # 等待服务生成完成
        if task_id in service_manager.active_tasks:
            await service_manager.active_tasks[task_id]  # 等待后台生成任务完成
        else:
            raise RuntimeError("Generation task not found or failed to start.")
        
        # 获取生成完成的服务记录
        result = await db.execute(select(MCPService).where(MCPService.id == task_id))
        service = result.scalar_one_or_none()
        if not service or service.status != ServiceStatus.READY:
            raise RuntimeError("Service generation failed or not completed.")
        
        # 3. 部署生成的服务
        deployment_result = await deployment_service.deploy_service(
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
