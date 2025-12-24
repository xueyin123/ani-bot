import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from ani_bot.models.anime import Anime, Episode
import time
import logging


class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('crawler.user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        })
        self.timeout = config.get('crawler.timeout', 30)
        self.retry_times = config.get('crawler.retry_times', 3)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        for attempt in range(self.retry_times):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                self.logger.warning(f"获取页面失败 (尝试 {attempt + 1}/{self.retry_times}): {url}, 错误: {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    self.logger.error(f"获取页面最终失败: {url}")
                    return None
        return None
    
    @abstractmethod
    def search_anime(self, keyword: str) -> List[Anime]:
        """搜索动漫"""
        pass
    
    @abstractmethod
    def get_anime_detail(self, anime_id: str) -> Optional[Anime]:
        """获取动漫详细信息"""
        pass
    
    @abstractmethod
    def get_latest_episodes(self, anime: Anime) -> List[Episode]:
        """获取动漫最新剧集"""
        pass


class BangumiCrawler(BaseCrawler):
    """Bangumi番组计划爬虫"""
    
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.bgm.tv"
    
    def search_anime(self, keyword: str) -> List[Anime]:
        """搜索动漫"""
        url = f"{self.base_url}/search/subject/{keyword}?type=2"
        content = self.fetch_page(url)
        
        if not content:
            return []
        
        try:
            import json
            data = json.loads(content)
            animes = []
            
            if 'list' in data:
                for item in data['list']:
                    anime = Anime(
                        name=item.get('name', ''),
                        original_name=item.get('name_cn', ''),
                        description=item.get('summary', ''),
                        cover_image_url=item.get('images', {}).get('large', ''),
                        source_url=f"https://bgm.tv/subject/{item.get('id', '')}"
                    )
                    animes.append(anime)
            
            return animes
        except Exception as e:
            self.logger.error(f"解析搜索结果失败: {e}")
            return []
    
    def get_anime_detail(self, subject_id: str) -> Optional[Anime]:
        """获取动漫详细信息"""
        url = f"{self.base_url}/v0/subjects/{subject_id}"
        content = self.fetch_page(url)
        
        if not content:
            return None
        
        try:
            import json
            data = json.loads(content)
            
            # 获取放送信息
            air_date = None
            if 'date' in data and data['date']:
                from datetime import datetime
                air_date = datetime.strptime(data['date'], '%Y-%m-%d')
            
            anime = Anime(
                name=data.get('name', ''),
                original_name=data.get('name_cn', ''),
                description=data.get('summary', ''),
                air_date=air_date,
                cover_image_url=data.get('images', {}).get('large', ''),
                source_url=f"https://bgm.tv/subject/{subject_id}",
                total_episodes=data.get('eps', 0)
            )
            
            return anime
        except Exception as e:
            self.logger.error(f"解析动漫详情失败: {e}")
            return None
    
    def get_latest_episodes(self, anime: Anime) -> List[Episode]:
        """获取动漫最新剧集（Bangumi API不直接提供剧集下载链接，需要其他方式获取）"""
        # Bangumi API不直接提供下载链接，这里只是示例
        # 实际使用中需要结合其他资源站获取下载链接
        return []


class SubSourceCrawler(BaseCrawler):
    """字幕组资源爬虫"""
    
    def __init__(self, config):
        super().__init__(config)
        # 这里可以添加各种字幕组或资源站的爬取逻辑
        self.sources = []
    
    def search_anime(self, keyword: str) -> List[Anime]:
        """从资源站搜索动漫"""
        # 实现从各种资源站搜索动漫的逻辑
        # 由于版权原因，这里不提供具体实现
        self.logger.info(f"从资源站搜索: {keyword}")
        return []
    
    def get_anime_detail(self, anime_id: str) -> Optional[Anime]:
        """获取资源站动漫详情"""
        # 实现获取资源站动漫详情的逻辑
        return None
    
    def get_latest_episodes(self, anime: Anime) -> List[Episode]:
        """获取最新剧集下载链接"""
        # 实现获取最新剧集下载链接的逻辑
        return []