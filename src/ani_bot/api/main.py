from fastapi import APIRouter
from ani_bot.api.routers import rss


api_router = APIRouter()
api_router.include_router(rss.router)
