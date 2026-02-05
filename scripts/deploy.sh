#!/bin/bash

# 智遇到错误立即退出

echo "=================================="
echo "   智农链销平台 - 一键部署"
echo "=================================="
echo ""

# 1. 检查环境
echo "📋 检查环境依赖..."
command -v docker >/dev/null 2>&1 || { echo "❌ 请先安装 Docker"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ 请先安装 Docker Compose"; exit 1; }
echo "✅ 环境检查通过"
echo ""

# 2. 检查.env文件
if [ ! -f .env ]; then
    echo "❌ .env文件不存在"
    echo "请从 backend/.env.example 复制并配置："
    echo "  cp backend/.env.example .env"
    echo "  nano .env  # 编辑配置，至少设置GEMINI_API_KEY和数据库密码"
    exit 1
fi
echo "✅ .env文件已找到"
echo ""

# 3. 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 4. 检查必需的API密钥
if [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$QWEN_API_KEY" ]; then
    echo "❌ 至少需要配置一个LLM API密钥(GEMINI_API_KEY/OPENAI_API_KEY/QWEN_API_KEY)"
    exit 1
fi
echo "✅ LLM API密钥已配置"
echo ""

# 5. 拉取最新代码(可选)
# echo "🔄 拉取最新代码..."
# git pull origin main

# 6. 构建镜像
echo "🏗️  构建Docker镜像..."
cd infrastructure/docker
docker-compose build --no-cache
echo "✅ 镜像构建完成"
echo ""

# 7. 启动服务
echo "🎬 启动服务..."
docker-compose up -d
echo "✅ 服务启动完成"
echo ""

# 8. 等待服务就绪
echo "⏳ 等待服务启动（约30秒）..."
sleep 30

# 9. 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 10. 初始化数据库
echo ""
echo "📊 初始化数据库..."
docker-compose exec -T api python -m backend.scripts.init_db
echo "✅ 数据库初始化完成"
echo ""

# 11. 健成"
echo ""

# 11. 健康检查
echo "🏥 执行健康检查..."
if curl -f http://localhost:8000/health >服务健康"
else
    echo "❌ API服务未就绪，请检查日志"
    docker-compose logs api
    exit 1
fi
echo ""

# 12. 完成
echo "=================================="
echo "✅ 部署完成！"
echo "=================================="
echo ""
echo "📌 访问地址："
echo "   - API文档: http://localhost:8000/docs"
echo "   - 农户后台: http://localhost/admin"
echo "   - 健康检查: http://localhost:8000/health"
echo ""
echo "📝 常用命令："
echo "   - 查看日志: cd infrastructure/docker && docker-compose logs -f"
echo "   - 停止服务: cd infrastructure/docker && docker-compose down"
echo "   - 重启服务: cd infrastructure/docker && docker-compose restart"
echo "   - 进入容器: cd infrastructure/docker && docker-compose exec api bash"
echo ""
echo "🔐 Demo账号："
echo "   - 手机号: 13800138000"
echo "   - 密码: demo123456"
echo ""
echo "💡 提示："
echo "   - 首次启动后请访问 http://localhost:8000/docs 查看API文档"
echo "   - MCPybarra工作流日志位于 workspace的服务位于 workspace/pipeline-output-servers/"
echo ""
