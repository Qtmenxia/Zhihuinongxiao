import argparse
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Ensure the working directory is the project root
project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
sys.path.append(str(project_root))

# A simple logger, as we are in a separate script.
def log(message):
    """一个简单的日志记录器，用于在控制台打印带有时间戳的消息。"""
    print(f"[{datetime.now().isoformat()}] {message}")

async def run_workflow(semaphore, user_input, log_dir, swe_model=None):
    """
    为一个给定的用户输入运行一个单独的工作流实例。
    """
    log(f"⚠️ 批量生成的启动模式只能选择--non-interactive，意味着不能及时调整代码，涉及到敏感信息或者路径信息的功能建议运行run_langgraph_workflow.py。")
    async with semaphore:
        # 为日志文件创建一个唯一的名称以避免冲突
        input_slug = "".join(filter(str.isalnum, user_input))[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        log_file_name = f"run_{timestamp}_{input_slug}.log"
        log_file = log_dir / log_file_name
        
        model_info = f"使用模型: '{swe_model}'" if swe_model else "使用默认模型"
        log(f"正在启动工作流, {model_info}，输入: '{user_input[:40]}...'。日志文件: {log_file.name}")
        
        # 动态构建命令
        command = [
            sys.executable,  # 使用相同的 python 解释器
            "framwork/run_langgraph_workflow.py",
        ]

        if swe_model:
            command.extend(["--swe-model", swe_model])
        
        command.extend([
            "--user-input",
            user_input,
            "--non-interactive"
        ])

        # 将子进程的 stdout/stderr 重定向到日志文件
        with open(log_file, "w", encoding="utf-8") as log_output:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=log_output,
                stderr=asyncio.subprocess.STDOUT
            )

        await process.wait()

        if process.returncode == 0:
            log(f"✅ 成功: 工作流 '{user_input[:40]}...' 执行完毕。")
        else:
            log(f"❌ 失败: 工作流 '{user_input[:40]}...' 执行失败。详情请查看日志: {log_file}")
        
        return process.returncode

async def main():
    parser = argparse.ArgumentParser(
        description="从文件批量运行 MCP Agent LangGraph 工作流。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input-file",
        default="framwork/batch_inputs.txt",
        help="包含每行一个用户输入的文本文件路径。\n默认为: framwork/batch_inputs.txt"
    )
    parser.add_argument(
        "-n", "--parallel-runs",
        type=int,
        default=3,
        help="并行运行的工作流数量 (默认: 3)。"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs/batch_runs",
        help="存储每个工作流运行日志的目录 (默认: logs/batch_runs)。"
    )
    parser.add_argument(
        "--swe-model",
        type=str,
        default=None,
        help="指定用于SWE-Agent的模型 (例如 'deepseek-r1-0528')。"
    )
    
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    input_file_path = Path(args.input_file)
    if not input_file_path.is_file():
        log(f"❌ 错误: 在 '{args.input_file}' 未找到输入文件")
        sys.exit(1)

    with open(input_file_path, "r", encoding="utf-8") as f:
        user_inputs = [line.strip() for line in f if line.strip()]

    if not user_inputs:
        log("输入文件为空，无需执行任何操作。")
        sys.exit(0)

    log(f"在 '{args.input_file}' 文件中找到 {len(user_inputs)} 个用户输入。")
    log(f"将并行运行 {args.parallel_runs} 个工作流。")
    log(f"日志将存储在: {log_dir.resolve()}")
    
    if args.swe_model:
        log(f"将为所有工作流使用 SWE Agent 模型: {args.swe_model}")
    
    semaphore = asyncio.Semaphore(args.parallel_runs)
    tasks = [run_workflow(semaphore, user_input, log_dir, args.swe_model) for user_input in user_inputs]
    
    log("\n--- 开始批处理 ---")
    results = await asyncio.gather(*tasks)

    successful_runs = sum(1 for r in results if r == 0)
    failed_runs = len(results) - successful_runs

    log("\n--- 批处理完成 ---")
    log(f"总共执行的工作流数量: {len(results)}")
    log(f"  - 成功: {successful_runs}")
    log(f"  - 失败: {failed_runs}")
    log(f"日志存储在: {log_dir.resolve()}")
    log("--------------------")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main()) 