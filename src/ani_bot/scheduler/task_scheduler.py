import time
import threading
import schedule
from datetime import datetime
from typing import Callable, Any
import logging
from ani_bot.models import Anime, Episode
from ani_bot.crawlers.base_crawler import BangumiCrawler
from ani_bot.downloader.bt_downloader import BTDownloadManager


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, config):
        self.config = config
        self.check_interval = config.get('scheduler.check_interval', 1800)  # 默认30分钟
        self.enable_auto_download = config.get('scheduler.enable_auto_download', True)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.crawler = BangumiCrawler(config)
        self.downloader = BTDownloadManager(config)
        
        self.running = False
        self.scheduler_thread = None
        
    def start(self):
        """启动调度器"""
        if self.running:
            self.logger.warning("调度器已在运行中")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        self.logger.info("调度器已停止")
    
    def _run_scheduler(self):
        """运行调度器主循环"""
        # 立即执行一次检查
        self._check_new_episodes()
        
        # 设置定时任务
        schedule.every(self.check_interval).seconds.do(self._check_new_episodes)
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _check_new_episodes(self):
        """检查新剧集"""
        self.logger.info("开始检查新剧集...")
        
        try:
            # 从数据库获取所有需要跟踪的动漫
            from ani_bot.models import AnimeDatabase
            db = AnimeDatabase(self.config.get('database.path', './data/anime.db'))
            animes = db.get_all_animes()
            
            for anime in animes:
                self.logger.info(f"检查动漫: {anime.name}")
                
                # 获取动漫的最新信息
                updated_anime = self._update_anime_info(anime)
                if updated_anime:
                    # 更新数据库中的动漫信息
                    db.update_anime(updated_anime)
                    
                    # 获取最新剧集
                    latest_episodes = self.crawler.get_latest_episodes(updated_anime)
                    
                    for episode in latest_episodes:
                        # 检查剧集是否已经存在
                        existing_episodes = db.get_episodes_by_anime_id(updated_anime.id)
                        existing_episode_numbers = [ep.episode_number for ep in existing_episodes]
                        
                        if episode.episode_number not in existing_episode_numbers:
                            # 新剧集，添加到数据库
                            episode.anime_id = updated_anime.id
                            db.add_episode(episode)
                            
                            # 如果启用了自动下载，则开始下载
                            if self.enable_auto_download:
                                self.logger.info(f"发现新剧集 {updated_anime.name} 第{episode.episode_number}集，开始下载...")
                                success = self.downloader.download_episode(episode)
                                if success:
                                    self.logger.info(f"成功添加下载任务: {updated_anime.name} 第{episode.episode_number}集")
                                    
                                    # 更新剧集下载状态
                                    episode.download_status = "downloading"
                                    # 这里应该更新数据库中的剧集状态
                                else:
                                    self.logger.error(f"添加下载任务失败: {updated_anime.name} 第{episode.episode_number}集")
            
            self.logger.info("检查新剧集完成")
        except Exception as e:
            self.logger.error(f"检查新剧集过程中出现错误: {e}")
    
    def _update_anime_info(self, anime: Anime) -> Anime:
        """更新动漫信息"""
        # 这里需要根据具体的动漫来源更新信息
        # 对于Bangumi，我们可以使用API获取最新信息
        if "bgm.tv" in anime.source_url:
            # 从URL中提取ID
            import re
            match = re.search(r'subject/(\d+)', anime.source_url)
            if match:
                subject_id = match.group(1)
                updated_info = self.crawler.get_anime_detail(subject_id)
                if updated_info:
                    # 更新动漫信息
                    anime.name = updated_info.name
                    anime.original_name = updated_info.original_name
                    anime.description = updated_info.description
                    anime.air_date = updated_info.air_date
                    anime.total_episodes = updated_info.total_episodes
                    anime.cover_image_url = updated_info.cover_image_url
                    anime.last_updated = datetime.now()
        
        return anime
    
    def add_anime_to_track(self, anime: Anime):
        """添加动漫到跟踪列表"""
        from ani_bot.models import AnimeDatabase
        db = AnimeDatabase(self.config.get('database.path', './data/anime.db'))
        
        # 检查动漫是否已存在
        existing_anime = db.get_anime_by_name(anime.name)
        if existing_anime:
            self.logger.warning(f"动漫 {anime.name} 已存在，ID: {existing_anime.id}")
            return existing_anime.id
        
        # 添加新的动漫
        anime_id = db.add_anime(anime)
        self.logger.info(f"已添加动漫到跟踪列表: {anime.name}, ID: {anime_id}")
        return anime_id
    
    def remove_anime_from_track(self, anime_id: int):
        """从跟踪列表移除动漫"""
        from ani_bot.models import AnimeDatabase
        db = AnimeDatabase(self.config.get('database.path', './data/anime.db'))
        
        # 这里可以添加暂停相关下载任务的逻辑
        anime = db.get_anime_by_id(anime_id)
        if anime:
            self.logger.info(f"已从跟踪列表移除动漫: {anime.name}")
        else:
            self.logger.warning(f"未找到ID为 {anime_id} 的动漫")