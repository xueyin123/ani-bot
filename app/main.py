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
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import config
from app.scheduler.task_scheduler import TaskScheduler
from app.utils.logger import get_logger
from app.models.anime import AnimeDatabase, Anime


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
    
    def start(self):
        """启动Ani-Bot"""
        self.logger.info("正在启动Ani-Bot...")
        
        # 启动调度器
        self.scheduler.start()
        
        self.running = True
        self.logger.info("Ani-Bot已启动并运行")
        
        # 保持主程序运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("接收到键盘中断，正在关闭Ani-Bot...")
            self.stop()
    
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
    bot = AniBot()
    
    # 示例：添加一些动漫到跟踪列表
    # bot.add_anime("鬼灭之刃", "https://bgm.tv/subject/292185")
    # bot.add_anime("我的英雄学院", "https://bgm.tv/subject/208912")
    
    # 启动Ani-Bot
    bot.start()


if __name__ == "__main__":
    main()