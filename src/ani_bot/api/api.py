from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
import os
import sqlite3

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ani_bot.models import AnimeDatabase, Anime
from ani_bot.config.settings import config
from ani_bot.utils.logger import get_logger

# Pydantic模型定义
class AnimeRequest(BaseModel):
    name: str
    original_name: Optional[str] = ""
    season: Optional[int] = 1
    episode: Optional[int] = 0
    total_episodes: Optional[int] = 0
    air_date: Optional[str] = None
    status: Optional[str] = "ongoing"
    description: Optional[str] = ""
    cover_image_url: Optional[str] = ""
    source_url: Optional[str] = ""
    download_status: Optional[str] = "pending"
    download_path: Optional[str] = ""


class AnimeUpdateRequest(BaseModel):
    name: Optional[str] = None
    original_name: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    total_episodes: Optional[int] = None
    air_date: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    source_url: Optional[str] = None
    download_status: Optional[str] = None
    download_path: Optional[str] = None


class AnimeResponse(AnimeRequest):
    id: int
    last_updated: Optional[str] = None
    next_air_date: Optional[str] = None


class EpisodeRequest(BaseModel):
    anime_id: int
    episode_number: int
    title: Optional[str] = ""
    air_date: Optional[str] = None
    download_url: Optional[str] = ""
    torrent_hash: Optional[str] = ""
    download_status: Optional[str] = "pending"
    download_path: Optional[str] = ""
    size: Optional[int] = 0
    quality: Optional[str] = ""


class EpisodeResponse(EpisodeRequest):
    id: int


app = FastAPI(title="Ani-Bot API", description="自动追番工具API接口", version="1.0.0")

# 获取数据库实例
def get_db():
    db_path = config.get('database.path', './data/anime.db')
    return AnimeDatabase(db_path)


# 获取日志记录器
logger = get_logger('AniBotAPI', config)


@app.get("/")
async def root():
    return {"message": "Welcome to Ani-Bot API"}


@app.get("/anime", response_model=List[AnimeResponse])
async def get_all_anime():
    """获取所有动漫列表"""
    db = get_db()
    anime_list = []
    
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM anime ORDER BY last_updated DESC')
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        anime = Anime(
            id=row[0], name=row[1], original_name=row[2], 
            season=row[3], episode=row[4], total_episodes=row[5],
            air_date=datetime.fromisoformat(row[6]) if row[6] else None,
            status=row[7],
            last_updated=datetime.fromisoformat(row[8]) if row[8] else None,
            next_air_date=datetime.fromisoformat(row[9]) if row[9] else None,
            description=row[10], cover_image_url=row[11], 
            source_url=row[12], download_status=row[13], 
            download_path=row[14]
        )
        anime_list.append(AnimeResponse(
            id=anime.id,
            name=anime.name,
            original_name=anime.original_name,
            season=anime.season,
            episode=anime.episode,
            total_episodes=anime.total_episodes,
            air_date=anime.air_date.isoformat() if anime.air_date else None,
            status=anime.status,
            last_updated=anime.last_updated.isoformat() if anime.last_updated else None,
            next_air_date=anime.next_air_date.isoformat() if anime.next_air_date else None,
            description=anime.description,
            cover_image_url=anime.cover_image_url,
            source_url=anime.source_url,
            download_status=anime.download_status,
            download_path=anime.download_path
        ))
    
    return anime_list


# 搜索动漫路由必须在 /anime/{anime_id} 之前定义，以避免路径冲突
@app.get("/anime/search", response_model=List[AnimeResponse])
async def search_anime(keyword: str):
    """搜索动漫"""
    db = get_db()
    anime_list = []
    
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM anime WHERE name LIKE ? OR original_name LIKE ?', (f'%{keyword}%', f'%{keyword}%'))
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        anime = Anime(
            id=row[0], name=row[1], original_name=row[2], 
            season=row[3], episode=row[4], total_episodes=row[5],
            air_date=datetime.fromisoformat(row[6]) if row[6] else None,
            status=row[7],
            last_updated=datetime.fromisoformat(row[8]) if row[8] else None,
            next_air_date=datetime.fromisoformat(row[9]) if row[9] else None,
            description=row[10], cover_image_url=row[11], 
            source_url=row[12], download_status=row[13], 
            download_path=row[14]
        )
        anime_list.append(AnimeResponse(
            id=anime.id,
            name=anime.name,
            original_name=anime.original_name,
            season=anime.season,
            episode=anime.episode,
            total_episodes=anime.total_episodes,
            air_date=anime.air_date.isoformat() if anime.air_date else None,
            status=anime.status,
            last_updated=anime.last_updated.isoformat() if anime.last_updated else None,
            next_air_date=anime.next_air_date.isoformat() if anime.next_air_date else None,
            description=anime.description,
            cover_image_url=anime.cover_image_url,
            source_url=anime.source_url,
            download_status=anime.download_status,
            download_path=anime.download_path
        ))
    
    return anime_list


