"""
服务部署管理
管理已部署MCP服务的生命周期
"""
import logging
from typing import Dict, Optional
import subprocess
import asyncio

from backend.mcpybarra_core.framework.mcp_swe_flow.adapters.mcp_client_adapter import MCPClientAdapter

logger = logging.getLogger(__name__)


class DeploymentService:
    """部署服务管理器"""
    
    def __init__(self):
        """初始化部署服务"""
        self.running_services: Dict[str, MCPClientAdapter] = {}
        self.service_processes: Dict[str, subprocess.Popen] = {}
        logger.info("DeploymentService initialized")
    
    async def deploy_service(self, service_id: str, file_path: str) -> dict:
        """
        启动MCP服务并缓存适配器
        
        Args:
            service_id: 服务ID
            file_path: 服务文件路径
            
        Returns:
            dict: 部署结果，包含端点列表
        """
        logger.info(f"Deploying service {service_id} from {file_path}")
        
        try:
            # 初始化MCP客户端适配器
            adapter = MCPClientAdapter()
            
            # 连接到服务(通过文件路径)
            await adapter.connect_stdio_file(file_path)
            
            # 获取可用工具列表
            tools = await adapter.list_tools()
            endpoints = [tool.name for tool in tools]
            
            # 缓存适配器
            self.running_services[service_id] = adapter
            
            logger.info(f"Service {service_id} deployed with endpoints: {endpoints}")
            
            return {
                "service_id": service_id,
                "endpoints": endpoints,
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy service {service_id}: {e}", exc_info=True)
            raise RuntimeError(f"Deployment failed: {str(e)}")
    
    async def stop_service(self, service_id: str):
        """
        停止MCP服务
        
        Args:
            service_id: 服务ID
        """
        logger.info(f"Stopping service {service_id}")
        
        if service_id in self.running_services:
            try:
                adapter = self.running_services[service_id]
                await adapter.disconnect()
                del self.running_services[service_id]
                logger.info(f"Service {service_id} stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping service {service_id}: {e}")
                raise
        else:
            logger.warning(f"Service {service_id} is not running")
    
    async def call_service_tool(
        self,
        service_id: str,
        tool_name: str,
        params: dict
    ) -> dict:
        """
        调用已部署服务的工具
        
        Args:
            service_id: 服务ID
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            dict: 工具执行结果
        """
        # 检查服务是否运行
        if service_id not in self.running_services:
            raise RuntimeError(f"Service {service_id} is not deployed")
        
        adapter = self.running_services[service_id]
        
        try:
            # 调用工具
            result = await adapter.call_tool(tool_name, params)
            return result
            
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} on service {service_id}: {e}")
            raise RuntimeError(f"Tool call failed: {str(e)}")
    
    async def health_check(self, service_id: str) -> bool:
        """
        检查服务健康状态
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 服务是否健康
        """
        if service_id not in self.running_services:
            return False
        
        try:
            adapter = self.running_services[service_id]
            # 尝试列出工具来验证连接
            await adapter.list_tools()
            return True
        except:
            return False
    
    def get_running_services(self) -> list:
        """
        获取所有运行中的服务列表
        
        Returns:
            list: 运行中的服务ID列表
        """
        return list(self.running_services.keys())
