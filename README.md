# 智农链销 - AI农产品电商赋能平台

<div align="center">

![智农链销Logo](docs/images/logo.png)

**基于MCPybarra多智能体框架的智能农产品电商解决方案**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![MCPybarra](https://img.shields.io/badge/MCPybarra-v1.0-orange.svg)](https://github.com/mcpybarra/mcpybarra)

[功能特性](#-核心特性) • [快速开始](#-快速开始) • [技术架构](#️-技术架构) • [文档](#-文档) • [路线图](#️-路线图)

</div>

---

## 📖 项目简介

**智农链销**是一个创新的AI驱动农产品电商赋能平台，专为中小农户和合作社设计。通过集成**MCPybarra多智能体框架**，实现从自然语言需求到MCP服务的全自动生成，将传统软件开发成本降低**99.9%**，从数万元降至仅需数美元。

### 🎯 解决的核心问题

| 传统方案 | 智农链销方案 |
|---------|------------|
| 开发成本：¥30,000-¥100,000 | **生成成本：$0.15-$0.50** |
| 开发周期：2-4周 | **生成时间：5-10分钟** |
| 需要专业开发团队 | **自然语言描述即可** |
| 维护成本高，迭代慢 | **自动优化，秒级迭代** |

### 🌾 真实应用场景：蒲县玉露香梨

**背景**：山西蒲县被子垣有机果园
- **产品**：玉露香梨、维纳斯黄金苹果
- **痛点**：传统电商工具年费数万元，技术门槛高，无法负担
- **解决方案**：
  1. 农户用自然语言描述需求："我需要一个订单查询工具，客户输入手机号就能看到订单状态"
  2. AI自动生成完整的MCP服务代码
  3. 一键部署，立即可用
  4. **成本**：$0.25（vs 传统方案¥5,000）

---

## ✨ 核心特性

### 1. 🤖 AI驱动的服务生成

<details>
<summary><b>点击查看详细流程</b></summary>

用户输入自然语言需求
↓
┌─────────────────────────────┐
│ Phase 1: Planning (规划) │
│ - LLM分析需求 │
│ - 设计MCP工具接口 │
│ - 使用Tavily搜索相关文档 │
└─────────────────────────────┘
↓
┌─────────────────────────────┐
│ Phase 2: Coding (编码) │
│ - 生成完整Python代码 │
│ - 使用Context7查询MCP文档 │
│ - 自动代码审查优化 │
└─────────────────────────────┘
↓
┌─────────────────────────────┐
│ Phase 3: Testing (测试) │
│ - 生成测试计划 │
│ - 执行自动化测试 │
│ - 生成质量报告 │
└─────────────────────────────┘
↓
┌─────────────────────────────┐
│ Phase 4: Refining (优化) │
│ - 根据测试反馈修复bug │
│ - 性能优化 │
│ - 生成README和requirements │
└─────────────────────────────┘
↓
MCP服务就绪 ✅

```php-template

**关键优势**：
- ✅ **零代码**：用白话描述需求，AI自动生成
- ✅ **高质量**：四阶段工作流确保代码质量
- ✅ **低成本**：单次生成$0.15-$0.50（vs 传统¥5,000+）
- ✅ **快速迭代**：5-10分钟生成，秒级优化

</details>

### 2. 🍐 专业的农产品管理

- **标准化产品库**：预置蒲县特色产品配置
  - 玉露香梨（9枚装、7枚装、6枚装）
  - 维纳斯黄金苹果（12枚装、10枚装、5枚装）
  - 深加工产品（果干、果汁礼盒）
- **智能库存管理**：
  - 实时库存跟踪
  - 低库存自动预警
  - 库存变动日志
- **全程溯源**：
  - 果园信息（位置、认证、面积）
  - 种植过程（施肥、授粉、防控、采摘）
  - 质检报告（农残、重金属、糖度检测）

### 3. 📦 智能订单处理

- **灵活定价策略**：
  - 满额包邮（满158元包邮）
  - 批量折扣（5件9.5折，10件9折，20件85折）
  - 新人优惠券
  - 礼盒组合优惠
- **支付集成**：微信支付、支付宝（配置即用）
- **物流跟踪**：快递单号自动同步，实时更新状态
- **订单状态管理**：待付款→已支付→已发货→已完成/已取消

### 4. 📊 数据驱动的决策支持

- **实时仪表盘**：
  - 今日销售额、订单量
  - 服务配额剩余
  - API调用统计
  - 成本消耗追踪
- **趋势分析**：
  - 最近30天销售趋势
  - 产品销量排行
  - 客户地域分布
- **成本监控**：
  - LLM调用成本明细
  - 订阅费用账单
  - 交易抽成统计
  - 月度成本预测

### 5. 🔄 智能优化与运维

- **自动质量监控**：
  - 实时监测服务错误率、延迟
  - 低于阈值自动触发MCPybarra重新生成
  - 保留优化历史，支持版本回滚
- **健康检查**：
  - 服务可用性监控
  - 异常告警（邮件/短信）
  - 性能瓶颈分析

---

## 🏗️ 技术架构

### 技术栈

<table>
<tr>
<td><b>层级</b></td>
<td><b>技术选型</b></td>
<td><b>说明</b></td>
</tr>
<tr>
<td>前端</td>
<td>Vue 3 + Element Plus</td>
<td>农户管理后台</td>
</tr>
<tr>
<td>API层</td>
<td>FastAPI + WebSocket</td>
<td>RESTful API + 实时推送</td>
</tr>
<tr>
<td>业务逻辑</td>
<td>ServiceManager<br/>DeploymentService<br/>QualityMonitor</td>
<td>服务管理、部署、质量监控</td>
</tr>
<tr>
<td>AI框架</td>
<td>MCPybarra (LangGraph)</td>
<td>多智能体工作流编排</td>
</tr>
<tr>
<td>LLM</td>
<td>Gemini 2.5 Pro / Qwen / GPT-4o</td>
<td>代码生成与优化</td>
</tr>
<tr>
<td>数据库</td>
<td>PostgreSQL + Redis</td>
<td>关系型数据 + 缓存</td>
</tr>
<tr>
<td>部署</td>
<td>Docker + Nginx</td>
<td>容器化 + 反向代理</td>
</tr>
</table>

### 系统架构图

┌─────────────────────────────────────────────────┐
│ 前端层 (Vue 3) │
│ 农户管理后台 + 实时进度推送 (WebSocket) │
└─────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────┐
│ API层 (FastAPI) │
│ RESTful API + 认证鉴权 + 中间件 │
└─────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────┐
│ 业务逻辑层 (Services) │
│ ServiceManager │ DeploymentService │
│ CostCalculator │ QualityMonitor │
└─────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────┐
│ MCPybarra多智能体框架 (LangGraph) │
│ ┌───────────┐ ┌──────────┐ ┌──────────┐ │
│ │ Planning │→│ Coding │→│ Testing │ │
│ │ (规划) │ │ (编码) │ │ (测试) │ │
│ └───────────┘ └──────────┘ └──────────┘ │
│ ↓ │
│ ┌──────────┐ │
│ │ Refining │ (优化) │
│ └──────────┘ │
│ │
│ 工具集: Tavily搜索 | Context7文档 | SaveFile │
└─────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────┐
│ 数据层 (PostgreSQL + Redis) │
│ 业务数据持久化 + 缓存 + 会话管理 │
└─────────────────────────────────────────────────┘


### MCPybarra工作流详解

```mermaid
graph TD
    A[用户输入需求] --> B[input_loader节点]
    B --> C[swe_generator: Planning阶段]
    C --> D{Planning完成?}
    D -->|否| C
    D -->|是| E[swe_generator: Coding阶段]
    E --> F[代码审查]
    F --> G[human_confirmation节点]
    G --> H[server_tester: 生成测试计划]
    H --> I[server_tester: 执行测试]
    I --> J[server_tester: 生成测试报告]
    J --> K{质量达标?}
    K -->|是| L[完成]
    K -->|否| M[code_refiner: 优化]
    M --> N{达到最大优化次数?}
    N -->|否| H
    N -->|是| L
    L --> O[statistics_logger: 生成统计]
    O --> P[服务就绪]

🚀 快速开始
前置要求

Docker 20.10+ & Docker Compose 2.0+

Python 3.11+ (本地开发)

Node.js 18+ (前端开发，可选)

至少一个LLM API密钥：

Gemini API Key
 (推荐，免费额度大)

OpenAI API Key
 (备选)

Qwen API Key
 (国内，经济实惠)

方式一：Docker一键部署（⭐ 推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-org/zhinonglianxiao.git
cd zhinonglianxiao

# 2. 配置环境变量
cp backend/.env.example .env
nano .env  # 编辑配置，必须设置：
           # - GEMINI_API_KEY (或其他LLM的API密钥)
           # - POSTGRES_PASSWORD (数据库密码)
           # - SECRET_KEY (JWT密钥，建议32位随机字符串)

# 3. 一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 4. 访问服务
# - API文档: http://localhost:8000/docs
# - 农户后台: http://localhost/admin (前端需单独构建)
# - 健康检查: http://localhost:8000/health

# 5. 使用Demo账号登录
# 手机号: 13800138000
# 密码: demo123456
```

方式二：本地开发
<details> <summary><b>展开查看详细步骤</b></summary>
```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 5. 启动数据库（使用Docker）
docker run -d \
  --name zhinong-postgres \
  -e POSTGRES_DB=zhinong_db \
  -e POSTGRES_PASSWORD=postgres123 \
  -p 5432:5432 \
  postgres:15-alpine

docker run -d \
  --name zhinong-redis \
  -p 6379:6379 \
  redis:7-alpine

# 6. 初始化数据库
alembic upgrade head
python -m backend.scripts.init_db

# 7. 启动API服务
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# 8. （可选）启动Worker进程（另一个终端）
python -m backend.scripts.worker_daemon
前端启动（可选）
# 1. 进入前端目录
cd frontend/farmer-admin

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 访问 http://localhost:3000
</details>
快速测试
```bash
# 运行API测试脚本
chmod +x scripts/test_api.sh
./scripts/test_api.sh

# 或使用curl测试健康检查
curl http://localhost:8000/health
```
项目结构
```bash
zhinonglianxiao/
├── backend/                           # 后端服务
│   ├── api/                          # FastAPI应用
│   │   ├── main.py                  # 应用入口
│   │   ├── dependencies.py          # 依赖注入
│   │   ├── routers/                 # API路由
│   │   │   ├── service_generation.py   # 服务生成
│   │   │   ├── farmer_management.py    # 农户管理
│   │   │   ├── product_management.py   # 产品管理
│   │   │   ├── order_management.py     # 订单管理
│   │   │   └── statistics.py           # 统计数据
│   │   ├── schemas/                 # Pydantic模型
│   │   └── middleware/              # 中间件
│   ├── models/                       # SQLAlchemy模型
│   │   ├── farmer.py                # 农户模型
│   │   ├── product.py               # 产品模型
│   │   ├── order.py                 # 订单模型
│   │   ├── mcp_service.py           # MCP服务模型
│   │   └── service_log.py           # 服务日志模型
│   ├── services/                     # 业务逻辑
│   │   ├── service_manager.py       # 服务管理器
│   │   ├── deployment_service.py    # 部署服务
│   │   ├── cost_calculator.py       # 成本计算
│   │   └── quality_monitor.py       # 质量监控
│   ├── mcpybarra_core/              # MCPybarra框架
│   │   └── framework/mcp_swe_flow/
│   │       ├── graph.py             # LangGraph工作流
│   │       ├── state.py             # 状态定义
│   │       ├── config.py            # LLM配置
│   │       ├── nodes/               # 工作流节点
│   │       │   ├── input_loader.py      # 输入加载
│   │       │   ├── swe_generator.py     # 代码生成
│   │       │   ├── server_tester.py     # 测试
│   │       │   ├── code_refiner.py      # 优化
│   │       │   └── statistics_logger.py # 统计
│   │       ├── prompts/             # 提示词模板
│   │       ├── adapters/            # MCP适配器
│   │       └── tools/               # 工具集
│   ├── scripts/                      # 脚本工具
│   │   ├── init_db.py               # 数据库初始化
│   │   └── worker_daemon.py         # Worker守护进程
│   └── tests/                        # 测试代码
│
├── frontend/                          # 前端应用
│   └── farmer-admin/                 # 农户管理后台
│       ├── src/
│       │   ├── views/               # 页面组件
│       │   ├── components/          # 公共组件
│       │   ├── router/              # 路由配置
│       │   ├── store/               # Vuex状态
│       │   └── api/                 # API封装
│       └── public/
│
├── infrastructure/                    # 基础设施
│   ├── docker/
│   │   ├── docker-compose.yml       # Docker编排
│   │   ├── Dockerfile.api           # API镜像
│   │   └── Dockerfile.worker        # Worker镜像
│   └── nginx/
│       └── nginx.conf               # Nginx配置
│
├── scripts/                           # 项目脚本
│   ├── deploy.sh                    # 一键部署
│   └── test_api.sh                  # API测试
│
├── docs/                              # 文档
│   ├── api/                         # API文档
│   ├── architecture/                # 架构设计
│   └── user-guide/                  # 用户指南
│
└── workspace/                         # MCPybarra工作空间
    ├── pipeline-output-servers/      # 生成的服务
    ├── refinement/                   # 优化过程
    └── server-test-report/           # 测试报告

