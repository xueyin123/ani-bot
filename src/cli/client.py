import argparse
import requests
import json
from typing import Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ani_bot.config.settings import config


class AniBotCLI:
    """Ani-Bot CLI客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.get('api.base_url', 'http://localhost:8000')
        
    def list_anime(self):
        """列出所有动漫"""
        try:
            response = requests.get(f"{self.base_url}/anime")
            if response.status_code == 200:
                animes = response.json()
                if not animes:
                    print("没有找到动漫记录")
                    return
                
                print(f"找到 {len(animes)} 个动漫:")
                print("-" * 80)
                for anime in animes:
                    print(f"ID: {anime['id']}")
                    print(f"名称: {anime['name']}")
                    print(f"原始名称: {anime['original_name']}")
                    print(f"季数: {anime['season']}")
                    print(f"当前集数: {anime['episode']}/{anime['total_episodes']}")
                    print(f"状态: {anime['status']}")
                    print(f"下载状态: {anime['download_status']}")
                    print(f"更新时间: {anime['last_updated']}")
                    print("-" * 80)
            else:
                print(f"获取动漫列表失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    def get_anime(self, anime_id: int):
        """获取特定动漫信息"""
        try:
            response = requests.get(f"{self.base_url}/anime/{anime_id}")
            if response.status_code == 200:
                anime = response.json()
                print("动漫信息:")
                print(f"  ID: {anime['id']}")
                print(f"  名称: {anime['name']}")
                print(f"  原始名称: {anime['original_name']}")
                print(f"  季数: {anime['season']}")
                print(f"  当前集数: {anime['episode']}/{anime['total_episodes']}")
                print(f"  首播日期: {anime['air_date']}")
                print(f"  状态: {anime['status']}")
                print(f"  下载状态: {anime['download_status']}")
                print(f"  描述: {anime['description']}")
                print(f"  封面URL: {anime['cover_image_url']}")
                print(f"  源URL: {anime['source_url']}")
                print(f"  更新时间: {anime['last_updated']}")
            elif response.status_code == 404:
                print(f"动漫ID {anime_id} 不存在")
            else:
                print(f"获取动漫信息失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    def add_anime(self, name: str, original_name: str = "", season: int = 1, 
                  episode: int = 0, total_episodes: int = 0, status: str = "ongoing", 
                  description: str = "", cover_image_url: str = "", 
                  source_url: str = "", download_status: str = "pending", 
                  download_path: str = ""):
        """添加动漫"""
        try:
            anime_data = {
                "name": name,
                "original_name": original_name,
                "season": season,
                "episode": episode,
                "total_episodes": total_episodes,
                "status": status,
                "description": description,
                "cover_image_url": cover_image_url,
                "source_url": source_url,
                "download_status": download_status,
                "download_path": download_path
            }
            
            response = requests.post(f"{self.base_url}/anime", json=anime_data)
            if response.status_code == 200:
                anime = response.json()
                print(f"成功添加动漫: {anime['name']} (ID: {anime['id']})")
            elif response.status_code == 400:
                print(f"添加失败: {response.json().get('detail', '未知错误')}")
            else:
                print(f"添加动漫失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    def update_anime(self, anime_id: int, name: str = None, original_name: str = None, 
                     season: int = None, episode: int = None, total_episodes: int = None, 
                     status: str = None, description: str = None, 
                     cover_image_url: str = None, source_url: str = None, 
                     download_status: str = None, download_path: str = None):
        """更新动漫信息"""
        try:
            # 先获取当前动漫信息
            response = requests.get(f"{self.base_url}/anime/{anime_id}")
            if response.status_code != 200:
                print(f"动漫ID {anime_id} 不存在")
                return
            
            current_anime = response.json()
            
            # 准备更新数据，只更新提供的字段
            update_data = {k: v for k, v in {
                "name": name,
                "original_name": original_name,
                "season": season,
                "episode": episode,
                "total_episodes": total_episodes,
                "status": status,
                "description": description,
                "cover_image_url": cover_image_url,
                "source_url": source_url,
                "download_status": download_status,
                "download_path": download_path
            }.items() if v is not None}
            
            # 保持未更新的字段
            for key in ['id', 'last_updated', 'next_air_date', 'air_date']:
                if key in current_anime:
                    update_data[key] = current_anime[key]
            
            response = requests.put(f"{self.base_url}/anime/{anime_id}", json=update_data)
            if response.status_code == 200:
                anime = response.json()
                print(f"成功更新动漫: {anime['name']} (ID: {anime['id']})")
            elif response.status_code == 404:
                print(f"动漫ID {anime_id} 不存在")
            else:
                print(f"更新动漫失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    def delete_anime(self, anime_id: int):
        """删除动漫"""
        try:
            response = requests.delete(f"{self.base_url}/anime/{anime_id}")
            if response.status_code == 200:
                print(f"成功删除动漫ID {anime_id}")
            elif response.status_code == 404:
                print(f"动漫ID {anime_id} 不存在")
            else:
                print(f"删除动漫失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    def search_anime(self, keyword: str):
        """搜索动漫"""
        try:
            response = requests.get(f"{self.base_url}/anime/search", params={"keyword": keyword})
            if response.status_code == 200:
                animes = response.json()
                if not animes:
                    print(f"没有找到包含 '{keyword}' 的动漫")
                    return
                
                print(f"找到 {len(animes)} 个匹配的动漫:")
                print("-" * 80)
                for anime in animes:
                    print(f"ID: {anime['id']}")
                    print(f"名称: {anime['name']}")
                    print(f"原始名称: {anime['original_name']}")
                    print(f"季数: {anime['season']}")
                    print(f"当前集数: {anime['episode']}/{anime['total_episodes']}")
                    print(f"状态: {anime['status']}")
                    print("-" * 80)
            else:
                print(f"搜索动漫失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='Ani-Bot CLI客户端')
    parser.add_argument('--base-url', default=None, help='API基础URL (默认: http://localhost:8000)')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出动漫
    list_parser = subparsers.add_parser('list', help='列出所有动漫')
    
    # 获取特定动漫
    get_parser = subparsers.add_parser('get', help='获取特定动漫信息')
    get_parser.add_argument('anime_id', type=int, help='动漫ID')
    
    # 添加动漫
    add_parser = subparsers.add_parser('add', help='添加新动漫')
    add_parser.add_argument('--name', required=True, help='动漫名称')
    add_parser.add_argument('--original-name', default="", help='原始名称')
    add_parser.add_argument('--season', type=int, default=1, help='季数')
    add_parser.add_argument('--episode', type=int, default=0, help='当前集数')
    add_parser.add_argument('--total-episodes', type=int, default=0, help='总集数')
    add_parser.add_argument('--status', default="ongoing", choices=["ongoing", "finished", "dropped"], help='状态')
    add_parser.add_argument('--description', default="", help='描述')
    add_parser.add_argument('--cover-image-url', default="", help='封面图片URL')
    add_parser.add_argument('--source-url', default="", help='源URL')
    add_parser.add_argument('--download-status', default="pending", choices=["pending", "downloading", "completed", "failed"], help='下载状态')
    add_parser.add_argument('--download-path', default="", help='下载路径')
    
    # 更新动漫
    update_parser = subparsers.add_parser('update', help='更新动漫信息')
    update_parser.add_argument('anime_id', type=int, help='动漫ID')
    update_parser.add_argument('--name', help='动漫名称')
    update_parser.add_argument('--original-name', help='原始名称')
    update_parser.add_argument('--season', type=int, help='季数')
    update_parser.add_argument('--episode', type=int, help='当前集数')
    update_parser.add_argument('--total-episodes', type=int, help='总集数')
    update_parser.add_argument('--status', choices=["ongoing", "finished", "dropped"], help='状态')
    update_parser.add_argument('--description', help='描述')
    update_parser.add_argument('--cover-image-url', help='封面图片URL')
    update_parser.add_argument('--source-url', help='源URL')
    update_parser.add_argument('--download-status', choices=["pending", "downloading", "completed", "failed"], help='下载状态')
    update_parser.add_argument('--download-path', help='下载路径')
    
    # 删除动漫
    delete_parser = subparsers.add_parser('delete', help='删除动漫')
    delete_parser.add_argument('anime_id', type=int, help='动漫ID')
    
    # 搜索动漫
    search_parser = subparsers.add_parser('search', help='搜索动漫')
    search_parser.add_argument('keyword', help='搜索关键词')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = AniBotCLI(args.base_url)
    
    if args.command == 'list':
        client.list_anime()
    elif args.command == 'get':
        client.get_anime(args.anime_id)
    elif args.command == 'add':
        client.add_anime(
            name=args.name,
            original_name=args.original_name,
            season=args.season,
            episode=args.episode,
            total_episodes=args.total_episodes,
            status=args.status,
            description=args.description,
            cover_image_url=args.cover_image_url,
            source_url=args.source_url,
            download_status=args.download_status,
            download_path=args.download_path
        )
    elif args.command == 'update':
        client.update_anime(
            anime_id=args.anime_id,
            name=args.name,
            original_name=args.original_name,
            season=args.season,
            episode=args.episode,
            total_episodes=args.total_episodes,
            status=args.status,
            description=args.description,
            cover_image_url=args.cover_image_url,
            source_url=args.source_url,
            download_status=args.download_status,
            download_path=args.download_path
        )
    elif args.command == 'delete':
        client.delete_anime(args.anime_id)
    elif args.command == 'search':
        client.search_anime(args.keyword)


if __name__ == "__main__":
    main()