"""
服务部署管理
管理已部署MCP服务的生命周期
"""
import logging
from typing import Dict, Optional
import subprocess
import asyncio
import os
import signal
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

from backend.config.settings import settings
from backend.mcpybarra_core.framework.mcp_swe_flow.adapters.mcp_client_adapter import MCPClientAdapter

logger = logging.getLogger(__name__)


class DeploymentService:
    """
    服务部署管理器
    
    支持两种部署模式：
    1. 进程模式：直接启动Python进程运行FastAPI服务
    2. Docker模式：将服务打包为Docker容器运行
    """
    
    def __init__(self):
        self.deployed_services: Dict[str, Dict[str, Any]] = {}  # service_id -> deployment_info
        self.base_port = 8100  # 部署服务的起始端口
        self.max_port = 8200   # 最大端口
        self._used_ports: set = set()
    
    def _allocate_port(self) -> int:
        """分配可用端口"""
        for port in range(self.base_port, self.max_port):
            if port not in self._used_ports:
                self._used_ports.add(port)
                return port
        raise RuntimeError("No available ports for deployment")
    
    def _release_port(self, port: int):
        """释放端口"""
        self._used_ports.discard(port)
    
    async def deploy_service(
        self,
        service_id: str,
        file_path: str,
        mode: str = "process"  # "process" or "docker"
    ) -> Dict[str, Any]:
        """
        部署MCP服务
        
        Args:
            service_id: 服务ID
            file_path: 服务代码文件路径
            mode: 部署模式
        
        Returns:
            Dict: 部署结果，包含端点URL等信息
        """
        logger.info(f"Deploying service {service_id} from {file_path}")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Service file not found: {file_path}")
        
        if mode == "process":
            return await self._deploy_as_process(service_id, file_path)
        elif mode == "docker":
            return await self._deploy_as_docker(service_id, file_path)
        else:
            raise ValueError(f"Unknown deployment mode: {mode}")
        
    async def _deploy_as_process(
        self,
        service_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """以Python进程方式部署服务"""
        port = self._allocate_port()
        
        try:
            # 获取服务文件所在目录和模块名
            service_path = Path(file_path)
            service_dir = service_path.parent
            module_name = service_path.stem
            
            # 构建uvicorn命令
            cmd = [
                "uvicorn",
                f"{module_name}:app",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--workers", "1"
            ]
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=str(service_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # 等待服务启动
            await asyncio.sleep(2)
            
            # 检查进程是否正常运行
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise RuntimeError(f"Service failed to start: {stderr.decode()}")
            
            # 构建端点URL
            base_url = f"http://localhost:{port}"
            endpoints = [
                f"{base_url}/health",
                f"{base_url}/products",
                f"{base_url}/orders",
                f"{base_url}/docs"  # Swagger文档
            ]
            
            # 记录部署信息
            deployment_info = {
                "service_id": service_id,
                "port": port,
                "process": process,
                "pid": process.pid,
                "base_url": base_url,
                "endpoints": endpoints,
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "mode": "process"
            }
            self.deployed_services[service_id] = deployment_info
            
            logger.info(f"Service {service_id} deployed at port {port}, PID: {process.pid}")
            
            return {
                "service_id": service_id,
                "status": "deployed",
                "port": port,
                "base_url": base_url,
                "endpoints": endpoints
            }
            
        except Exception as e:
            self._release_port(port)
            logger.error(f"Failed to deploy service {service_id}: {e}")
            raise
    
    async def _deploy_as_docker(
        self,
        service_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """以Docker容器方式部署服务（预留）"""
        # TODO: 实现Docker部署逻辑
        raise NotImplementedError("Docker deployment not implemented yet")
    
    async def stop_service(self, service_id: str) -> bool:
        """
        停止已部署的服务
        
        Args:
            service_id: 服务ID
        
        Returns:
            bool: 是否成功停止
        """
        if service_id not in self.deployed_services:
            logger.warning(f"Service {service_id} not found in deployed services")
            return False
        
        deployment_info = self.deployed_services[service_id]
        
        try:
            if deployment_info["mode"] == "process":
                process = deployment_info["process"]
                
                # 发送终止信号
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                
                # 释放端口
                self._release_port(deployment_info["port"])
            
            # 移除部署记录
            del self.deployed_services[service_id]
            logger.info(f"Service {service_id} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop service {service_id}: {e}")
            return False
    
    async def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """获取服务状态"""
        if service_id not in self.deployed_services:
            return None
        
        deployment_info = self.deployed_services[service_id]
        
        # 检查进程是否仍在运行
        if deployment_info["mode"] == "process":
            process = deployment_info["process"]
            is_running = process.poll() is None
        else:
            is_running = True  # Docker模式暂时假设运行中
        
        return {
            "service_id": service_id,
            "status": "running" if is_running else "stopped",
            "port": deployment_info.get("port"),
            "base_url": deployment_info.get("base_url"),
            "endpoints": deployment_info.get("endpoints"),
            "deployed_at": deployment_info.get("deployed_at")
        }
    
    async def list_deployed_services(self) -> List[Dict[str, Any]]:
        """列出所有已部署的服务"""
        services = []
        for service_id in list(self.deployed_services.keys()):
            status = await self.get_service_status(service_id)
            if status:
                services.append(status)
        return services
    
    async def health_check(self, service_id: str) -> bool:
        """检查服务健康状态"""
        if service_id not in self.deployed_services:
            return False
        
        deployment_info = self.deployed_services[service_id]
        health_url = f"{deployment_info['base_url']}/health"
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
    
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
    
    def get_running_services(self) -> list:
        """
        获取所有运行中的服务列表
        
        Returns:
            list: 运行中的服务ID列表
        """
        return list(self.running_services.keys())
