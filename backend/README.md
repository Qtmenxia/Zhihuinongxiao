# 智农链销后端系统

基于MCPybarra多智能体框架的AI农产品电商赋能平台后端服务。

## 技术栈

- **Web框架**: FastAPI 0.109
- **数据库**: PostgreSQL + SQLAlchemy (异步ORM)
- **缓存**: Redis
- **AI框架**: MCPybarra (基于LangGraph)
- **LLM**: Gemini 2.5 Pro / Qwen / GPT-4o
- **部署**: Docker + Nginx

## 核心功能

### 1. AI服务生成
- 自然语言转MCP服务，成本降低99.9%
- 基于MCPybarra两阶段生成（Planning + Coding）
- 三阶段测试（Generate Test Plan + Execute + Final Report）
- 三阶段优化（Refine with Tools）

### 2. 农产品管理
- 蒲县特色产品管理（玉露香梨、维纳斯黄金苹果）
- 库存管理与预警
- 溯源信息管理

### 3. 订单处理
- 全生命周期订单管理
- 微信/支付宝支付集成
- 物流跟踪

### 4. 数据统计
- 实时统计与可视化
- 成本监控与账单生成
- 质量监控与自动优化

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (可选)

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd zhinonglianxiao/backend

2. **配置环境变量**
```bash
cp .env.example .env
nano .env  # 编辑配置，至少设置GEMINI_API_KEY和数据库密码
```

3. **安装依赖**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
# 创建数据库
createdb zhinong_db

# 运行迁移
alembic upgrade head

# 导入初始数据
python -m backend.scripts.init_db

```

5. **启动服务**
```bash
# 启动FastAPI服务器
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

6. **访问API文档**
http://localhost:8000/docs

7. **Docker部署**
```bash
cd ../infrastructure/docker
docker-compose up -d
```

