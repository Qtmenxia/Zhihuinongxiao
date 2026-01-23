from mcp_swe_flow.state import MCPWorkflowState
from logger import logger

def human_confirmation_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """等待用户确认继续流程的节点，允许用户在测试前做必要准备"""
    logger.info("进入人工确认节点")
    
    print("\n" + "="*50)
    print(f"✅ MCP服务器代码已生成: {state.get('server_file_path')}")
    print("\n您可以现在进行以下操作:")
    print("- 检查生成的代码")
    print("- 添加所需的API密钥")
    print("- 安装缺失的库依赖")
    
    # 提取并显示可能需要的依赖
    try:
        with open(state.get('server_file_path'), 'r', encoding='utf-8') as f:
            code = f.read()
            imports = [line.strip() for line in code.split('\n') 
                      if line.strip().startswith(('import ', 'from ')) and 'import' in line]
            if imports:
                print("\n可能的依赖项:")
                for imp in imports[:10]:  # 只显示前10个
                    print(f"  {imp}")
                if len(imports) > 10:
                    print(f"  ...以及{len(imports)-10}个更多导入...")
    except Exception as e:
        print(f"无法解析代码中的导入: {e}")
        logger.error(f"无法解析代码中的导入: {e}")
    
    input("\n准备就绪后，请按回车键继续...")
    logger.info("用户已确认继续流程")
    
    # 确保将所有状态传递下去
    update = state.copy()
    update.update({
        "next_step": "server_test",
        "human_confirmed": True
    })
    return update 