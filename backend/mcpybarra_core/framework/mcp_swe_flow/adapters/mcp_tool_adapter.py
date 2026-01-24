from typing import Any, Dict, List, Optional, Union, Callable
import asyncio
from langchain_core.tools import BaseTool, ToolException
from pydantic.v1 import BaseModel, Field
from langchain_core.messages import ToolMessage
from mcp import ClientSession
from mcp.types import TextContent
import json

from logger import logger

class MCPToolAdapter(BaseTool):
    """将MCP工具适配到LangChain工具格式"""
    
    name: str = Field(description="工具的名称")
    description: str = Field(description="工具的描述")
    args_schema: Dict[str, Any] = Field(default_factory=dict, description="工具参数的JSON Schema")
    max_output_length: int = Field(default=2000, description="工具返回结果的最大长度")
    
    # 使用 getter/setter 来处理会话属性
    _session: Optional[ClientSession] = None
    ainvoke_override: Optional[Callable] = None
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        parameters: Dict[str, Any], 
        session: Optional[ClientSession],
        max_output_length: int = 2000,
        ainvoke_override: Optional[Callable] = None
    ):
        """初始化MCP工具适配器"""
        super().__init__(
            name=name,
            description=description,
            args_schema=parameters
        )
        self._session = session
        self.max_output_length = max_output_length
        self.ainvoke_override = ainvoke_override
    
    def _run(self, **kwargs) -> str:
        """同步执行MCP工具调用（为满足BaseTool的抽象方法要求）"""
        raise NotImplementedError("只支持异步执行，请使用_arun方法。")
    
    def _truncate_output(self, output: str) -> str:
        """截断过长的输出结果
        
        Args:
            output: 原始输出结果
            
        Returns:
            截断后的输出结果，如果长度超过限制，会追加截断提示
        """
        if len(output) <= self.max_output_length:
            return output
            
        truncated = output[:self.max_output_length]
        remaining_length = len(output) - self.max_output_length
        truncation_msg = f"\n\n[输出已截断，剩余 {remaining_length} 个字符未显示。总长度: {len(output)}]"
        return truncated + truncation_msg
    
    async def _arun(self, **kwargs) -> str:
        """异步执行MCP工具调用"""
        # 优先使用覆盖的ainvoke方法
        if self.ainvoke_override:
            return await self.ainvoke_override(kwargs)

        if not self._session:
            raise ToolException("MCP会话未初始化")
            
        try:
            logger.info(f"🔧 执行MCP工具 '{self.name}' 参数: {kwargs}")
            
                # 添加参数类型转换
            converted_args = {}
            for key, value in kwargs.items():
                # 检查参数模式以确定预期类型
                param_schema = self.args_schema.get("properties", {}).get(key, {})
                expected_type = param_schema.get("type", "string")
                
                # 如果期望字符串但收到数字，进行转换
                if expected_type == "string" and isinstance(value, (int, float)):
                    converted_args[key] = str(value)
                    logger.debug(f"参数 '{key}' 已从 {type(value).__name__} 转换为 string")
                else:
                    converted_args[key] = value
            
            # 调用MCP工具，使用转换后的参数
            result = await self._session.call_tool(self.name, converted_args)
            
                
            # 从结果中提取文本内容
            content_str = ", ".join(
                item.text for item in result.content if isinstance(item, TextContent)
            )
            
            # --- 智能截断逻辑 ---
            original_length = len(content_str)
            if original_length > self.max_output_length:
                logger.info(f"⚠️ MCP工具 '{self.name}' 返回结果过长 ({original_length} 字符)，将尝试智能截断。")
                try:
                    # 尝试将结果解析为JSON
                    data = json.loads(content_str)
                    
                    # 如果是JSON，则智能地截断其内部
                    was_truncated = False
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 3:
                                data[key] = value[:3] # 只保留列表的前3个元素
                                was_truncated = True
                                logger.info(f"  - 截断了列表 '{key}' 至前3个元素。")
                            elif isinstance(value, str) and len(value) > 1000:
                                data[key] = value[:1000] + "..." # 截断长字符串
                                was_truncated = True
                                logger.info(f"  - 截断了字符串 '{key}'。")
                    
                    if was_truncated:
                        data["__truncation_alert__"] = "This JSON object has been intelligently truncated to save space. Lists may be shortened."
                        # 添加明确的适配器截断标记
                        data["__adapter_truncation_note__"] = "NOTE: This truncation is due to the MCP adapter's output length limit, NOT an issue with the tool itself."

                    # 将截断后的JSON转换回字符串
                    content_str = json.dumps(data, ensure_ascii=False)
                    logger.info(f"  - 成功执行智能JSON截断。")

                except json.JSONDecodeError:
                    # 如果不是JSON，则执行原始的暴力截断
                    logger.info(f"  - 内容非JSON，执行标准文本截断。")
                    truncated = content_str[:self.max_output_length]
                    remaining_length = len(content_str) - self.max_output_length
                    # 添加明确的适配器截断标记
                    truncation_msg = f"\n\n[ADAPTER_TRUNCATION_NOTE: 输出已被MCP适配器截断，这是适配器的限制而非工具本身的问题。剩余 {remaining_length} 个字符未显示。总长度: {len(content_str)}]"
                    content_str = truncated + truncation_msg
            
            # --- 硬性长度限制检查 ---
            hard_limit = self.max_output_length + 1000
            if len(content_str) > hard_limit:
                logger.warning(f"  - 智能截断后长度 ({len(content_str)}) 仍超过硬性限制 ({hard_limit})，将执行最终截断。")
                content_str = content_str[:hard_limit] + f"\n\n[ADAPTER_TRUNCATION_NOTE: 输出已被MCP适配器硬性截断，这是适配器的限制而非工具本身的问题。原始长度: {original_length}]"

            logger.info(f"✅ MCP工具 '{self.name}' 执行成功：{content_str}")
            return content_str or "No output returned."
            
        except Exception as e:
            error_msg = f"❌ MCP工具 '{self.name}' 执行失败: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}" 