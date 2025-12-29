from typing import List, Optional
from sqlmodel import Session, select
from .models import RSSItem, RSSFeed, Anime, Episode, Torrent


def get_rss_items(db_session: Session, skip: int = 0, limit: int = 100) -> List[RSSItem]:
    """获取RSS项目列表"""
    statement = select(RSSItem).offset(skip).limit(limit)
    return db_session.exec(statement).all()


def get_rss_item(db_session: Session, rss_item_id: int) -> Optional[RSSItem]:
    """根据ID获取RSS项目"""
    return db_session.get(RSSItem, rss_item_id)


def create_rss_item(db_session: Session, rss_item: RSSItem) -> RSSItem:
    """创建RSS项目"""
    db_session.add(rss_item)
    db_session.commit()
    db_session.refresh(rss_item)
    return rss_item


def update_rss_item(db_session: Session, rss_item_id: int, rss_item_data: RSSItem) -> Optional[RSSItem]:
    """更新RSS项目"""
    rss_item = db_session.get(RSSItem, rss_item_id)
    if rss_item:
        # 更新字段
        update_data = rss_item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rss_item, field, value)
        
        db_session.add(rss_item)
        db_session.commit()
        db_session.refresh(rss_item)
    return rss_item


def delete_rss_item(db_session: Session, rss_item_id: int) -> Optional[RSSItem]:
    """删除RSS项目"""
    rss_item = db_session.get(RSSItem, rss_item_id)
    if rss_item:
        db_session.delete(rss_item)
        db_session.commit()
    return rss_item


def get_rss_feeds(db_session: Session, skip: int = 0, limit: int = 100) -> List[RSSFeed]:
    """获取RSS源列表"""
    statement = select(RSSFeed).offset(skip).limit(limit)
    return db_session.exec(statement).all()


def get_animes(db_session: Session, skip: int = 0, limit: int = 100) -> List[Anime]:
    """获取动漫列表"""
    statement = select(Anime).offset(skip).limit(limit)
    return db_session.exec(statement).all()


def get_episodes(db_session: Session, skip: int = 0, limit: int = 100) -> List[Episode]:
    """获取剧集列表"""
    statement = select(Episode).offset(skip).limit(limit)
    return db_session.exec(statement).all()


def get_torrents(db_session: Session, skip: int = 0, limit: int = 100) -> List[Torrent]:
    """获取种子列表"""
    statement = select(Torrent).offset(skip).limit(limit)
    return db_session.exec(statement).all()