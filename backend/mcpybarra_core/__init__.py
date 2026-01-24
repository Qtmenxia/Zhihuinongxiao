"""
MCPybarra框架初始化
设置正确的Python路径以支持MCPybarra的导入方式
"""
import sys
from pathlib import Path

# 将mcp_swe_flow目录添加到Python路径
# 这样可以支持 `from mcp_swe_flow.xxx import xxx` 的导入方式
MCP_SWE_FLOW_DIR = Path(__file__).parent / "framework"
if str(MCP_SWE_FLOW_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_SWE_FLOW_DIR))

# 同时添加tool目录（某些文件直接从tool导入）
TOOL_DIR = MCP_SWE_FLOW_DIR / "mcp_swe_flow" / "tool"
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

# 添加mcp_swe_flow目录本身（支持from logger import logger等）
MCP_FLOW_DIR = MCP_SWE_FLOW_DIR / "mcp_swe_flow"
if str(MCP_FLOW_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_FLOW_DIR))
