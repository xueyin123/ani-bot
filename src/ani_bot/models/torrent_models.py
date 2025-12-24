from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import sqlite3


@dataclass
class Torrent:
    """种子数据模型"""
    id: Optional[int] = None
    title: str = ""  # 种子标题
    size: int = 0  # 文件大小，字节
    magnet_link: str = ""  # 磁力链接
    torrent_url: str = ""  # 种子文件URL
    torrent_hash: str = ""  # 种子哈希
    category: str = ""  # 分类
    quality: str = ""  # 质量，如 720p, 1080p
    source: str = ""  # 来源
    publish_date: Optional[datetime] = None  # 发布时间
    seeders: int = 0  # 做种人数
    leechers: int = 0  # 下载人数
    completed: int = 0  # 完成人数
    download_status: str = "pending"  # 下载状态: pending, downloading, completed, failed
    download_path: str = ""  # 下载路径
    anime_id: Optional[int] = None  # 关联的动漫ID
    episode_id: Optional[int] = None  # 关联的剧集ID
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间