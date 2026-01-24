"""
智农链销 - FastAPI主应用入口
基于MCPybarra多智能体框架的农产品电商赋能平台
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from backend.api.routers import (
    service_generation,
    farmer_management,
    product_management,
    order_management,
    statistics
)
from backend.api.middleware.auth import AuthMiddleware
from backend.api.middleware.logging import LoggingMiddleware
from backend.config.settings import settings
from backend.database.connection import engine, init_db

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 Starting ZhiNongLianXiao API Server...")
    
    # 初始化数据库
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
    
    # 预热MCPybarra工作流(可选)
    try:
        from backend.mcpybarra_core.framework.mcp_swe_flow.graph import create_mcp_swe_workflow
        workflow = create_mcp_swe_workflow()
        logger.info("✅ MCPybarra workflow preloaded")
    except Exception as e:
        logger.warning(f"⚠️ Failed to preload MCPybarra workflow: {e}")
    
    logger.info("✅ Application startup complete")
    
    yield  # 应用运行中
    
    # 关闭时执行
    logger.info("🛑 Shutting down application...")
    # 清理资源
    logger.info("✅ Cleanup complete")


# 创建FastAPI应用实例
app = FastAPI(
    title="智农链销 API",
    description="""
    基于MCPybarra多智能体框架的AI农产品电商赋能平台
    
    ## 核心功能
    - **AI服务生成**: 自然语言转电商服务，成本降低99.9%
    - **产品管理**: 蒲县有机水果产品管理
    - **订单处理**: 全生命周期订单管理
    - **数据分析**: 实时统计与成本监控
    
    ## 技术特点
    - MCPybarra框架(ICSOC 2025投稿)
    - 质量评分72%超越人工
    - 服务生成成本$0.018-0.14
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ==================== 中间件配置 ====================

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Request-ID"]
)

# 自定义中间件
app.add_middleware(LoggingMiddleware)
# 注意：AuthMiddleware只对需要认证的路由生效，健康检查等公开路由不受影响


# ==================== 全局异常处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "path": str(request.url)
        }
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource '{request.url.path}' was not found",
            "path": str(request.url)
        }
    )


# ==================== 路由注册 ====================

# 健康检查(公开接口)
@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查接口
    
    返回系统运行状态和版本信息
    """
    return {
        "status": "healthy",
        "version": app.version,
        "service": "ZhiNongLianXiao API"
    }


@app.get("/", tags=["系统"])
async def root():
    """
    根路径欢迎信息
    """
    return {
        "message": "欢迎使用智农链销API",
        "description": "基于MCPybarra的AI农产品电商赋能平台",
        "docs": "/docs",
        "health": "/health"
    }


# 注册业务路由
app.include_router(
    service_generation.router,
    prefix=f"{settings.API_PREFIX}/services",
    tags=["服务生成"]
)

app.include_router(
    farmer_management.router,
    prefix=f"{settings.API_PREFIX}/farmers",
    tags=["农户管理"]
)

app.include_router(
    product_management.router,
    prefix=f"{settings.API_PREFIX}/products",
    tags=["产品管理"]
)

app.include_router(
    order_management.router,
    prefix=f"{settings.API_PREFIX}/orders",
    tags=["订单管理"]
)

app.include_router(
    statistics.router,
    prefix=f"{settings.API_PREFIX}/statistics",
    tags=["数据统计"]
)


# ==================== WebSocket支持 ====================

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json

# 管理活动的WebSocket连接
active_connections: Dict[str, WebSocket] = {}


@app.websocket("/ws/service/{service_id}")
async def websocket_endpoint(websocket: WebSocket, service_id: str):
    """
    WebSocket端点 - 实时推送服务生成进度
    
    Args:
        service_id: 服务任务ID
    """
    await websocket.accept()
    active_connections[service_id] = websocket
    
    try:
        while True:
            # 保持连接活跃
            data = await websocket.receive_text()
            
            # 可以处理客户端发送的心跳或控制消息
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for service {service_id}")
    finally:
        if service_id in active_connections:
            del active_connections[service_id]


async def notify_service_progress(service_id: str, progress_data: dict):
    """
    通过WebSocket推送服务生成进度
    
    Args:
        service_id: 服务任务ID
        progress_data: 进度数据
    """
    if service_id in active_connections:
        try:
            await active_connections[service_id].send_text(json.dumps(progress_data))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")


# ==================== 性能监控中间件 ====================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加响应时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ==================== 启动入口 ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
