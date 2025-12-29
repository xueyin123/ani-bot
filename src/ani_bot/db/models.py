from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from pydantic import BaseModel

class Anime(SQLModel, table=True):
    """动漫数据模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="")
    original_name: str = Field(default="")
    season: int = Field(default=1)
    episode: int = Field(default=0)
    total_episodes: int = Field(default=0)
    air_date: Optional[datetime] = Field(default=None)
    status: str = Field(default="ongoing")  # ongoing, finished, dropped
    last_updated: Optional[datetime] = Field(default=None)
    next_air_date: Optional[datetime] = Field(default=None)
    description: str = Field(default="")
    cover_image_url: str = Field(default="")
    source_url: str = Field(default="")
    download_status: str = Field(default="pending")  # pending, downloading, completed, failed
    download_path: str = Field(default="")


class Episode(SQLModel, table=True):
    """剧集数据模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    anime_id: int = Field(default=0)
    episode_number: int = Field(default=0)
    title: str = Field(default="")
    air_date: Optional[datetime] = Field(default=None)
    download_url: str = Field(default="")
    torrent_hash: str = Field(default="")
    download_status: str = Field(default="pending")  # pending, downloaded, failed
    download_path: str = Field(default="")
    size: int = Field(default=0)  # 文件大小，字节
    quality: str = Field(default="")  # 如 720p, 1080p


class RSSFeed(SQLModel, table=True):
    """RSS订阅源数据模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="")  # 订源名称
    url: str = Field(default="")  # RSS源URL
    site_url: str = Field(default="")  # 对应网站URL
    category: str = Field(default="")  # 分类，如动漫、电影等
    enabled: bool = Field(default=True)  # 是否启用
    last_checked: Optional[datetime] = Field(default=None)  # 最后检查时间
    created_at: Optional[datetime] = Field(default=None)  # 创建时间
    updated_at: Optional[datetime] = Field(default=None)  # 更新时间



class RSSItem(SQLModel, table=True):
    """RSS条目数据模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    rss_feed_id: int = Field(default=0)  # 所属RSS源ID
    title: str = Field(default="")  # 条目标题
    link: str = Field(default="")  # 条目链接
    description: str = Field(default="")  # 描述
    publish_date: Optional[datetime] = Field(default=None)  # 发布时间
    torrent_url: str = Field(default="")  # 种子链接
    magnet_link: str = Field(default="")  # 磁力链接
    enclosure_url: str = Field(default="")  # 附件链接
    guid: str = Field(default="")  # 全局唯一标识符
    read_status: str = Field(default="unread")  # 阅读状态: unread, read, downloaded
    anime_id: Optional[int] = Field(default=None)  # 关联的动漫ID
    episode_id: Optional[int] = Field(default=None)  # 关联的剧集ID
    created_at: Optional[datetime] = Field(default=None)  # 创建时间
    updated_at: Optional[datetime] = Field(default=None)  # 更新时间

class RSSItemCreate(BaseModel):
    title: str
    link: str
    description: str = ""
    publish_date: Optional[datetime] = None
    torrent_url: str = ""
    magnet_link: str = ""
    enclosure_url: str = ""
    guid: str
    read_status: str = "unread"
    anime_id: Optional[int] = None
    episode_id: Optional[int] = None

class RSSItemPublic(SQLModel):
    data: list[RSSItem]
    count: int


class Torrent(SQLModel, table=True):
    """种子数据模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(default="")  # 种子标题
    size: int = Field(default=0)  # 文件大小，字节
    magnet_link: str = Field(default="")  # 磁力链接
    torrent_url: str = Field(default="")  # 种子文件URL
    torrent_hash: str = Field(default="")  # 种子哈希
    category: str = Field(default="")  # 分类
    quality: str = Field(default="")  # 质量，如 720p, 1080p
    source: str = Field(default="")  # 来源
    publish_date: Optional[datetime] = Field(default=None)  # 发布时间
    seeders: int = Field(default=0)  # 做种人数
    leechers: int = Field(default=0)  # 下载人数
    completed: int = Field(default=0)  # 完成人数
    download_status: str = Field(default="pending")  # 下载状态: pending, downloading, completed, failed
    download_path: str = Field(default="")  # 下载路径
    anime_id: Optional[int] = Field(default=None)  # 关联的动漫ID
    episode_id: Optional[int] = Field(default=None)  # 关联的剧集ID
    created_at: Optional[datetime] = Field(default=None)  # 创建时间
    updated_at: Optional[datetime] = Field(default=None)  # 更新时间