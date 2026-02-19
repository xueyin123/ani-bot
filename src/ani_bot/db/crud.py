from typing import List, Optional, Sequence
from sqlmodel import Session, select

from ani_bot.core.db import session_scope
from .models import RSSFeed, Anime, Episode, Torrent

def get_rss_feeds(db_session: Session, skip: int = 0, limit: int = 100) -> Sequence[RSSFeed]:
    """获取RSS源列表"""
    limit = min(limit, 500)
    statement = (
        select(RSSFeed)
        .offset(skip)
        .limit(limit)
    )
    return db_session.exec(statement).all()

def create_rss_feed(db_session: Session, rss_feed: RSSFeed) -> RSSFeed:
    """创建新的RSS源"""
    db_session.add(rss_feed)
    db_session.commit()
    db_session.refresh(rss_feed)
    return rss_feed

def delete_rss_feed(db_session: Session, rss_id: int) -> None:
    """删除指定ID的RSS源"""
    rss_feed = db_session.get(RSSFeed, rss_id)
    if rss_feed:
        db_session.delete(rss_feed)
        db_session.commit()

def update_rss_feed(db_session: Session, rss_id: int, rss_feed: RSSFeed) -> Optional[RSSFeed]:
    """更新指定ID的RSS源"""
    existing_feed = db_session.get(RSSFeed, rss_id)
    if not existing_feed:
        return None
    
    existing_feed.url = rss_feed.url
    existing_feed.name = rss_feed.name
    
    db_session.add(existing_feed)
    db_session.commit()
    db_session.refresh(existing_feed)
    
    return existing_feed

async def get_all_rss_feed_urls() -> List[str]:
    """获取所有RSS源的URL列表"""
    with session_scope() as db_session:
        statement = select(RSSFeed.url)
        return [row[0] for row in db_session.exec(statement).all()]