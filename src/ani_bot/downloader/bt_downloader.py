import os
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from qbittorrent import Client


class BTDownloader(ABC):
    """BT下载器抽象基类"""
    
    def __init__(self, config):
        self.config = config
        self.save_path = config.get('download.save_path', './downloads')
        self.max_download_speed = config.get('download.max_download_speed', -1)
        self.max_upload_speed = config.get('download.max_upload_speed', -1)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 确保下载目录存在
        os.makedirs(self.save_path, exist_ok=True)
    
    @abstractmethod
    async def add_torrent(self, torrent_url: str, save_path: str = None) -> bool:
        """添加BT下载任务"""
        pass
    
    @abstractmethod
    def add_magnet(self, magnet_link: str, save_path: str = None) -> bool:
        """添加磁力链接下载任务"""
        pass
    
    @abstractmethod
    def get_download_status(self, torrent_id: str) -> Dict[str, Any]:
        """获取下载状态"""
        pass
    
    @abstractmethod
    def pause_download(self, torrent_id: str) -> bool:
        """暂停下载"""
        pass
    
    @abstractmethod
    def resume_download(self, torrent_id: str) -> bool:
        """恢复下载"""
        pass
    
    @abstractmethod
    def remove_download(self, torrent_id: str, delete_files: bool = False) -> bool:
        """移除下载任务"""
        pass

