import os
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from ani_bot.models import Episode


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
    def add_torrent(self, torrent_url: str, save_path: str = None) -> bool:
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


class TransmissionDownloader(BTDownloader):
    """Transmission BT下载器"""
    
    def __init__(self, config):
        super().__init__(config)
        try:
            import transmissionrpc
            self.tc = transmissionrpc.Client(
                address=config.get('transmission.host', 'localhost'),
                port=config.get('transmission.port', 9091),
                user=config.get('transmission.username', ''),
                password=config.get('transmission.password', '')
            )
            # 测试连接
            self.tc.session_stats()
        except ImportError:
            self.logger.error("需要安装 transmissionrpc: pip install transmissionrpc")
            raise
        except Exception as e:
            self.logger.warning(f"无法连接到Transmission客户端: {e}，BT下载功能将不可用")
            self.tc = None
    
    def add_torrent(self, torrent_url: str, save_path: str = None) -> bool:
        """添加BT下载任务"""
        try:
            download_dir = save_path or self.save_path
            torrent = self.tc.add_torrent(torrent_url, download_dir=download_dir)
            
            # 设置速度限制
            if self.max_download_speed != -1:
                torrent.set_download_limit(self.max_download_speed)
            if self.max_upload_speed != -1:
                torrent.set_upload_limit(self.max_upload_speed)
            
            self.logger.info(f"已添加BT任务: {torrent_url}, ID: {torrent.id}")
            return True
        except Exception as e:
            self.logger.error(f"添加BT任务失败: {e}")
            return False
    
    def add_magnet(self, magnet_link: str, save_path: str = None) -> bool:
        """添加磁力链接下载任务"""
        try:
            download_dir = save_path or self.save_path
            torrent = self.tc.add_torrent(magnet_link, download_dir=download_dir)
            
            # 设置速度限制
            if self.max_download_speed != -1:
                torrent.set_download_limit(self.max_download_speed)
            if self.max_upload_speed != -1:
                torrent.set_upload_limit(self.max_upload_speed)
            
            self.logger.info(f"已添加磁力链接任务: {magnet_link}, ID: {torrent.id}")
            return True
        except Exception as e:
            self.logger.error(f"添加磁力链接任务失败: {e}")
            return False
    
    def get_download_status(self, torrent_id: str) -> Dict[str, Any]:
        """获取下载状态"""
        try:
            torrent = self.tc.get_torrent(torrent_id)
            return {
                'id': torrent.id,
                'name': torrent.name,
                'status': torrent.status,
                'progress': torrent.progress,
                'download_rate': torrent.rateDownload,
                'upload_rate': torrent.rateUpload,
                'total_size': torrent.totalSize,
                'left_until_done': torrent.leftUntilDone,
                'download_path': torrent.downloadDir
            }
        except Exception as e:
            self.logger.error(f"获取下载状态失败: {e}")
            return {}
    
    def pause_download(self, torrent_id: str) -> bool:
        """暂停下载"""
        try:
            self.tc.stop_torrent(torrent_id)
            self.logger.info(f"已暂停下载: {torrent_id}")
            return True
        except Exception as e:
            self.logger.error(f"暂停下载失败: {e}")
            return False
    
    def resume_download(self, torrent_id: str) -> bool:
        """恢复下载"""
        try:
            self.tc.start_torrent(torrent_id)
            self.logger.info(f"已恢复下载: {torrent_id}")
            return True
        except Exception as e:
            self.logger.error(f"恢复下载失败: {e}")
            return False
    
    def remove_download(self, torrent_id: str, delete_files: bool = False) -> bool:
        """移除下载任务"""
        try:
            self.tc.remove_torrent(torrent_id, delete_data=delete_files)
            self.logger.info(f"已移除下载任务: {torrent_id}")
            return True
        except Exception as e:
            self.logger.error(f"移除下载任务失败: {e}")
            return False


