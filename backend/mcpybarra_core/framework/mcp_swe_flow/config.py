from pathlib import Path
from langchain_openai import ChatOpenAI
from logger import logger, get_agent_logger
import uuid
from langchain_core.callbacks import BaseCallbackHandler
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
import re

# Load environment variables from a .env file at the project root
# The .env file should be located at the same level as the 'framwork' directory
load_dotenv(override=True)

# Define default paths relative to the project root
# Assuming the script is run from the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DEFAULT_RESOURCES_DIR = PROJECT_ROOT / "resources"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "workspace/output-servers"
DEFAULT_REFINEMENT_DIR = PROJECT_ROOT / "workspace/refinement"
DEFAULT_TEST_REPORT_DIR = PROJECT_ROOT / "workspace/server-test-report"

# --- Centralized Model Configuration ---
# Maps model names to their provider configuration.
# The key is a regex pattern to match the start of a model name.
MODEL_CONFIG = {
    # ====== OpenRouter Provider (优先匹配，支持多种模型) ======
    # OpenRouter 模型命名格式: openrouter/provider/model
    # 例如: openrouter/anthropic/claude-3.5-sonnet, openrouter/openai/gpt-4o
    r"^openrouter/": {
        "provider": "openrouter",
        "env_prefix": "OPENROUTER",
        "costs": {
            # Anthropic models via OpenRouter
            "openrouter/anthropic/claude-3.5-sonnet": {"prompt": 0.000003, "completion": 0.000015},
            "openrouter/anthropic/claude-3-opus": {"prompt": 0.000015, "completion": 0.000075},
            "openrouter/anthropic/claude-3-haiku": {"prompt": 0.00000025, "completion": 0.00000125},
            # OpenAI models via OpenRouter
            "openrouter/openai/gpt-4o": {"prompt": 0.000005, "completion": 0.000015},
            "openrouter/openai/gpt-4o-mini": {"prompt": 0.00000015, "completion": 0.0000006},
            "openrouter/openai/gpt-4-turbo": {"prompt": 0.00001, "completion": 0.00003},
            # Google models via OpenRouter
            "openrouter/google/gemini-2.0-flash-exp": {"prompt": 0.0, "completion": 0.0},
            "openrouter/google/gemini-pro-1.5": {"prompt": 0.00000125, "completion": 0.000005},
            # DeepSeek models via OpenRouter
            "openrouter/deepseek/deepseek-chat": {"prompt": 0.00000014, "completion": 0.00000028},
            "openrouter/deepseek/deepseek-r1": {"prompt": 0.00000055, "completion": 0.00000219},
            # Meta Llama models via OpenRouter
            "openrouter/meta-llama/llama-3.1-405b-instruct": {"prompt": 0.000003, "completion": 0.000003},
            "openrouter/meta-llama/llama-3.1-70b-instruct": {"prompt": 0.00000052, "completion": 0.00000075},
            # Qwen models via OpenRouter
            "openrouter/qwen/qwen-2.5-72b-instruct": {"prompt": 0.00000035, "completion": 0.0000004},
            # Mistral models via OpenRouter
            "openrouter/mistralai/mistral-large": {"prompt": 0.000002, "completion": 0.000006},
            "default": {"prompt": 0.000002, "completion": 0.000006}
        }
    },
    
    # Qwen models via Dashscope
    r"^(qwen|deepseek)-": {
        "provider": "qwen",
        "env_prefix": "QWEN",
        "costs": {
            "qwen-max": {"prompt": 0.0000024, "completion": 0.0000096},
            "qwen-max-latest": {"prompt": 0.0000024, "completion": 0.0000096},
            "qwen-plus": {"prompt": 0.0000008, "completion": 0.000002},
            "deepseek-v3": {"prompt": 0.000002, "completion": 0.000008},
            "deepseek-r1-0528": {"prompt": 0.000004, "completion": 0.0000016},
            "default": {"prompt": 0.0000024, "completion": 0.0000096} # Fallback for other qwen models
        }
    },

    # Models via GPTSAPI (ChatGPT, Claude)
    r"^(gpt|claude)-": {
        "provider": "gptsapi",
        "env_prefix": "GPTSAPI",
        "costs": {
            "claude-sonnet-4-20250514": {"prompt": 0.00002376, "completion": 0.0001188},
            "gpt-4o": {"prompt": 0.000018, "completion": 0.000072},
            "gemini-2.5-pro-preview-03-25": {"prompt": 0.00000138, "completion": 0.000011},
            "default": {"prompt": 0.00002, "completion": 0.00006} # Generic fallback
        }
    },
    # Gemini models
    r"^gemini-": {
        "provider": "gemini",
        "env_prefix": "GEMINI",
        "costs": {
            "gemini-2.5-pro": {"prompt": 0.00000138, "completion": 0.000011},
            "default": {"prompt": 0.0000025, "completion": 0.000005}
        }
    },
    # Default fallback for any other model
    "default": {
        "provider": "default",
        "env_prefix": "LLM", # Uses the original LLM_... variables
        "costs": {
            "default": {"prompt": 0.0000008, "completion": 0.000002}
        }
    }
}

