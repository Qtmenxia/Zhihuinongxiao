"""
服务相关的Pydantic数据模型
"""
from pydantic import BaseModel, Field, field_validator, model_validator,ConfigDict
from typing import Optional, List
from datetime import datetime


class ServiceGenerationRequest(BaseModel):
    """服务生成请求"""
    requirement: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="自然语言需求描述",
        example="我需要一个能自动回复顾客询问玉露香梨保存方法、营养价值的智能客服工具"
    )
    product_category: str = Field(
        ...,
        description="产品类别",
        example="玉露香梨"
    )
    model: Optional[str] = Field(
        None,
        description="指定使用的LLM模型(默认gemini-2.5-pro)",
        example="gemini-2.5-pro"
    )
    
    @field_validator('requirement')
    @classmethod
    def requirement_must_be_detailed(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('需求描述过于简短，请提供更详细的说明')
        return v.strip()


class ServiceGenerationResponse(BaseModel):
    """服务生成响应"""
    service_id: str = Field(..., description="服务任务ID")
    status: str = Field(..., description="当前状态")
    estimated_cost: float = Field(..., description="预估成本(美元)")
    estimated_cost_cny: float = Field(..., description="预估成本(人民币)")
    estimated_time: int = Field(..., description="预估耗时(秒)")
    message: str = Field(..., description="提示信息")


class ServiceStatusResponse(BaseModel):
    """服务状态响应"""
    service_id: str
    status: str = Field(..., description="服务状态: generating/testing/ready/deployed/failed")
    progress: int = Field(0, ge=0, le=100, description="生成进度(0-100)")
    current_stage: Optional[str] = Field(None, description="当前阶段: planning/coding/testing/refining")
    message: Optional[str] = Field(None, description="状态消息")
    cost: Optional[float] = Field(None, description="实际成本(美元)")
    quality_score: Optional[float] = Field(None, description="质量评分(0-100)")
    generation_time: Optional[int] = Field(None, description="生成耗时(秒)")


class ServiceDetail(BaseModel):
    """服务详情"""
    service_id: str
    farmer_id: str
    name: str
    description: Optional[str] = None
    status: str
    model_used: Optional[str] = None
    original_requirement: str
    
    # 代码相关
    code: Optional[str] = None
    readme: Optional[str] = None
    requirements: Optional[str] = None
    file_path: Optional[str] = None
    
    # 成本与质量
    generation_cost: Optional[float] = None
    generation_time: Optional[int] = None
    quality_score: Optional[float] = None
    test_pass_rate: Optional[float] = None
    
    # 部署信息
    is_deployed: bool = False
    deployed_at: Optional[datetime] = None
    endpoints: List[str] = []
    
    # 运行统计
    total_calls: int = 0
    total_errors: int = 0
    avg_latency: Optional[float] = None
    refinement_count: int = 0
    
    # 时间戳
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    """服务列表响应"""
    items: List[ServiceDetail]
    total: int
    page: int
    page_size: int
    has_more: bool


class DeploymentRequest(BaseModel):
    """部署请求"""
    force_redeploy: bool = Field(
        False,
        description="是否强制重新部署(即使已部署)"
    )
    config: Optional[dict] = Field(
        None,
        description="部署配置(可选)"
    )


class DeploymentResponse(BaseModel):
    """部署响应"""
    service_id: str
    status: str = Field(..., description="部署状态")
    endpoints: List[str] = Field(..., description="可用的API端点")
    message: str = Field(..., description="部署消息")

class ServiceDeploymentRequest(BaseModel):
    """服务部署请求（产品信息）"""
    name: str = Field(..., description="产品名称", example="玉露香梨")
    category: str = Field(..., description="产品品类", example="水果")
    price: float = Field(..., gt=0, description="产品价格", example=5.0)
    origin: Optional[str] = Field(None, description="产地", example="山西省蒲县")
    stock: int = Field(..., ge=0, description="库存数量", example=100)
    description: Optional[str] = Field(None, description="产品描述", example="香甜多汁的梨子，非常适合夏季解渴。")
    certifications: Optional[List[str]] = Field(None, description="认证列表", example=["有机认证"])