class QBittorrentDownloader(BTDownloader):
    """qBittorrent BT下载器"""
    
    def __init__(self, config):
        super().__init__(config)
        try:
            from qbittorrent import Client
            self.qb = Client(
                f"http://{config.get('qbittorrent.host', 'localhost')}:{config.get('qbittorrent.port', 8080)}/"
            )
            self.qb.login(
                config.get('qbittorrent.username', 'admin'),
                config.get('qbittorrent.password', 'adminadmin')
            )
        except ImportError:
            self.logger.error("需要安装 python-qbittorrent: pip install python-qbittorrent")
            raise
        except Exception as e:
            self.logger.warning(f"无法连接到qBittorrent客户端: {e}，BT下载功能将不可用")
            self.qb = None
    
    def add_torrent(self, torrent_url: str, save_path: str = None) -> bool:
        """添加BT下载任务"""
        try:
            download_dir = save_path or self.save_path
            self.qb.download_from_link(torrent_url)
            # qBittorrent中设置保存路径可能需要额外的API调用
            self.logger.info(f"已添加BT任务: {torrent_url}")
            return True
        except Exception as e:
            self.logger.error(f"添加BT任务失败: {e}")
            return False
    
    def add_magnet(self, magnet_link: str, save_path: str = None) -> bool:
        """添加磁力链接下载任务"""
        try:
            download_dir = save_path or self.save_path
            self.qb.download_from_link(magnet_link)
            self.logger.info(f"已添加磁力链接任务: {magnet_link}")
            return True
        except Exception as e:
            self.logger.error(f"添加磁力链接任务失败: {e}")
            return False
    
    def get_download_status(self, torrent_id: str) -> Dict[str, Any]:
        """获取下载状态"""
        try:
            torrents = self.qb.torrents()
            for torrent in torrents:
                if torrent['hash'] == torrent_id:
                    return {
                        'id': torrent['hash'],
                        'name': torrent['name'],
                        'status': torrent['state'],
                        'progress': torrent['progress'],
                        'download_rate': torrent['dlspeed'],
                        'upload_rate': torrent['upspeed'],
                        'total_size': torrent['total_size'],
                        'left_until_done': torrent['amount_left'],
                        'download_path': torrent['save_path']
                    }
        except Exception as e:
            self.logger.error(f"获取下载状态失败: {e}")
            return {}
        return {}
    
    def pause_download(self, torrent_id: str) -> bool:
        """暂停下载"""
        try:
            self.qb.pause(torrent_id)
            self.logger.info(f"已暂停下载: {torrent_id}")
            return True
        except Exception as e:
            self.logger.error(f"暂停下载失败: {e}")
            return False
    
    def resume_download(self, torrent_id: str) -> bool:
        """恢复下载"""
        try:
            self.qb.resume(torrent_id)
            self.logger.info(f"已恢复下载: {torrent_id}")
            return True
        except Exception as e:
            self.logger.error(f"恢复下载失败: {e}")
            return False
    
    def remove_download(self, torrent_id: str, delete_files: bool = False) -> bool:
        """移除下载任务"""
        try:
            self.qb.delete(torrent_id, delete_files=delete_files)
            self.logger.info(f"已移除下载任务: {torrent_id}")
            return True
        except Exception as e:
            self.logger.error(f"移除下载任务失败: {e}")
            return False


class BTDownloadManager:
    """BT下载管理器"""
    
    def __init__(self, config):
        self.config = config
        self.downloader_type = config.get('download.bt_client', 'transmission')
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if self.downloader_type == 'transmission':
            self.downloader = TransmissionDownloader(config)
        elif self.downloader_type == 'qbittorrent':
            self.downloader = QBittorrentDownloader(config)
        else:
            raise ValueError(f"不支持的BT客户端: {self.downloader_type}")
        
        # 检查下载器是否可用
        if hasattr(self.downloader, 'tc') and self.downloader.tc is None:
            self.logger.warning("Transmission客户端不可用，BT下载功能将被禁用")
        elif hasattr(self.downloader, 'qb') and self.downloader.qb is None:
            self.logger.warning("qBittorrent客户端不可用，BT下载功能将被禁用")
    
    def download_episode(self, episode: Episode) -> bool:
        """下载剧集"""
        # 检查下载器是否可用
        if hasattr(self.downloader, 'tc') and self.downloader.tc is None:
            self.logger.warning("Transmission客户端不可用，跳过下载")
            return False
        elif hasattr(self.downloader, 'qb') and self.downloader.qb is None:
            self.logger.warning("qBittorrent客户端不可用，跳过下载")
            return False
        
        if episode.download_url.startswith('magnet:'):
            return self.downloader.add_magnet(episode.download_url)
        else:
            # 假设是torrent文件链接
            return self.downloader.add_torrent(episode.download_url)
    
    def get_download_status(self, episode_id: str) -> Dict[str, Any]:
        """获取剧集下载状态"""
        # 检查下载器是否可用
        if hasattr(self.downloader, 'tc') and self.downloader.tc is None:
            self.logger.warning("Transmission客户端不可用，无法获取下载状态")
            return {}
        elif hasattr(self.downloader, 'qb') and self.downloader.qb is None:
            self.logger.warning("qBittorrent客户端不可用，无法获取下载状态")
            return {}
        
        return self.downloader.get_download_status(episode_id)
    
    def pause_download(self, episode_id: str) -> bool:
        """暂停剧集下载"""
        # 检查下载器是否可用
        if hasattr(self.downloader, 'tc') and self.downloader.tc is None:
            self.logger.warning("Transmission客户端不可用，无法暂停下载")
            return False
        elif hasattr(self.downloader, 'qb') and self.downloader.qb is None:
            self.logger.warning("qBittorrent客户端不可用，无法暂停下载")
            return False
        
        return self.downloader.pause_download(episode_id)
    
    def resume_download(self, episode_id: str) -> bool:
        """恢复剧集下载"""
        # 检查下载器是否可用
        if hasattr(self.downloader, 'tc') and self.downloader.tc is None:
            self.logger.warning("Transmission客户端不可用，无法恢复下载")
            return False
        elif hasattr(self.downloader, 'qb') and self.downloader.qb is None:
            self.logger.warning("qBittorrent客户端不可用，无法恢复下载")
            return False
        
        return self.downloader.resume_download(episode_id)
    
    def remove_download(self, episode_id: str, delete_files: bool = False) -> bool:
        """移除剧集下载"""
        # 检查下载器是否可用
        if hasattr(self.downloader, 'tc') and self.downloader.tc is None:
            self.logger.warning("Transmission客户端不可用，无法移除下载")
            return False
        elif hasattr(self.downloader, 'qb') and self.downloader.qb is None:
            self.logger.warning("qBittorrent客户端不可用，无法移除下载")
            return False
        
        return self.downloader.remove_download(episode_id, delete_files)