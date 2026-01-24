from typing import Dict, List, Any, Optional
import asyncio

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import StdioServerParameters

from logger import logger
from mcp_swe_flow.adapters.mcp_client_adapter import MCPClientAdapter

class MCPToolManager:
    """MCP工具管理器，使用MCPClientAdapter连接服务器，但使用langchain_mcp_adapters管理工具"""
    
    def __init__(self):
        """初始化一个新的MCPToolManager实例。"""
        self._initialized = False
        self.client_adapter = MCPClientAdapter()
        self.lc_tools = None  # langchain_mcp_adapters工具
    
    async def initialize(self, server_params):
        """初始化MCP服务器连接
        
        Args:
            server_params: StdioServerParameters对象
            
        Returns:
            加载的langchain_mcp_adapters工具列表
        """
        if self._initialized:
            return self.lc_tools
        
        try:
            logger.info(f"🔌 初始化MCP服务器连接：{server_params.args}")
            
            # 使用MCPClientAdapter连接服务器
            await self.client_adapter.connect_stdio_with_params(server_params)
            
            # 使用langchain_mcp_adapters加载工具
            self.lc_tools = await load_mcp_tools(self.client_adapter.session)
            
            self._initialized = True
            logger.info(f"✅ 已加载MCP工具: {[t.name for t in self.lc_tools]}")
            
            return self.lc_tools
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_tool_names(self) -> List[str]:
        """获取所有可用工具的名称列表"""
        if not self._initialized:
            raise RuntimeError("MCPToolManager未初始化")
        return [t.name for t in self.lc_tools]
    
    def get_tool_by_name(self, tool_name: str):
        """根据名称获取工具对象"""
        if not self._initialized:
            raise RuntimeError("MCPToolManager未初始化")
        
        tool = next((t for t in self.lc_tools if t.name == tool_name), None)
        if tool is None:
            raise ValueError(f"未找到'{tool_name}'工具")
        return tool
    
    async def invoke_tool(self, tool_name: str, params: Dict[str, Any], max_length: int = 1400) -> Any:
        """通用工具调用方法
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            max_length: 返回内容最大长度
            
        Returns:
            工具执行结果
        """
        if not self._initialized:
            raise RuntimeError("MCPToolManager未初始化")
        
        tool = self.get_tool_by_name(tool_name)
        
        try:
            logger.info(f"🔧 执行MCP工具 '{tool_name}' 参数: {params}")
            result = await tool.ainvoke(params)
            
            # 处理不同类型的结果
            if isinstance(result, dict):
                # 如果结果是字典，保留原始结构
                processed_result = result
                # 如果有content字段且是字符串，截断它
                if "content" in result and isinstance(result["content"], str):
                    content = result["content"]
                    original_length = len(content)
                    if original_length > max_length:
                        logger.info(f"⚠️ 工具返回结果过长 ({original_length} 字符)，已截断")
                        processed_result["content"] = content[:max_length] + f"...[截断]，输出已被MCP适配器截断，这是适配器的限制而非工具本身的问题。共计{original_length}字符，剩余{original_length - max_length}字符"

            elif isinstance(result, str):
                # 如果结果是字符串，直接截断
                original_length = len(result)
                if original_length > max_length:
                    logger.info(f"⚠️ 工具返回结果过长 ({original_length} 字符)，已截断")
                    processed_result = result[:max_length] + f"...[截断]，输出已被MCP适配器截断，这是适配器的限制而非工具本身的问题。共计{original_length}字符，剩余{original_length - max_length}字符"
                else:
                    processed_result = result
            else:
                # 其他类型保持不变
                processed_result = result
            
            # 根据processed_result的类型，正确记录日志
            if isinstance(processed_result, dict) and "content" in processed_result:
                logger.info(f"✅ 工具 '{tool_name}' 执行成功,工具返回结果: {processed_result['content']}")
            else:
                logger.info(f"✅ 工具 '{tool_name}' 执行成功,工具返回结果: {processed_result}")
            return processed_result
        except asyncio.CancelledError:
            logger.warning(f"🟠 工具 '{tool_name}' 的调用被取消。这通常在超时或程序关闭时发生。")
            # 重新抛出异常，以便上层调用（如asyncio.wait_for）可以正确处理超时
            raise
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)


    async def cleanup(self):
        """清理资源"""
        if self._initialized:
            try:
                logger.info("🧹 开始清理MCP工具管理器资源...")
                
                # 使用MCPClientAdapter断开连接
                await self.client_adapter.disconnect()
                
                self._initialized = False
                self.lc_tools = None
                logger.info("✅ MCP工具管理器资源已清理完成")
            except Exception as e:
                logger.error(f"❌ 资源清理失败: {type(e).__name__}: {e}")
