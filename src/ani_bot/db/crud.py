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
    if not anime:
        raise ValueError("Anime object cannot be None")
    
    if len(episodes) != len(torrents):
        raise ValueError("Episodes and torrents lists must have the same length")
    
    try:
        with session_scope() as db_session:
            # 查找或创建动漫
            select_anime = select(Anime).where(Anime.original_title == anime.original_title)
            existing_anime = db_session.exec(select_anime).first()
            
            if existing_anime:
                # 更新现有动漫的字段
                existing_anime.title = anime.title
                existing_anime.original_title = anime.original_title
                existing_anime.air_date = anime.air_date
                existing_anime.status = anime.status
                existing_anime.description = anime.description
                existing_anime.download_status = anime.download_status
                existing_anime.download_path = anime.download_path
                existing_anime.season = anime.season
                existing_anime.total_episodes = anime.total_episodes
                existing_anime.last_updated = anime.last_updated
                existing_anime.next_air_date = anime.next_air_date
                anime = existing_anime
            else:
                db_session.add(anime)
                db_session.flush()  # 获取ID但不提交事务
            
            for episode, torrent in zip(episodes, torrents):
                # 查找或创建剧集
                select_episode = select(Episode).where(
                    Episode.anime_id == anime.id,
                    Episode.episode_number == episode.episode_number
                )
                existing_episode = db_session.exec(select_episode).first()
                
                if existing_episode:
                    # 更新现有剧集的字段
                    existing_episode.title = episode.title
                    existing_episode.original_title = episode.original_title
                    existing_episode.air_date = episode.air_date
                    existing_episode.download_url = episode.download_url
                    existing_episode.download_status = episode.download_status
                    existing_episode.download_path = episode.download_path
                    existing_episode.quality = episode.quality
                    episode = existing_episode
                else:
                    episode.anime_id = anime.id
                    db_session.add(episode)
                    db_session.flush()  # 获取ID但不提交事务
                
                # 查找或创建种子
                select_torrent = select(Torrent).where(
                    Torrent.torrent_url == torrent.torrent_url
                )
                existing_torrent = db_session.exec(select_torrent).first()
                
                if existing_torrent:
                    # 更新现有种子的字段
                    existing_torrent.title = torrent.title
                    existing_torrent.size = torrent.size
                    existing_torrent.magnet_link = torrent.magnet_link
                    existing_torrent.torrent_hash = torrent.torrent_hash
                    existing_torrent.category = torrent.category
                    existing_torrent.quality = torrent.quality
                    existing_torrent.source = torrent.source
                    existing_torrent.download_status = torrent.download_status
                    existing_torrent.download_path = torrent.download_path
                    existing_torrent.anime_id = anime.id
                    existing_torrent.episode_id = episode.id
                    existing_torrent.created_at = torrent.created_at
                    existing_torrent.updated_at = torrent.updated_at
                else:
                    torrent.anime_id = anime.id
                    torrent.episode_id = episode.id
                    db_session.add(torrent)
            
            db_session.commit()
    except Exception as e:
        raise RuntimeError(f"Failed to save parsed RSS result: {str(e)}")