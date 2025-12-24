from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import sqlite3


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