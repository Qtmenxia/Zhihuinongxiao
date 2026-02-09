import datetime
import re
from mcp_swe_flow.state import MCPWorkflowState
from logger import logger

def error_recovery_node(state: MCPWorkflowState) -> MCPWorkflowState:
    """错误恢复节点，根据错误来源提供不同的恢复选项，允许用户解决问题后继续工作流。"""
    logger.info("--- Entering Error Recovery Node ---")
    error_source = state.get("error_source", "unknown")
    error_msg = state.get("error", "未知错误")

    # --- 向用户显示错误信息和通用建议 ---
    print("\n" + "="*30)
    print(f"❌ 工作流在 '{error_source}' 节点遇到错误。")
    try:
        print(f"   错误详情: {error_msg}")
    except UnicodeEncodeError:
        # 降级显示,避免控制台崩溃
        print(f"   错误详情: {error_msg.encode('ascii', errors='ignore').decode('ascii')}")

    print("="*30)
    
    print("\n🔍 问题排查建议:")
    if "ModuleNotFoundError" in error_msg or "ImportError" in error_msg:
        module_match = re.search(r"No module named '([^']*)'", error_msg)
        missing_module = module_match.group(1) if module_match else "未知模块"
        print(f"  - 似乎缺少 Python 依赖: '{missing_module}'。")
    elif "Connection closed" in error_msg or "process exited" in error_msg:
        print("  - 服务器进程可能启动失败或意外崩溃。")
        print("    👉 请检查生成的代码是否存在语法错误或初始化问题。")
        print("    👉 确认所有必需的环境变量（如 API 密钥）都已正确设置。")
    else:
        print("  - 请检查终端中的详细日志以获取更多线索。")
        print("  - 检查生成的代码或相关配置文件。")

    # --- 根据错误来源提供特定的恢复选项 ---
    if error_source == "server_test":
        print("\n🛠️ 您希望如何操作？ (服务器测试失败)")
        print("  1. 重试测试 (默认选项，直接按 Enter)")
        print("  2. 跳过测试，直接进入代码优化阶段")
        print("  3. 退出工作流")
        
        choice = input("\n您的选择 [1]: ").strip().lower()
        
        if choice == "2" or choice == "skip":
            logger.info("用户选择跳过测试并进入优化阶段。")
            empty_report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "server": state.get("server_file_path", "未知"),
                "status": "skipped_after_error",
                "message": "用户在测试节点遇到错误后选择跳过测试。",
                "tests": []
            }
            return {
                **state, 
                "error": None,
                "error_source": None,
                "next_step": "refine_code",
                "test_report_content": empty_report,
            }
        elif choice == "3" or choice == "exit":
            logger.info("用户选择退出工作流。")
            return {**state, "next_step": "end"}
        else:
            logger.info("用户选择重试测试。")
            return {**state, "error": None, "error_source": None, "next_step": "server_test"}

    elif error_source == "code_refiner":
        print("\n🛠️ 您希望如何操作？ (代码优化失败)")
        print("  1. 重试优化 (默认选项，直接按 Enter)")
        print("  2. 退出工作流")
        
        choice = input("\n您的选择 [1]: ").strip().lower()

        if choice == "2" or choice == "exit":
            logger.info("用户选择退出工作流。")
            return {**state, "next_step": "end"}
        else:
            logger.info("用户选择重试优化。")
            return {**state, "error": None, "error_source": None, "next_step": "refine_code"}
    
    else:
        logger.warning(f"'{error_source}' 没有特定的恢复路径，工作流将终止。")
        print("\n" + "!"*60)
        print("! 未知的错误来源，无法提供恢复选项。工作流将退出。")
        print("!"*60)
        return {**state, "next_step": "end"} 