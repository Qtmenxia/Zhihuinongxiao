"""
服务部署管理
管理已部署MCP服务的生命周期

支持两种部署模式：
1. 进程模式：直接启动uvicorn进程运行FastAPI服务
2. MCP stdio模式：通过MCPClientAdapter连接MCP服务
"""
import logging
import subprocess
import asyncio
import os
import signal
from typing import Dict, Optional, List, Any
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DeploymentService:
    """服务部署管理器"""
    
    def __init__(self):
        """初始化部署服务"""
        self.running_services: Dict[str, Dict[str, Any]] = {}  # service_id -> deployment_info
        self.base_port = 8100  # 部署服务的起始端口
        self.max_port = 8200   # 最大端口
        self._used_ports: set = set()
        logger.info("DeploymentService initialized")
    
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
        mode: str = "http"  # "http" or "mcp"
    ) -> Dict[str, Any]:
        """
        部署MCP服务
        
        Args:
            service_id: 服务ID
            file_path: 服务代码文件路径
            mode: 部署模式 ("http" 或 "mcp")
            
        Returns:
            dict: 部署结果，包含端点列表
        """
        logger.info(f"Deploying service {service_id} from {file_path} in {mode} mode")
        
        if not file_path or not Path(file_path).exists():
            logger.warning(f"Service file not found at {file_path}")
            raise FileNotFoundError(f"Service file not found: {file_path}")
        
        if mode == "http":
            return await self._deploy_as_http(service_id, file_path)
        elif mode == "mcp":
            return await self._deploy_as_mcp(service_id, file_path)
        else:
            raise ValueError(f"Unknown deployment mode: {mode}")
    
    async def _deploy_as_http(
        self,
        service_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """以HTTP服务方式部署（使用uvicorn）"""
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
            
            logger.info(f"Starting service with command: {' '.join(cmd)} in {service_dir}")
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=str(service_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # 等待服务启动
            await asyncio.sleep(3)
            
            # 检查进程是否正常运行
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self._release_port(port)
                raise RuntimeError(f"Service failed to start: {stderr.decode()}")
            
            # 构建端点URL
            base_url = f"http://localhost:{port}"
            endpoints = [
                f"{base_url}/health",
                f"{base_url}/products",
                f"{base_url}/orders",
                f"{base_url}/docs"
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
                "mode": "http",
                "file_path": file_path
            }
            self.running_services[service_id] = deployment_info
            
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
    
    async def _deploy_as_mcp(
        self,
        service_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """以MCP stdio模式部署"""
        try:
            from backend.mcpybarra_core.framework.mcp_swe_flow.adapters.mcp_client_adapter import MCPClientAdapter
            
            adapter = MCPClientAdapter()
            await adapter.connect_stdio_file(file_path)
            
            tools = await adapter.list_tools()
            endpoints = [tool.name for tool in tools]
            
            deployment_info = {
                "service_id": service_id,
                "adapter": adapter,
                "endpoints": endpoints,
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "mode": "mcp",
                "file_path": file_path
            }
            self.running_services[service_id] = deployment_info
            
            logger.info(f"Service {service_id} deployed as MCP with endpoints: {endpoints}")
            
            return {
                "service_id": service_id,
                "status": "deployed",
                "endpoints": endpoints
            }
            
        except ImportError:
            logger.warning("MCPClientAdapter not available, falling back to HTTP mode")
            return await self._deploy_as_http(service_id, file_path)
        except Exception as e:
            logger.error(f"Failed to deploy service {service_id} as MCP: {e}")
            raise
    
    async def stop_service(self, service_id: str) -> bool:
        """停止已部署的服务"""
        if service_id not in self.running_services:
            logger.warning(f"Service {service_id} not found in deployed services")
            return False
        
        deployment_info = self.running_services[service_id]
        
        try:
            if deployment_info["mode"] == "http":
                process = deployment_info["process"]
                
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                
                self._release_port(deployment_info.get("port", 0))
                
            elif deployment_info["mode"] == "mcp":
                adapter = deployment_info.get("adapter")
                if adapter:
                    await adapter.disconnect()
            
            del self.running_services[service_id]
            logger.info(f"Service {service_id} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop service {service_id}: {e}")
            return False
    
    async def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """获取服务状态"""
        if service_id not in self.running_services:
            return None
        
        deployment_info = self.running_services[service_id]
        
        is_running = False
        if deployment_info["mode"] == "http":
            process = deployment_info.get("process")
            is_running = process and process.poll() is None
        elif deployment_info["mode"] == "mcp":
            is_running = True
        
        return {
            "service_id": service_id,
            "status": "running" if is_running else "stopped",
            "mode": deployment_info.get("mode"),
            "port": deployment_info.get("port"),
            "base_url": deployment_info.get("base_url"),
            "endpoints": deployment_info.get("endpoints", []),
            "deployed_at": deployment_info.get("deployed_at")
        }
    
    async def list_deployed_services(self) -> List[Dict[str, Any]]:
        """列出所有已部署的服务"""
        services = []
        for service_id in list(self.running_services.keys()):
            status = await self.get_service_status(service_id)
            if status:
                services.append(status)
        return services
    
    async def health_check(self, service_id: str) -> bool:
        """检查服务健康状态"""
        if service_id not in self.running_services:
            return False
        
        deployment_info = self.running_services[service_id]
        
        if deployment_info["mode"] == "http":
            health_url = f"{deployment_info.get('base_url', '')}/health"
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        return response.status == 200
            except Exception:
                return False
        
        elif deployment_info["mode"] == "mcp":
            try:
                adapter = deployment_info.get("adapter")
                if adapter:
                    await adapter.list_tools()
                    return True
            except Exception:
                return False
        
        return False
    
    def get_running_services(self) -> List[str]:
        """获取所有运行中的服务ID列表"""
        return list(self.running_services.keys())
    