@app.get("/anime/{anime_id}", response_model=AnimeResponse)
async def get_anime(anime_id: int):
    """根据ID获取特定动漫"""
    db = get_db()
    anime = db.get_anime_by_id(anime_id)
    
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    return AnimeResponse(
        id=anime.id,
        name=anime.name,
        original_name=anime.original_name,
        season=anime.season,
        episode=anime.episode,
        total_episodes=anime.total_episodes,
        air_date=anime.air_date.isoformat() if anime.air_date else None,
        status=anime.status,
        last_updated=anime.last_updated.isoformat() if anime.last_updated else None,
        next_air_date=anime.next_air_date.isoformat() if anime.next_air_date else None,
        description=anime.description,
        cover_image_url=anime.cover_image_url,
        source_url=anime.source_url,
        download_status=anime.download_status,
        download_path=anime.download_path
    )


@app.post("/anime", response_model=AnimeResponse)
async def create_anime(anime: AnimeRequest):
    """添加新动漫到跟踪列表"""
    db = get_db()
    
    # 检查动漫是否已存在
    existing_anime = db.get_anime_by_name(anime.name)
    if existing_anime:
        raise HTTPException(status_code=400, detail=f"Anime {anime.name} already exists with ID {existing_anime.id}")
    
    # 创建新的动漫对象
    new_anime = Anime(
        name=anime.name,
        original_name=anime.original_name,
        season=anime.season,
        episode=anime.episode,
        total_episodes=anime.total_episodes,
        air_date=datetime.fromisoformat(anime.air_date) if anime.air_date else None,
        status=anime.status,
        description=anime.description,
        cover_image_url=anime.cover_image_url,
        source_url=anime.source_url,
        download_status=anime.download_status,
        download_path=anime.download_path
    )
    
    # 添加到数据库
    anime_id = db.add_anime(new_anime)
    created_anime = db.get_anime_by_id(anime_id)
    
    logger.info(f"已添加动漫: {created_anime.name}, ID: {created_anime.id}")
    
    return AnimeResponse(
        id=created_anime.id,
        name=created_anime.name,
        original_name=created_anime.original_name,
        season=created_anime.season,
        episode=created_anime.episode,
        total_episodes=created_anime.total_episodes,
        air_date=created_anime.air_date.isoformat() if created_anime.air_date else None,
        status=created_anime.status,
        last_updated=created_anime.last_updated.isoformat() if created_anime.last_updated else None,
        next_air_date=created_anime.next_air_date.isoformat() if created_anime.next_air_date else None,
        description=created_anime.description,
        cover_image_url=created_anime.cover_image_url,
        source_url=created_anime.source_url,
        download_status=created_anime.download_status,
        download_path=created_anime.download_path
    )


@app.put("/anime/{anime_id}", response_model=AnimeResponse)
async def update_anime(anime_id: int, anime_update: AnimeUpdateRequest):
    """更新动漫信息"""
    db = get_db()
    existing_anime = db.get_anime_by_id(anime_id)
    
    if not existing_anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    # 使用提供的值更新现有动漫对象
    if anime_update.name is not None:
        existing_anime.name = anime_update.name
    if anime_update.original_name is not None:
        existing_anime.original_name = anime_update.original_name
    if anime_update.season is not None:
        existing_anime.season = anime_update.season
    if anime_update.episode is not None:
        existing_anime.episode = anime_update.episode
    if anime_update.total_episodes is not None:
        existing_anime.total_episodes = anime_update.total_episodes
    if anime_update.air_date is not None:
        existing_anime.air_date = datetime.fromisoformat(anime_update.air_date) if anime_update.air_date else None
    if anime_update.status is not None:
        existing_anime.status = anime_update.status
    if anime_update.description is not None:
        existing_anime.description = anime_update.description
    if anime_update.cover_image_url is not None:
        existing_anime.cover_image_url = anime_update.cover_image_url
    if anime_update.source_url is not None:
        existing_anime.source_url = anime_update.source_url
    if anime_update.download_status is not None:
        existing_anime.download_status = anime_update.download_status
    if anime_update.download_path is not None:
        existing_anime.download_path = anime_update.download_path
    
    # 更新数据库
    db.update_anime(existing_anime)
    updated_anime = db.get_anime_by_id(anime_id)
    
    logger.info(f"已更新动漫: {updated_anime.name}, ID: {updated_anime.id}")
    
    return AnimeResponse(
        id=updated_anime.id,
        name=updated_anime.name,
        original_name=updated_anime.original_name,
        season=updated_anime.season,
        episode=updated_anime.episode,
        total_episodes=updated_anime.total_episodes,
        air_date=updated_anime.air_date.isoformat() if updated_anime.air_date else None,
        status=updated_anime.status,
        last_updated=updated_anime.last_updated.isoformat() if updated_anime.last_updated else None,
        next_air_date=updated_anime.next_air_date.isoformat() if updated_anime.next_air_date else None,
        description=updated_anime.description,
        cover_image_url=updated_anime.cover_image_url,
        source_url=updated_anime.source_url,
        download_status=updated_anime.download_status,
        download_path=updated_anime.download_path
    )


@app.delete("/anime/{anime_id}")
async def delete_anime(anime_id: int):
    """删除动漫"""
    db = get_db()
    anime = db.get_anime_by_id(anime_id)
    
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    # 删除动漫
    db.delete_anime(anime_id)
    logger.info(f"已删除动漫: {anime.name}, ID: {anime.id}")
    
    return {"message": f"Anime {anime.name} deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)