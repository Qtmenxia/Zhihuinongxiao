import os
import asyncio
import logging
from datetime import datetime,timezone
from pathlib import Path
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

# 导入项目模块
from backend.database.connection import AsyncSessionLocal
from backend.models.mcp_service import MCPService, ServiceStatus
from backend.mcpybarra_core.framework.mcp_swe_flow.nodes.swe_generator import swe_generate_node
from backend.config.settings import settings
from backend.mcpybarra_core.framework.mcp_swe_flow.nodes.input_loader import load_input_node

# 配置日志
logger = logging.getLogger("worker.service")

async def process_pending_services():
    """
    核心工作函数：
    1. 查找所有状态为 GENERATING 且 代码为空 的任务
    2. 逐个处理
    """
    async with AsyncSessionLocal() as session:
        try:
            # 1. 查找待处理任务
            # 修正：根据你的模型定义，新任务默认是 GENERATING
            # 我们增加一个条件：code 为空，确保只处理新任务，不重复处理正在跑的任务
            result = await session.execute(
                select(MCPService).where(
                    and_(
                        MCPService.status == ServiceStatus.GENERATING,
                        (MCPService.code == None) | (MCPService.code == "")
                    )
                )
            )
            pending_services = result.scalars().all()
            
            if not pending_services:
                return 

            logger.info(f"🚀 Found {len(pending_services)} new services to process")

            # 2. 逐个处理任务
            for service in pending_services:
                await process_single_service(session, service)
                
        except Exception as e:
            logger.error(f"❌ Error in process_pending_services: {e}", exc_info=True)


async def process_single_service(session: AsyncSession, service: MCPService):
    """处理单个服务生成流程"""
    service_id = service.id
    logger.info(f"👉 Starting processing for service: {service.name} ({service_id})")

    try:
        # Step 1: 更新时间戳，表示 Worker 正在活跃处理
        service.updated_at = datetime.utcnow()
        await session.commit()
        
        # Step 2: 准备生成参数
        state = {
            "user_input": service.original_requirement,
            "project_path": service.file_path or "",  
            "demo_mode": False,
            "verbose": True,
            "swe_model": service.model_used or "openrouter/anthropic/claude-3.5-sonnet"
        }
        
        logger.info(f"🤖 Generating code with LLM for {service_id}...")

        # Step 3: 先通过 load_input_node 加载 MCP 文档
        state = load_input_node(state)
        if state.get("error"):
            raise Exception(f"Input loading failed: {state.get('error')}")
        
        # Step 4: 调用生成逻辑
        result_state = await swe_generate_node(state)
        
        generated_code = (
            result_state.get("server_code")
            or result_state.get("code")
            or result_state.get("implementation_code")
            or ""
        )

        test_code = (
            result_state.get("test_code")
            or result_state.get("tests_code")
            or ""
        )
        if not generated_code.strip():
            server_file_path = result_state.get("server_file_path")
            if server_file_path and os.path.exists(server_file_path):
                with open(server_file_path, "r", encoding="utf-8") as f:
                    generated_code = f.read()

        if not generated_code.strip():
            raise Exception("LLM returned empty code")


        error = result_state.get("error")

        if error:
            raise Exception(f"LLM Generation failed: {error}")

        if not generated_code:
            raise Exception("LLM returned empty code")

        logger.info(f"✅ Code generated successfully for {service_id}")

        # Step 4: 不再另存为 main.py，直接使用 generator 输出路径
        server_file_path = result_state.get("server_file_path")
        project_dir = result_state.get("project_dir")

        if project_dir:
            service_dir = Path(project_dir)
        elif server_file_path:
            service_dir = Path(server_file_path).parent
        elif service.file_path:
            service_dir = Path(service.file_path)
        else:
            # 兜底目录（不依赖 settings.SERVICES_DIR）
            service_dir = Path("workspace") / "generated-services" / service_id

        service_dir.mkdir(parents=True, exist_ok=True)

        # 主文件：优先 server_file_path（与 python -m workspace... 一致）
        if server_file_path:
            main_file = Path(server_file_path)
        else:
            # 兜底：不要叫 main.py，至少用服务名，避免后续模块路径错位
            main_file = service_dir / f"{service.name}.py"

        # 如果 generator 没写入（极少情况），才补写
        if (not main_file.exists()) or main_file.stat().st_size == 0:
            with open(main_file, "w", encoding="utf-8") as f:
                f.write(generated_code)

        # README（可保留）
        readme_file = service_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(f"# {service.name}\n\n{service.description}\n\nGenerated by MCP-SWE-Agent")


        # Step 5: 更新数据库状态
        # 重新获取对象防止 Session 冲突
        result = await session.execute(select(MCPService).where(MCPService.id == service_id))
        service = result.scalar_one()

        service.code = generated_code
        # 修正：模型里没有 COMPLETED，改为 READY
        service.status = ServiceStatus.READY 
        service.file_path = str(service_dir)
        service.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        await session.commit()
        logger.info(f"🎉 Service {service_id} processing COMPLETED (Status: READY)!")

    except Exception as e:
        logger.error(f"❌ Failed to process service {service_id}: {e}", exc_info=True)
        
        try:
            result = await session.execute(select(MCPService).where(MCPService.id == service_id))
            service = result.scalar_one()
            
            service.status = ServiceStatus.FAILED
            service.total_errors += 1
            service.updated_at = datetime.utcnow()
            if service.description:
                service.description += f"\n\n[Error Log]: {str(e)}"
            
            await session.commit()
            logger.info(f"⚠️ Marked service {service_id} as FAILED")
        except Exception as db_e:
            logger.critical(f"🔥 Critical DB error: {db_e}")
