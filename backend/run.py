"""
智农链销 - 本地启动入口
解决模块导入问题的启动脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    from backend.config.settings import settings
    
    print("=" * 60)
    print("智农链销 MCP服务启动")
    print("=" * 60)
    print(f"项目根目录: {project_root}")
    print(f"访问地址: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"API文档: http://localhost:{settings.API_PORT}/docs")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

