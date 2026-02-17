from typing import List, Optional, Sequence
from sqlmodel import Session, select
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