# --- Agent-to-Model Mapping ---
# Defines which model each agent type should use by default.
# This allows for using stronger models for creative tasks (like code generation)
# and more economical models for routine tasks (like reporting).
AGENT_MODEL_MAPPING = {
    "SWE-Agent-": os.getenv("SWE_AGENT_MODEL", "gpt-4o"),
    "ServerTest-Agent-": os.getenv("SERVER_TEST_AGENT_MODEL", "qwen-plus"),
    "CodeRefiner-Agent-": os.getenv("CODE_REFINER_AGENT_MODEL", "qwen-plus"),
    "default": os.getenv("DEFAULT_AGENT_MODEL", "qwen-plus"),
}

def get_provider_config(model_name: str) -> Dict[str, Any]:
    """Finds the provider configuration for a given model name."""
    for pattern, config in MODEL_CONFIG.items():
        if pattern != "default" and re.match(pattern, model_name):
            return config
    return MODEL_CONFIG["default"]

def calculate_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, float]:
    """Calculates the token cost for a given model."""
    provider_config = get_provider_config(model_name)
    model_cost_config = provider_config["costs"]
    
    # Find specific cost or use default for that provider
    costs = model_cost_config.get(model_name, model_cost_config["default"])
    
    prompt_cost = prompt_tokens * costs["prompt"]
    completion_cost = completion_tokens * costs["completion"]
    total_cost = prompt_cost + completion_cost
    
    return {
        "prompt_cost": prompt_cost,
        "completion_cost": completion_cost,
        "total_cost": total_cost
    }

