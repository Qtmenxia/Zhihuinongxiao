"""
认证中间件
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证中间件
    
    验证请求的JWT令牌，但对公开路由放行
    """
    
    # 不需要认证的公开路径
    PUBLIC_PATHS: List[str] = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/farmers/register",
        "/api/v1/farmers/login",
        "/api/v1/products",  # 产品列表公开访问
    ]
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
        """
        path = request.url.path
        
        # 检查是否为公开路径
        if self._is_public_path(path):
            return await call_next(request)
        
        # 检查Authorization头
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            # 对于需要认证的路径，返回401
            if not self._is_optional_auth_path(path):
                logger.warning(f"Unauthorized access attempt to {path}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        # 继续处理请求(具体的token验证在dependencies中进行)
        response = await call_next(request)
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """检查是否为公开路径"""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False
    
    def _is_optional_auth_path(self, path: str) -> bool:
        """检查是否为可选认证路径(未登录也能访问但功能受限)"""
        optional_paths = [
            "/api/v1/products",
        ]
        for optional_path in optional_paths:
            if path.startswith(optional_path):
                return True
        return False
