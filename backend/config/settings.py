"""
环境配置管理
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "智农链销"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "zhinong_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    
    @property
    def DATABASE_URL(self) -> str:
        """生成数据库连接URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        """生成Redis连接URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # LLM配置(继承MCPybarra的配置)
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    QWEN_API_KEY: Optional[str] = None
    
    # OpenRouter配置 (支持多种模型的统一API)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: str = "https://zhinonglianxiao.com"
    OPENROUTER_SITE_NAME: str = "智农链销"
    
    # 默认使用的模型 (可以使用OpenRouter格式: openrouter/provider/model)
    DEFAULT_SWE_MODEL: str = "openrouter/anthropic/claude-3.5-sonnet"
    
    # Agent 模型配置（用于 MCPybarra 工作流）
    SWE_AGENT_MODEL: Optional[str] = None
    SERVER_TEST_AGENT_MODEL: Optional[str] = None
    CODE_REFINER_AGENT_MODEL: Optional[str] = None
    DEFAULT_AGENT_MODEL: Optional[str] = None
    
    # LLM 通用参数
    LLM_MAX_TOKENS: int = 64000
    LLM_TEMPERATURE: float = 0.6
    LLM_ENABLE_THINKING: bool = False
    
    # MCPybarra工作流参数（与config.py保持一致）
    MAX_REFINE_LOOPS: int = 2
    MAX_PLANNING_TURNS: int = 4
    MAX_CODEGEN_TURNS: int = 5
    MAX_PLANNING_TOOL_CALLS: int = 2
    MAX_CODEGEN_TOOL_CALLS: int = 3
    
    #搜索： Tavily 配置 [必填](MCPyabarra需要)
    TAVILY_API_KEY: str | None = None 
    
    # 文件存储配置
    WORKSPACE_DIR: str = "workspace"
    UPLOAD_DIR: str = "uploads"
    GENERATED_SERVICES_DIR: str = "generated_services"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production-PLEASE"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    ALGORITHM: str = "HS256"

    # Langchain 配置
    LANGCHAIN_TRACING_V2: bool = False
    
    # CORS配置
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS_ORIGINS，支持逗号分隔的字符串"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # 支付配置
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    WECHAT_MCH_ID: Optional[str] = None
    WECHAT_API_KEY: Optional[str] = None
    
    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    ALIPAY_PUBLIC_KEY: Optional[str] = None
    
    # 短信配置(用于订单通知)
    SMS_PROVIDER: str = "aliyun"
    SMS_ACCESS_KEY: Optional[str] = None
    SMS_ACCESS_SECRET: Optional[str] = None
    SMS_SIGN_NAME: str = "智农链销"
    
    # 对象存储配置(用于图片/视频)
    OSS_PROVIDER: str = "aliyun"
    OSS_ACCESS_KEY: Optional[str] = None
    OSS_ACCESS_SECRET: Optional[str] = None
    OSS_BUCKET: str = "zhinong-assets"
    OSS_ENDPOINT: str = "oss-cn-beijing.aliyuncs.com"
    
    # 监控配置
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 性能配置
    ENABLE_ASYNC_DB: bool = True
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # 功能开关
    ENABLE_AUTO_REFINE: bool = True
    ENABLE_COST_ALERT: bool = True
    ENABLE_STOCK_ALERT: bool = True
    
    class Config:
        """Pydantic配置"""
        # 使用绝对路径指向 backend/.env 文件
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True
    


# 创建全局配置实例
settings = Settings()


# 创建必要的目录
def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        settings.WORKSPACE_DIR,
        f"{settings.WORKSPACE_DIR}/resources",
        f"{settings.WORKSPACE_DIR}/pipeline-output-servers",
        f"{settings.WORKSPACE_DIR}/refinement",
        f"{settings.WORKSPACE_DIR}/server-test-report",
        settings.UPLOAD_DIR,
        settings.GENERATED_SERVICES_DIR,
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# 启动时调用
ensure_directories()