# Token计数回调处理器
class TokenCounterHandler(BaseCallbackHandler):
    """跟踪LLM调用的token使用情况的回调处理器"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_logger = get_agent_logger(agent_name)
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """记录LLM调用开始"""
        self.call_id = str(uuid.uuid4())
        
        # 估计prompts的token数量
        prompt_tokens = 0
        try:
            # 使用内置的tokenizer估算token数量
            import tiktoken
            tokenizer = tiktoken.encoding_for_model(serialized.get("kwargs", {}).get("model", "gpt-3.5-turbo"))
            for prompt in prompts:
                prompt_tokens += len(tokenizer.encode(prompt))
        except ImportError:
            # 如果没有tiktoken，则使用简单估计（每4个字符约1个token）
            for prompt in prompts:
                prompt_tokens += len(prompt) // 4
        
        # 创建带有提示词token估计的日志
        self.agent_logger.log(
            event_type="llm_invoke", 
            call_id=self.call_id,
            model=serialized.get("kwargs", {}).get("model", "unknown"),
            usage_metadata={
                "input_tokens": prompt_tokens,
                "model": serialized.get("kwargs", {}).get("model", "unknown")
            }
        )
        
    def on_llm_end(self, response: Any, **kwargs):
        """记录LLM调用结束和token使用"""
        usage = response.llm_output.get("token_usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        # 计算成本（如果需要）
        model_name = response.llm_output.get("model_name", "unknown")
        costs = calculate_cost(model_name, prompt_tokens, completion_tokens)
        
        # 记录使用信息
        self.agent_logger.log_llm_usage(
            call_id=self.call_id,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            prompt_cost=costs["prompt_cost"],
            completion_cost=costs["completion_cost"]
        )
        
        # 记录响应日志
        self.agent_logger.log(event_type="llm_response", 
                           call_id=self.call_id,
                           usage_metadata={
                               "model": model_name,
                               "input_tokens": prompt_tokens,
                               "output_tokens": completion_tokens,
                               "total_tokens": total_tokens,
                               "cost": costs["total_cost"]
                           })
                       
    def on_llm_error(self, error: Exception, **kwargs):
        """记录LLM调用错误"""
        self.agent_logger.log(event_type="llm_exception", 
                           call_id=getattr(self, "call_id", str(uuid.uuid4())),
                           error=str(error))

# --- Dynamic LLM Instantiation ---
# Global llm and llm_with_tools are removed.

def get_llm_for_agent(agent_name: str, model_override: Optional[str] = None) -> ChatOpenAI:
    """
    Dynamically gets an LLM instance for a specific agent.
    - If a 'model_override' is provided for an 'SWE-Agent', it will be used.
    - Otherwise, it determines the correct model from AGENT_MODEL_MAPPING.
    """
    # Step 1: Determine the model name
    model_name = None
    # Priority for SWE-Agent override
    if agent_name.startswith("SWE-Agent-") and model_override:
        model_name = model_override
        logger.info(f"Using model override '{model_override}' for SWE-Agent.")
    
    # Fallback to agent mapping
    if not model_name:
        model_name = AGENT_MODEL_MAPPING.get("default", "qwen-plus") # Fallback
        for prefix, model in AGENT_MODEL_MAPPING.items():
            if agent_name.startswith(prefix):
                model_name = model
                break

    # Step 2: Get provider config and credentials for the determined model
    provider_config = get_provider_config(model_name)
    env_prefix = provider_config["env_prefix"]
    
    base_url = os.getenv(f"{env_prefix}_BASE_URL")
    api_key = os.getenv(f"{env_prefix}_API_KEY")
    
    if not base_url or not api_key:
        error_msg = f"Missing environment variables for provider '{provider_config['provider']}'. Please set {env_prefix}_BASE_URL and {env_prefix}_API_KEY."
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", 64000))
    llm_temperature = float(os.getenv("LLM_TEMPERATURE", 0.6))
    llm_enable_thinking = os.getenv("LLM_ENABLE_THINKING", "false").lower() == "true"

    token_handler = TokenCounterHandler(agent_name)
    
    try:
        # 根据不同的提供商设置不同的extra_body和default_headers
        extra_body = {}
        default_headers = {}
        
        # OpenRouter 特有配置
        if provider_config['provider'] == 'openrouter':
            # OpenRouter 需要额外的 HTTP 头用于追踪和识别
            site_url = os.getenv("OPENROUTER_SITE_URL", "https://zhinonglianxiao.com")
            site_name = os.getenv("OPENROUTER_SITE_NAME", "智农链销")
            default_headers = {
                "HTTP-Referer": site_url,
                "X-Title": site_name,
            }
            # OpenRouter 支持的额外参数
            openrouter_transforms = os.getenv("OPENROUTER_TRANSFORMS", "")
            if openrouter_transforms:
                extra_body["transforms"] = openrouter_transforms.split(",")
        
        # Gemini模型特有的thinking配置
        elif provider_config['provider'] == 'gemini':
            extra_body = {
                "extra_body":{
                "google": {
                    "thinking_config": {
                        "thinking_budget": 800,
                        "include_thoughts": True
                    }
                }}
            }
        
        # Qwen模型特有的配置
        elif provider_config['provider'] == 'qwen':
            if llm_enable_thinking:
                extra_body = {
                    "enable_thinking": True
                }

        
        agent_llm = ChatOpenAI(
            model=model_name,
            openai_api_base=base_url,
            openai_api_key=api_key,
            max_tokens=llm_max_tokens,
            temperature=llm_temperature,
            callbacks=[token_handler],
            request_timeout=6000, # 设置为无超时
            default_headers=default_headers if default_headers else None,
            extra_body=extra_body if extra_body else None
        )
        logger.info(f"Created LLM instance for agent '{agent_name}' with model '{model_name}' via provider '{provider_config['provider']}'.")
        return agent_llm
    except Exception as e:
        logger.error(f"Failed to initialize ChatOpenAI for model {model_name}: {e}")
        raise

# Keep `llm` and `llm_with_tools` in __all__ for now to avoid breaking imports,
# but they should be considered deprecated and removed in a future refactor.
llm = None
llm_with_tools = None

def get_env_int(key, default):
    try:
        return int(os.getenv(key, default))
    except Exception:
        return default

__all__ = [
    "llm", 
    "llm_with_tools",
    "PROJECT_ROOT",
    "DEFAULT_RESOURCES_DIR",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_REFINEMENT_DIR",
    "DEFAULT_TEST_REPORT_DIR",
    "get_llm_for_agent",
    "MODEL_CONFIG",
    "AGENT_MODEL_MAPPING",
    "get_provider_config",
    "calculate_cost",
    "TokenCounterHandler"
] 