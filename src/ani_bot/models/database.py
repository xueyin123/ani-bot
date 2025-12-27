from datetime import datetime
from typing import List, Optional
from sqlmodel import Session
from .anime_models import Anime, Episode
from .rss_models import RSSFeed, RSSItem
from .torrent_models import Torrent


class RSSDatabase:
    """RSS数据库管理类"""
    def __init__(self, session: Session):
        self.session = session

class AnimeDatabase:
    """动漫数据库管理类"""
    
    def __init__(self, db_path: str = "./data/anime.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建动漫表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                original_name TEXT,
                season INTEGER DEFAULT 1,
                episode INTEGER DEFAULT 0,
                total_episodes INTEGER DEFAULT 0,
                air_date TEXT,
                status TEXT DEFAULT 'ongoing',
                last_updated TEXT,
                next_air_date TEXT,
                description TEXT,
                cover_image_url TEXT,
                source_url TEXT,
                download_status TEXT DEFAULT 'pending',
                download_path TEXT
            )
        ''')
        
        # 创建剧集表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER,
                episode_number INTEGER,
                title TEXT,
                air_date TEXT,
                download_url TEXT,
                torrent_hash TEXT,
                download_status TEXT DEFAULT 'pending',
                download_path TEXT,
                size INTEGER DEFAULT 0,
                quality TEXT,
                FOREIGN KEY (anime_id) REFERENCES anime (id)
            )
        ''')
        
        # 创建RSS源表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                site_url TEXT,
                category TEXT,
                enabled BOOLEAN DEFAULT 1,
                last_checked TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # 创建RSS条目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rss_feed_id INTEGER,
                title TEXT,
                link TEXT,
                description TEXT,
                publish_date TEXT,
                torrent_url TEXT,
                magnet_link TEXT,
                enclosure_url TEXT,
                guid TEXT UNIQUE,
                read_status TEXT DEFAULT 'unread',
                anime_id INTEGER,
                episode_id INTEGER,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (rss_feed_id) REFERENCES rss_feeds (id),
                FOREIGN KEY (anime_id) REFERENCES anime (id),
                FOREIGN KEY (episode_id) REFERENCES episodes (id)
            )
        ''')
        
        # 创建种子表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS torrents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                size INTEGER DEFAULT 0,
                magnet_link TEXT,
                torrent_url TEXT,
                torrent_hash TEXT,
                category TEXT,
                quality TEXT,
                source TEXT,
                publish_date TEXT,
                seeders INTEGER DEFAULT 0,
                leechers INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                download_status TEXT DEFAULT 'pending',
                download_path TEXT,
                anime_id INTEGER,
                episode_id INTEGER,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (anime_id) REFERENCES anime (id),
                FOREIGN KEY (episode_id) REFERENCES episodes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Anime相关方法
    def add_anime(self, anime: Anime) -> int:
        """添加动漫到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO anime (
                name, original_name, season, episode, total_episodes, 
                air_date, status, last_updated, next_air_date, 
                description, cover_image_url, source_url, 
                download_status, download_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            anime.name, anime.original_name, anime.season, anime.episode,
            anime.total_episodes, 
            anime.air_date.isoformat() if anime.air_date else None,
            anime.status,
            anime.last_updated.isoformat() if anime.last_updated else None,
            anime.next_air_date.isoformat() if anime.next_air_date else None,
            anime.description, anime.cover_image_url, anime.source_url,
            anime.download_status, anime.download_path
        ))
        
        anime_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return anime_id
    
    def update_anime(self, anime: Anime):
        """更新动漫信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE anime SET
                name = ?, original_name = ?, season = ?, episode = ?, 
                total_episodes = ?, air_date = ?, status = ?, 
                last_updated = ?, next_air_date = ?, description = ?, 
                cover_image_url = ?, source_url = ?, 
                download_status = ?, download_path = ?
            WHERE id = ?
        ''', (
            anime.name, anime.original_name, anime.season, anime.episode,
            anime.total_episodes,
            anime.air_date.isoformat() if anime.air_date else None,
            anime.status,
            anime.last_updated.isoformat() if anime.last_updated else None,
            anime.next_air_date.isoformat() if anime.next_air_date else None,
            anime.description, anime.cover_image_url, anime.source_url,
            anime.download_status, anime.download_path, anime.id
        ))
        
        conn.commit()
        conn.close()
    
    def get_anime_by_id(self, anime_id: int) -> Optional[Anime]:
        """根据ID获取动漫信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM anime WHERE id = ?', (anime_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Anime(
                id=row[0], name=row[1], original_name=row[2], 
                season=row[3], episode=row[4], total_episodes=row[5],
                air_date=datetime.fromisoformat(row[6]) if row[6] else None,
                status=row[7],
                last_updated=datetime.fromisoformat(row[8]) if row[8] else None,
                next_air_date=datetime.fromisoformat(row[9]) if row[9] else None,
                description=row[10], cover_image_url=row[11], 
                source_url=row[12], download_status=row[13], 
                download_path=row[14]
            )
        return None
    
    def get_anime_by_name(self, name: str) -> Optional[Anime]:
        """根据名称获取动漫信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM anime WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Anime(
                id=row[0], name=row[1], original_name=row[2], 
                season=row[3], episode=row[4], total_episodes=row[5],
                air_date=datetime.fromisoformat(row[6]) if row[6] else None,
                status=row[7],
                last_updated=datetime.fromisoformat(row[8]) if row[8] else None,
                next_air_date=datetime.fromisoformat(row[9]) if row[9] else None,
                description=row[10], cover_image_url=row[11], 
                source_url=row[12], download_status=row[13], 
                download_path=row[14]
            )
        return None
    
    def get_all_animes(self) -> List[Anime]:
        """获取所有动漫信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM anime')
        rows = cursor.fetchall()
        conn.close()
        
        animes = []
        for row in rows:
            anime = Anime(
                id=row[0], name=row[1], original_name=row[2], 
                season=row[3], episode=row[4], total_episodes=row[5],
                air_date=datetime.fromisoformat(row[6]) if row[6] else None,
                status=row[7],
                last_updated=datetime.fromisoformat(row[8]) if row[8] else None,
                next_air_date=datetime.fromisoformat(row[9]) if row[9] else None,
                description=row[10], cover_image_url=row[11], 
                source_url=row[12], download_status=row[13], 
                download_path=row[14]
            )
            animes.append(anime)
        
        return animes
    
    def add_episode(self, episode: Episode) -> int:
        """添加剧集到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO episodes (
                anime_id, episode_number, title, air_date, 
                download_url, torrent_hash, download_status, 
                download_path, size, quality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            episode.anime_id, episode.episode_number, episode.title,
            episode.air_date.isoformat() if episode.air_date else None,
            episode.download_url, episode.torrent_hash, 
            episode.download_status, episode.download_path,
            episode.size, episode.quality
        ))
        
        episode_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return episode_id
    
    def get_episodes_by_anime_id(self, anime_id: int) -> List[Episode]:
        """根据动漫ID获取剧集列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM episodes WHERE anime_id = ?', (anime_id,))
        rows = cursor.fetchall()
        conn.close()
        
        episodes = []
        for row in rows:
            episode = Episode(
                id=row[0], anime_id=row[1], episode_number=row[2],
                title=row[3],
                air_date=datetime.fromisoformat(row[4]) if row[4] else None,
                download_url=row[5], torrent_hash=row[6],
                download_status=row[7], download_path=row[8],
                size=row[9], quality=row[10]
            )
            episodes.append(episode)
        
        return episodes
    
    def delete_anime(self, anime_id: int):
        """根据ID删除动漫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 先删除相关的剧集
        cursor.execute('DELETE FROM episodes WHERE anime_id = ?', (anime_id,))
        
        # 再删除动漫本身
        cursor.execute('DELETE FROM anime WHERE id = ?', (anime_id,))
        
        conn.commit()
        conn.close()
    
    # RSS相关方法
    def add_rss_feed(self, rss_feed: RSSFeed) -> int:
        """添加RSS源到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rss_feeds (
                name, url, site_url, category, 
                enabled, last_checked, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rss_feed.name, rss_feed.url, rss_feed.site_url, rss_feed.category,
            rss_feed.enabled,
            rss_feed.last_checked.isoformat() if rss_feed.last_checked else None,
            rss_feed.created_at.isoformat() if rss_feed.created_at else datetime.now().isoformat(),
            rss_feed.updated_at.isoformat() if rss_feed.updated_at else datetime.now().isoformat()
        ))
        
        feed_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feed_id
    
    def update_rss_feed(self, rss_feed: RSSFeed):
        """更新RSS源信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE rss_feeds SET
                name = ?, url = ?, site_url = ?, category = ?,
                enabled = ?, last_checked = ?, updated_at = ?
            WHERE id = ?
        ''', (
            rss_feed.name, rss_feed.url, rss_feed.site_url, rss_feed.category,
            rss_feed.enabled,
            rss_feed.last_checked.isoformat() if rss_feed.last_checked else None,
            datetime.now().isoformat(),
            rss_feed.id
        ))
        
        conn.commit()
        conn.close()
    
    def get_rss_feed_by_id(self, feed_id: int) -> Optional[RSSFeed]:
        """根据ID获取RSS源信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM rss_feeds WHERE id = ?', (feed_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return RSSFeed(
                id=row[0], name=row[1], url=row[2], site_url=row[3],
                category=row[4],
                enabled=bool(row[5]) if row[5] is not None else True,
                last_checked=datetime.fromisoformat(row[6]) if row[6] else None,
                created_at=datetime.fromisoformat(row[7]) if row[7] else None,
                updated_at=datetime.fromisoformat(row[8]) if row[8] else None
            )
        return None
    
    def get_rss_feed_by_url(self, url: str) -> Optional[RSSFeed]:
        """根据URL获取RSS源信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM rss_feeds WHERE url = ?', (url,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return RSSFeed(
                id=row[0], name=row[1], url=row[2], site_url=row[3],
                category=row[4],
                enabled=bool(row[5]) if row[5] is not None else True,
                last_checked=datetime.fromisoformat(row[6]) if row[6] else None,
                created_at=datetime.fromisoformat(row[7]) if row[7] else None,
                updated_at=datetime.fromisoformat(row[8]) if row[8] else None
            )
        return None
    
    def get_all_rss_feeds(self) -> List[RSSFeed]:
        """获取所有RSS源信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM rss_feeds')
        rows = cursor.fetchall()
        conn.close()
        
        feeds = []
        for row in rows:
            feed = RSSFeed(
                id=row[0], name=row[1], url=row[2], site_url=row[3],
                category=row[4],
                enabled=bool(row[5]) if row[5] is not None else True,
                last_checked=datetime.fromisoformat(row[6]) if row[6] else None,
                created_at=datetime.fromisoformat(row[7]) if row[7] else None,
                updated_at=datetime.fromisoformat(row[8]) if row[8] else None
            )
            feeds.append(feed)
        
        return feeds
    
    def add_rss_item(self, rss_item: RSSItem) -> int:
        """添加RSS条目到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rss_items (
                rss_feed_id, title, link, description, publish_date,
                torrent_url, magnet_link, enclosure_url, guid,
                read_status, anime_id, episode_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rss_item.rss_feed_id, rss_item.title, rss_item.link, rss_item.description,
            rss_item.publish_date.isoformat() if rss_item.publish_date else None,
            rss_item.torrent_url, rss_item.magnet_link, rss_item.enclosure_url,
            rss_item.guid, rss_item.read_status, rss_item.anime_id, rss_item.episode_id,
            rss_item.created_at.isoformat() if rss_item.created_at else datetime.now().isoformat(),
            rss_item.updated_at.isoformat() if rss_item.updated_at else datetime.now().isoformat()
        ))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return item_id
    
    def update_rss_item(self, rss_item: RSSItem):
        """更新RSS条目信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE rss_items SET
                rss_feed_id = ?, title = ?, link = ?, description = ?, publish_date = ?,
                torrent_url = ?, magnet_link = ?, enclosure_url = ?,
                read_status = ?, anime_id = ?, episode_id = ?, updated_at = ?
            WHERE id = ?
        ''', (
            rss_item.rss_feed_id, rss_item.title, rss_item.link, rss_item.description,
            rss_item.publish_date.isoformat() if rss_item.publish_date else None,
            rss_item.torrent_url, rss_item.magnet_link, rss_item.enclosure_url,
            rss_item.read_status, rss_item.anime_id, rss_item.episode_id,
            datetime.now().isoformat(),
            rss_item.id
        ))
        
        conn.commit()
        conn.close()
    
    def get_rss_item_by_id(self, item_id: int) -> Optional[RSSItem]:
        """根据ID获取RSS条目信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM rss_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return RSSItem(
                id=row[0], rss_feed_id=row[1], title=row[2], link=row[3],
                description=row[4],
                publish_date=datetime.fromisoformat(row[5]) if row[5] else None,
                torrent_url=row[6], magnet_link=row[7], enclosure_url=row[8],
                guid=row[9], read_status=row[10],
                anime_id=row[11] if row[11] else None,
                episode_id=row[12] if row[12] else None,
                created_at=datetime.fromisoformat(row[13]) if row[13] else None,
                updated_at=datetime.fromisoformat(row[14]) if row[14] else None
            )
        return None
    
    def get_rss_items_by_feed_id(self, feed_id: int) -> List[RSSItem]:
        """根据RSS源ID获取RSS条目列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM rss_items WHERE rss_feed_id = ?', (feed_id,))
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            item = RSSItem(
                id=row[0], rss_feed_id=row[1], title=row[2], link=row[3],
                description=row[4],
                publish_date=datetime.fromisoformat(row[5]) if row[5] else None,
                torrent_url=row[6], magnet_link=row[7], enclosure_url=row[8],
                guid=row[9], read_status=row[10],
                anime_id=row[11] if row[11] else None,
                episode_id=row[12] if row[12] else None,
                created_at=datetime.fromisoformat(row[13]) if row[13] else None,
                updated_at=datetime.fromisoformat(row[14]) if row[14] else None
            )
            items.append(item)
        
        return items
    
    def get_unread_rss_items(self) -> List[RSSItem]:
        """获取所有未读RSS条目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM rss_items WHERE read_status = "unread"')
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            item = RSSItem(
                id=row[0], rss_feed_id=row[1], title=row[2], link=row[3],
                description=row[4],
                publish_date=datetime.fromisoformat(row[5]) if row[5] else None,
                torrent_url=row[6], magnet_link=row[7], enclosure_url=row[8],
                guid=row[9], read_status=row[10],
                anime_id=row[11] if row[11] else None,
                episode_id=row[12] if row[12] else None,
                created_at=datetime.fromisoformat(row[13]) if row[13] else None,
                updated_at=datetime.fromisoformat(row[14]) if row[14] else None
            )
            items.append(item)
        
        return items
    
    # Torrent相关方法
    def add_torrent(self, torrent: Torrent) -> int:
        """添加种子到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO torrents (
                title, size, magnet_link, torrent_url, torrent_hash,
                category, quality, source, publish_date,
                seeders, leechers, completed, download_status,
                download_path, anime_id, episode_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            torrent.title, torrent.size, torrent.magnet_link, torrent.torrent_url,
            torrent.torrent_hash, torrent.category, torrent.quality, torrent.source,
            torrent.publish_date.isoformat() if torrent.publish_date else None,
            torrent.seeders, torrent.leechers, torrent.completed,
            torrent.download_status, torrent.download_path,
            torrent.anime_id, torrent.episode_id,
            torrent.created_at.isoformat() if torrent.created_at else datetime.now().isoformat(),
            torrent.updated_at.isoformat() if torrent.updated_at else datetime.now().isoformat()
        ))
        
        torrent_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return torrent_id
    
    def update_torrent(self, torrent: Torrent):
        """更新种子信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE torrents SET
                title = ?, size = ?, magnet_link = ?, torrent_url = ?, torrent_hash = ?,
                category = ?, quality = ?, source = ?, publish_date = ?,
                seeders = ?, leechers = ?, completed = ?, download_status = ?,
                download_path = ?, anime_id = ?, episode_id = ?, updated_at = ?
            WHERE id = ?
        ''', (
            torrent.title, torrent.size, torrent.magnet_link, torrent.torrent_url,
            torrent.torrent_hash, torrent.category, torrent.quality, torrent.source,
            torrent.publish_date.isoformat() if torrent.publish_date else None,
            torrent.seeders, torrent.leechers, torrent.completed,
            torrent.download_status, torrent.download_path,
            torrent.anime_id, torrent.episode_id,
            datetime.now().isoformat(),
            torrent.id
        ))
        
        conn.commit()
        conn.close()
    
    def get_torrent_by_id(self, torrent_id: int) -> Optional[Torrent]:
        """根据ID获取种子信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM torrents WHERE id = ?', (torrent_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Torrent(
                id=row[0], title=row[1], size=row[2],
                magnet_link=row[3], torrent_url=row[4], torrent_hash=row[5],
                category=row[6], quality=row[7], source=row[8],
                publish_date=datetime.fromisoformat(row[9]) if row[9] else None,
                seeders=row[10], leechers=row[11], completed=row[12],
                download_status=row[13], download_path=row[14],
                anime_id=row[15] if row[15] else None,
                episode_id=row[16] if row[16] else None,
                created_at=datetime.fromisoformat(row[17]) if row[17] else None,
                updated_at=datetime.fromisoformat(row[18]) if row[18] else None
            )
        return None
    
    def get_torrent_by_hash(self, torrent_hash: str) -> Optional[Torrent]:
        """根据哈希获取种子信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM torrents WHERE torrent_hash = ?', (torrent_hash,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Torrent(
                id=row[0], title=row[1], size=row[2],
                magnet_link=row[3], torrent_url=row[4], torrent_hash=row[5],
                category=row[6], quality=row[7], source=row[8],
                publish_date=datetime.fromisoformat(row[9]) if row[9] else None,
                seeders=row[10], leechers=row[11], completed=row[12],
                download_status=row[13], download_path=row[14],
                anime_id=row[15] if row[15] else None,
                episode_id=row[16] if row[16] else None,
                created_at=datetime.fromisoformat(row[17]) if row[17] else None,
                updated_at=datetime.fromisoformat(row[18]) if row[18] else None
            )
        return None
    
    def get_torrents_by_anime_id(self, anime_id: int) -> List[Torrent]:
        """根据动漫ID获取种子列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM torrents WHERE anime_id = ?', (anime_id,))
        rows = cursor.fetchall()
        conn.close()
        
        torrents = []
        for row in rows:
            torrent = Torrent(
                id=row[0], title=row[1], size=row[2],
                magnet_link=row[3], torrent_url=row[4], torrent_hash=row[5],
                category=row[6], quality=row[7], source=row[8],
                publish_date=datetime.fromisoformat(row[9]) if row[9] else None,
                seeders=row[10], leechers=row[11], completed=row[12],
                download_status=row[13], download_path=row[14],
                anime_id=row[15] if row[15] else None,
                episode_id=row[16] if row[16] else None,
                created_at=datetime.fromisoformat(row[17]) if row[17] else None,
                updated_at=datetime.fromisoformat(row[18]) if row[18] else None
            )
            torrents.append(torrent)
        
        return torrents