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
        return [row for row in db_session.exec(statement).all()]
    
async def save_parsed_rss_result(anime: Anime, episodes: List[Episode], torrents: List[Torrent]) -> None:
    """保存解析结果到数据库"""
    with session_scope() as db_session:
        select_anime = select(Anime).where(Anime.original_title == anime.original_title)
        existing_anime = db_session.exec(select_anime).first()
        if existing_anime:
            anime.id = existing_anime.id  # 使用现有动漫ID
        else:
            db_session.add(anime)
        
        for i, episode in enumerate(episodes):
            select_episode = select(Episode).where(
                Episode.anime_id == anime.id,
                Episode.episode_number == episode.episode_number
            )
            existing_episode = db_session.exec(select_episode).first()
            if existing_episode:
                episode.id = existing_episode.id  # 使用现有剧集ID
            else:
                episode.anime_id = anime.id
                db_session.add(episode)


            torrent = torrents[i]

            select_torrent = select(Torrent).where(
                Torrent.torrent_url == torrent.torrent_url
            )
            existing_torrent = db_session.exec(select_torrent).first()
            if existing_torrent:
                torrent.id = existing_torrent.id  # 使用现有种子ID
            else:
                torrent.anime_id = anime.id
                torrent.episode_id = episode.id
                db_session.add(torrent)
        
        db_session.commit()