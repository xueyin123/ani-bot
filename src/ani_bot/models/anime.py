from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import sqlite3
import json


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
        
        conn.commit()
        conn.close()
    
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