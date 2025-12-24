from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import sqlite3


@dataclass
class Anime:
    """动漫数据模型"""
    id: Optional[int] = None
    name: str = ""
    original_name: str = ""
    season: int = 1
    episode: int = 0
    total_episodes: int = 0
    air_date: Optional[datetime] = None
    status: str = "ongoing"  # ongoing, finished, dropped
    last_updated: Optional[datetime] = None
    next_air_date: Optional[datetime] = None
    description: str = ""
    cover_image_url: str = ""
    source_url: str = ""
    download_status: str = "pending"  # pending, downloading, completed, failed
    download_path: str = ""


@dataclass
class Episode:
    """剧集数据模型"""
    id: Optional[int] = None
    anime_id: int = 0
    episode_number: int = 0
    title: str = ""
    air_date: Optional[datetime] = None
    download_url: str = ""
    torrent_hash: str = ""
    download_status: str = "pending"  # pending, downloaded, failed
    download_path: str = ""
    size: int = 0  # 文件大小，字节
    quality: str = ""  # 如 720p, 1080p