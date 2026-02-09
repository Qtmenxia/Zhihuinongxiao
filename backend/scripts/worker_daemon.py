"""
Worker守护进程
处理异步任务：服务生成、质量监控、自动优化等
"""
import os

# ✅ 1. 代理设置 (保持你之前的正确配置)
PROXY_PORT = "7897"  # 如果是v2rayN请改为10809，Clash通常是7890
os.environ["HTTP_PROXY"] = f"http://127.0.0.1:{PROXY_PORT}"
os.environ["HTTPS_PROXY"] = f"http://127.0.0.1:{PROXY_PORT}"

import asyncio
import signal
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.connection import AsyncSessionLocal
from backend.models.mcp_service import MCPService, ServiceStatus
from backend.services.quality_monitor import QualityMonitor
from backend.config.settings import settings
# ✅ 2. 新增：导入核心处理函数
from backend.services.worker_service import process_pending_services
from sqlalchemy import select, and_

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("worker")

# 全局运行标志
running = True


def signal_handler(signum, frame):
    """信号处理器"""
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


async def check_stuck_tasks():
    """检查并处理卡住的任务"""
    # logger.debug("Checking for stuck tasks...") # 减少日志噪音
    
    async with AsyncSessionLocal() as session:
        # 查找超过30分钟还在生成中的任务
        timeout = datetime.utcnow() - timedelta(minutes=30)
        
        result = await session.execute(
            select(MCPService).where(
                and_(
                    MCPService.status == ServiceStatus.GENERATING,
                    MCPService.created_at < timeout
                )
            )
        )
        stuck_services = result.scalars().all()
        
        for service in stuck_services:
            logger.warning(f"Service {service.id} appears stuck, marking as failed")
            service.status = ServiceStatus.FAILED
            service.updated_at = datetime.utcnow()
        
        if stuck_services:
            await session.commit()
            logger.info(f"Marked {len(stuck_services)} stuck services as failed")


async def run_quality_checks():
    """运行质量检查"""
    # logger.debug("Running quality checks...") # 减少日志噪音
    
    monitor = QualityMonitor()
    
    async with AsyncSessionLocal() as session:
        # 查找已部署的服务
        result = await session.execute(
            select(MCPService).where(
                MCPService.status == ServiceStatus.DEPLOYED
            )
        )
        deployed_services = result.scalars().all()
        
        for service in deployed_services:
            try:
                # 检查服务质量
                quality_ok = await monitor.check_service_quality(service.id)
                
                if not quality_ok and settings.ENABLE_AUTO_REFINE:
                    logger.info(f"Service {service.id} needs optimization")
                    
            except Exception as e:
                logger.error(f"Quality check failed for {service.id}: {e}")


async def cleanup_old_logs():
    """清理旧日志"""
    logger.debug("Cleaning up old logs...")
    
    log_dir = Path("logs")
    if not log_dir.exists():
        return
    
    cutoff = datetime.utcnow() - timedelta(days=7)
    
    for log_file in log_dir.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                log_file.unlink()
                logger.info(f"Deleted old log file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to delete {log_file}: {e}")


async def reset_daily_counters():
    """重置每日计数器"""
    logger.debug("Resetting daily counters...")
    
    async with AsyncSessionLocal() as session:
        from backend.models.farmer import Farmer
        result = await session.execute(select(Farmer))
        farmers = result.scalars().all()
        for farmer in farmers:
            farmer.api_calls_today = 0
        await session.commit()
        logger.info(f"Reset daily counters for {len(farmers)} farmers")


async def worker_loop():
    """主工作循环"""
    logger.info("Worker daemon started - Ready to process tasks")
    
    last_daily_reset = datetime.utcnow().date()
    
    while running:
        try:
            current_date = datetime.utcnow().date()
            
            # 每日任务
            if current_date > last_daily_reset:
                await reset_daily_counters()
                await cleanup_old_logs()
                last_daily_reset = current_date
            
            # ✅ 3. 核心修复：处理待办任务
            # 这一步是让 Worker 干活的关键
            await process_pending_services()
            
            # 定期维护
            await check_stuck_tasks()
            
            # 质量检查
            if settings.ENABLE_AUTO_REFINE:
                await run_quality_checks()
            
            # ✅ 4. 优化：缩短等待时间
            # 从60秒改为5秒，让它响应更快，不要让用户干等
            for _ in range(5): 
                if not running:
                    break
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Worker loop error: {e}", exc_info=True)
            await asyncio.sleep(10)
    
    logger.info("Worker daemon stopped")


def main():
    """主入口"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 50)
    logger.info("智农链销 - Worker守护进程 (Fixed Version)")
    logger.info("=" * 50)
    
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
    except Exception as e:
        logger.error(f"Worker fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
