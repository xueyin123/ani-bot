from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

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


@dataclass
class RSSFeed:
    """RSS订阅源数据模型"""
    id: Optional[int] = None
    name: str = ""  # 订源名称
    url: str = ""  # RSS源URL
    site_url: str = ""  # 对应网站URL
    category: str = ""  # 分类，如动漫、电影等
    enabled: bool = True  # 是否启用
    last_checked: Optional[datetime] = None  # 最后检查时间
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间



@dataclass
class RSSItem:
    """RSS条目数据模型"""
    id: Optional[int] = None
    rss_feed_id: int = 0  # 所属RSS源ID
    title: str = ""  # 条目标题
    link: str = ""  # 条目链接
    description: str = ""  # 描述
    publish_date: Optional[datetime] = None  # 发布时间
    torrent_url: str = ""  # 种子链接
    magnet_link: str = ""  # 磁力链接
    enclosure_url: str = ""  # 附件链接
    guid: str = ""  # 全局唯一标识符
    read_status: str = "unread"  # 阅读状态: unread, read, downloaded
    anime_id: Optional[int] = None  # 关联的动漫ID
    episode_id: Optional[int] = None  # 关联的剧集ID
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间

class RSSItemPublic(SQLModel):
    data: list[RSSItem]
    count: int


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