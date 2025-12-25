#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ani-Bot: 自动追番工具
部署在NAS上，可以在后台爬取动漫，然后使用BT下载
"""

import os
import sys
import signal
import time
import threading
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ani_bot.config.settings import config
from ani_bot.scheduler.task_scheduler import TaskScheduler
from ani_bot.utils.logger import get_logger
from ani_bot.models import AnimeDatabase, Anime


class AniBot:
    """Ani-Bot主程序"""
    
    def __init__(self):
        self.config = config
        self.logger = get_logger('AniBot', config)
        self.scheduler = TaskScheduler(config)
        self.db = AnimeDatabase(config.get('database.path', './data/anime.db'))
        self.running = False
        
        # 注册信号处理器，用于优雅关闭
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器，用于优雅关闭"""
        self.logger.info(f"接收到信号 {signum}，正在关闭Ani-Bot...")
        self.stop()
        sys.exit(0)
    
    def start(self, api_host: str = "0.0.0.0", api_port: int = 8000):
        """启动Ani-Bot"""
        self.logger.info("正在启动Ani-Bot...")
            
        # 启动调度器
        self.scheduler.start()
            
        # 如果需要，启动API服务
        self.start_api(api_host, api_port)
            
        
    def start_api(self, host: str = "0.0.0.0", port: int = 8000):
        """启动API服务"""
        from ani_bot.api.api import app
        import uvicorn
            
        self.logger.info(f"正在启动API服务，地址: {host}:{port}")
        uvicorn.run(app, host=host, port=port)
        
    def stop(self):
        """停止Ani-Bot"""
        self.logger.info("正在停止Ani-Bot...")
            
        # 停止调度器
        self.scheduler.stop()
            
        self.running = False
        self.logger.info("Ani-Bot已停止")
    
    def add_anime(self, name: str, source_url: str = ""):
        """添加动漫到跟踪列表"""
        anime = Anime(
            name=name,
            source_url=source_url
        )
        
        anime_id = self.scheduler.add_anime_to_track(anime)
        if anime_id:
            self.logger.info(f"已添加动漫到跟踪列表: {name}, ID: {anime_id}")
            return anime_id
        else:
            self.logger.error(f"添加动漫失败: {name}")
            return None
    
    def remove_anime(self, anime_id: int):
        """从跟踪列表移除动漫"""
        self.scheduler.remove_anime_from_track(anime_id)
        self.logger.info(f"已从跟踪列表移除动漫，ID: {anime_id}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ani-Bot: 自动追番工具')
    parser.add_argument('--api-host', default='0.0.0.0', help='API服务主机地址')
    parser.add_argument('--api-port', type=int, default=8000, help='API服务端口')
    
    args = parser.parse_args()
    
    bot = AniBot()
    
    # 启动Ani-Bot
    bot.start(api_host=args.api_host, api_port=args.api_port)


if __name__ == "__main__":
    main()