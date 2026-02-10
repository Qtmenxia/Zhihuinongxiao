from typing import Dict, List, Any, Optional
import sys
from pathlib import Path
import asyncio
import httpx

from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from mcp.shared.exceptions import McpError

from logger import logger
from mcp_swe_flow.adapters import MCPToolAdapter

class MCPClientAdapter:
    """
    一个适配器，用于简化与MCP服务器的STDIO连接。
    每个实例管理一个独立的服务器连接。
    """
    def __init__(self):
        """初始化一个新的MCPClientAdapter实例。"""
        self.session: Optional[ClientSession] = None
        self.process = None
        self._lock = asyncio.Lock()
        self._initialized = False
        self.exit_stack = AsyncExitStack()
        self.tools: List[MCPToolAdapter] = []
        
    async def _send_http_request(self, server_url: str, method: str, params: Dict[str, Any]) -> Any:
        """使用 httpx 发送一个包含自定义头部的 JSON-RPC 2.0 HTTP POST 请求"""
        headers = {
            "X-Context7-Source": "mcp-server",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        json_rpc_payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(server_url, json=json_rpc_payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                response_json = response.json()
                if "error" in response_json:
                    raise McpError(f"JSON-RPC Error from server: {response_json['error']}")
                return response_json.get("result")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP请求失败: {e.response.status_code} - {e.response.text}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"发送HTTP请求时出错: {e}", exc_info=True)
                raise

    async def connect_stdio(self, module_name: str, cwd: Optional[Path] = None, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """通过STDIO连接MCP服务器
        
        Args:
            module_name: 模块名称 (如 "output-servers.mcp-chucknorris")
            cwd: 工作目录，默认当前目录
            max_output_length: 工具返回结果的最大长度，默认为1200个字符
            
        Returns:
            适配后的LangChain工具列表
        """
        if self.session:
            await self.disconnect()
            
        try:
            logger.info(f"🔌 正在连接MCP服务器模块: {module_name}")
            
            # 准备参数
            command = sys.executable
            args = ["-m", module_name]
            cwd_str = str(cwd) if cwd else None
            
            logger.info(f"🔄 准备启动命令: {command} {' '.join(args)}, cwd={cwd_str}")
            
            # 使用与 framwork/tool/mcp.py 相同的方式
            # 尽量把 cwd 传进去（不同版本 mcp 可能 StdioServerParameters 参数不同，做兼容）
            try:
                server_params = StdioServerParameters(command=command, args=args, cwd=cwd_str)
            except TypeError:
                server_params = StdioServerParameters(command=command, args=args)
            logger.info(f"🔄 创建服务器参数: {server_params}")

            # ---- 预检：先试启动 0.8s，若秒退则抓 stdout/stderr ----
            try:
                proc = await asyncio.create_subprocess_exec(
                    command, *args,
                    cwd=cwd_str,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await asyncio.sleep(0.8)
                ret = proc.returncode
                if ret is not None:
                    out = (await proc.stdout.read()).decode("utf-8", errors="ignore")
                    err = (await proc.stderr.read()).decode("utf-8", errors="ignore")
                    logger.error("❌ MCP server 进程启动后立刻退出 (returncode={})", ret)
                    if out.strip():
                        logger.error("---- server stdout ----\n{}", out[-max_output_length:])
                    if err.strip():
                        logger.error("---- server stderr ----\n{}", err[-max_output_length:])
                    raise RuntimeError("MCP server 秒退：请根据 stderr 修复生成代码/依赖/环境变量后重试")
                # 仍在运行：终止预检进程（避免占用），然后走 stdio_client 正式连接
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=1.0)
                except Exception:
                    proc.kill()
            except Exception as precheck_exc:
                # 预检失败不应该吞掉信息
                logger.error("❌ MCP server 预检失败: {}", precheck_exc, exc_info=True)
                raise
            # ---- 预检结束 ----
            
            # 通过subprocess启动并连接到MCP服务器
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # 创建会话
            read, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            logger.info(f"✅ MCP服务器连接成功")
            
            # 初始化会话
            await self.session.initialize()
            logger.info("✅ MCP会话初始化成功")
            
            self._initialized = True
            
            # 获取并转换工具
            return await self.load_tools(max_output_length=max_output_length)
            
        except Exception as e:
            logger.error(f"❌ MCP服务器连接失败: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            if self.session:
                await self.disconnect()
            raise

    async def load_tools(self, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """从MCP服务器加载工具并转换为LangChain工具
        
        Args:
            max_output_length: 工具返回结果的最大长度，默认为1200个字符
            
        Returns:
            适配后的LangChain工具列表
        """
        if not self.session:
            raise RuntimeError("MCP会话未初始化")
            
        try:
            # 获取工具列表
            response = await self.session.list_tools()
            logger.info(f"📋 从MCP服务器获取到 {len(response.tools)} 个工具")
            
            # 清空现有工具
            self.tools = []
            
            # 转换工具
            for tool in response.tools:
                try:
                    # 创建适配器
                    adapter = MCPToolAdapter(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.inputSchema,
                        session=self.session,
                        max_output_length=max_output_length
                    )
                    self.tools.append(adapter)
                    logger.info(f"✅ 成功转换工具: {tool.name}")
                except Exception as e:
                    logger.error(f"❌ 工具 {tool.name} 转换失败: {e}", exc_info=True)
            
            logger.info(f"🧰 共转换 {len(self.tools)} 个工具: {[tool.name for tool in self.tools]}")
            return self.tools
            
        except Exception as e:
            logger.error(f"❌ 工具加载失败: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            raise
    
    async def disconnect(self):
        """断开与MCP服务器的连接并清理资源。"""
        async with self._lock:
            if not self._initialized:
                return

            logger.info("👋 正在断开MCP服务器连接...")
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                logger.warning(f"🟠 断开连接时发生可忽略的错误 (通常在测试结束时): {type(e).__name__}", exc_info=True)
            finally:
                self.session = None
                self.process = None
                self._initialized = False
                self.tools = []
                self.exit_stack = AsyncExitStack()
                logger.info("👋 已断开MCP服务器连接") 

    async def connect_stdio_with_params(self, server_params: StdioServerParameters, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """通过传入的StdioServerParameters连接MCP服务器
        
        Args:
            server_params: MCP服务器的STDIO启动参数
            max_output_length: 工具返回结果的最大长度，默认为1200个字符
            
        Returns:
            适配后的LangChain工具列表
        """
        if self.session:
            await self.disconnect()
            
        try:
            logger.info(f"🔌 正在通过预设参数连接MCP服务器: {server_params}")
            
            # 通过subprocess启动并连接到MCP服务器
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # 创建会话
            read, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            logger.info(f"✅ MCP服务器连接成功")
            
            # 初始化会话
            await self.session.initialize()
            logger.info("✅ MCP会话初始化成功")
            
            self._initialized = True
            
            # 获取并转换工具
            return await self.load_tools(max_output_length=max_output_length)
            
        except Exception as e:
            logger.error(f"❌ MCP服务器连接失败: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            if self.session:
                await self.disconnect()
            raise

    async def connect_stdio_file(self, file_path: str, cwd: Optional[Path] = None, max_output_length: int = 1200) -> List[MCPToolAdapter]:
        """通过直接运行Python文件来连接MCP服务器
        
        Args:
            file_path: Python文件的路径 (如 "workspace/pipeline-output-servers/gemini-2.5-pro/mcp_word_document_processor/mcp_word_document_processor.py")
            cwd: 工作目录，默认当前目录
            max_output_length: 工具返回结果的最大长度，默认为1200个字符
            
        Returns:
            适配后的LangChain工具列表
        """
        if self.session:
            await self.disconnect()
            
        try:
            logger.info(f"🔌 正在通过文件路径连接MCP服务器: {file_path}")
            
            # 确保文件路径存在
            if not Path(file_path).exists():
                raise FileNotFoundError(f"MCP服务器文件不存在: {file_path}")
            
            # 准备参数
            command = sys.executable
            args = [file_path]  # 直接运行Python文件
            cwd_str = str(cwd) if cwd else None
            
            logger.info(f"🔄 准备启动命令: {command} {' '.join(args)}, cwd={cwd_str}")
            
            # 使用与 framwork/tool/mcp.py 相同的方式
            server_params = StdioServerParameters(command=command, args=args)
            logger.info(f"🔄 创建服务器参数: {server_params}")
            
            # 通过subprocess启动并连接到MCP服务器
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # 创建会话
            read, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            logger.info(f"✅ MCP服务器连接成功")
            
            # 初始化会话
            await self.session.initialize()
            logger.info("✅ MCP会话初始化成功")
            
            self._initialized = True
            
            # 获取并转换工具
            return await self.load_tools(max_output_length=max_output_length)
            
        except Exception as e:
            logger.error(f"❌ MCP服务器连接失败: {e}", exc_info=True)
            if isinstance(e, ExceptionGroup):
                for i, sub_exc in enumerate(e.exceptions):
                    logger.error(f"  -> Sub-exception [{i+1}/{len(e.exceptions)}]: {sub_exc}", exc_info=True)
            if self.session:
                await self.disconnect()
            raise 