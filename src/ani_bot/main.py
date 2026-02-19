from contextlib import asynccontextmanager
import sentry_sdk
import logging
import sys
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from ani_bot.api.main import api_router
from ani_bot.core.config import settings
from ani_bot.core.db import init_db
from ani_bot.db import crud
from ani_bot.downloader.bt_downloader import QBittorrentDownloader
from ani_bot.rss import RSSParseTask
from ani_bot.scheduler import AsyncScheduler


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

scheduler = AsyncScheduler()

rss_parse_task = RSSParseTask(
    get_rss_sources=crud.get_all_rss_feed_urls,
    downloader=QBittorrentDownloader(settings.qbittorrent_config)  # 传入配置
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # === 启动阶段 ===
    init_db()
    logger.info("数据库初始化完成")
    
    await scheduler.start()
    
    # 添加周期任务
    scheduler.add_task(rss_parse_task.run, interval=1)
    
    logger.info("应用启动完成")
    yield
    
    # === 关闭阶段 ===
    await scheduler.stop()
    logger.info("应用关闭完成")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# 创建一个启动函数，而不是直接运行
def start_server():
    import uvicorn
    uvicorn.run(
        "ani_bot.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True  # 开发模式下启用热重载
    )

if __name__ == "__main__":
    start_server()