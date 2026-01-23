from mcp_swe_flow.state import MCPWorkflowState
from mcp_swe_flow.logger import logger

def error_handler_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """处理工作流错误，根据错误来源决定是进入恢复节点还是终止工作流。"""
    logger.error("--- Entering Error Handler Node ---")
    error_msg = state.get('error', 'Unknown error')
    error_source = state.get('error_source', 'unknown')
    logger.error(f"Workflow failed with error from '{error_source}': {error_msg}")
    
    # 来自 server_test 或 code_refiner 的错误应进入恢复流程
    if error_source in ["server_test", "code_refiner"]:
        logger.info(f"Error from '{error_source}' detected, routing to error recovery node.")
        return {**state, "next_step": "error_recovery"}
    
    # 其他来源的错误（例如，来自 load_input 或 swe_generate）将终止工作流
    logger.error(f"Unhandled error source ('{error_source}'), terminating workflow.")
    update = {"next_step": "end"} # 确保工作流终止
    return {**state, **update} 