import argparse
import requests
import json
from typing import Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ani_bot.core.config import settings


class AniBotCLI:
    """Ani-Bot CLI客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.API_BASE_URL
        
    
    def list_rss(self, skip: int = 0, limit: int = 100):
        """获取RSS列表"""
        url = f"{self.base_url}/rss"
        params = {"skip": skip, "limit": limit}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取RSS列表失败: {e}")
            return None
    
    def get_rss(self, rss_id: int):
        """根据ID获取RSS"""
        url = f"{self.base_url}/rss/{rss_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取RSS失败: {e}")
            return None
    
    def create_rss(self, rss_data: dict):
        """创建RSS"""
        url = f"{self.base_url}/rss"
        try:
            response = requests.post(url, json=rss_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"创建RSS失败: {e}")
            return None
    
    def update_rss(self, rss_id: int, rss_data: dict):
        """更新RSS"""
        url = f"{self.base_url}/rss/{rss_id}"
        try:
            response = requests.put(url, json=rss_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"更新RSS失败: {e}")
            return None
    
    def delete_rss(self, rss_id: int):
        """删除RSS"""
        url = f"{self.base_url}/rss/{rss_id}"
        try:
            response = requests.delete(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"删除RSS失败: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Ani-Bot CLI 客户端")
    parser.add_argument('--base-url', default=None, help='API基础URL')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # RSS 相关命令
    rss_parser = subparsers.add_parser('rss', help='RSS管理命令')
    rss_subparsers = rss_parser.add_subparsers(dest='rss_action', help='RSS操作')
    
    # 列出RSS
    list_parser = rss_subparsers.add_parser('list', help='列出RSS')
    list_parser.add_argument('--skip', type=int, default=0, help='跳过的条目数')
    list_parser.add_argument('--limit', type=int, default=100, help='限制返回的条目数')
    
    # 获取RSS详情
    get_parser = rss_subparsers.add_parser('get', help='获取RSS详情')
    get_parser.add_argument('id', type=int, help='RSS ID')
    
    # 创建RSS
    create_parser = rss_subparsers.add_parser('create', help='创建RSS')
    create_parser.add_argument('--title', required=True, help='RSS标题')
    create_parser.add_argument('--link', required=True, help='RSS链接')
    create_parser.add_argument('--description', help='RSS描述')
    create_parser.add_argument('--rss-feed-id', type=int, default=0, help='RSS源ID')
    create_parser.add_argument('--torrent-url', help='种子URL')
    create_parser.add_argument('--magnet-link', help='磁力链接')
    create_parser.add_argument('--guid', help='全局唯一标识符')
    
    # 更新RSS
    update_parser = rss_subparsers.add_parser('update', help='更新RSS')
    update_parser.add_argument('id', type=int, help='RSS ID')
    update_parser.add_argument('--title', help='RSS标题')
    update_parser.add_argument('--link', help='RSS链接')
    update_parser.add_argument('--description', help='RSS描述')
    update_parser.add_argument('--rss-feed-id', type=int, help='RSS源ID')
    update_parser.add_argument('--torrent-url', help='种子URL')
    update_parser.add_argument('--magnet-link', help='磁力链接')
    update_parser.add_argument('--guid', help='全局唯一标识符')
    
    # 删除RSS
    delete_parser = rss_subparsers.add_parser('delete', help='删除RSS')
    delete_parser.add_argument('id', type=int, help='RSS ID')
    
    args = parser.parse_args()
    
    cli = AniBotCLI(base_url=args.base_url)
    
    if args.command == 'rss':
        if args.rss_action == 'list':
            result = cli.list_rss(skip=args.skip, limit=args.limit)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.rss_action == 'get':
            result = cli.get_rss(args.id)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.rss_action == 'create':
            rss_data = {
                "title": args.title,
                "link": args.link,
                "description": args.description or "",
                "rss_feed_id": args.rss_feed_id,
                "torrent_url": args.torrent_url or "",
                "magnet_link": args.magnet_link or "",
                "guid": args.guid or ""
            }
            # 过滤掉空值
            rss_data = {k: v for k, v in rss_data.items() if v is not None}
            result = cli.create_rss(rss_data)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.rss_action == 'update':
            rss_data = {}
            if args.title is not None:
                rss_data["title"] = args.title
            if args.link is not None:
                rss_data["link"] = args.link
            if args.description is not None:
                rss_data["description"] = args.description
            if args.rss_feed_id is not None:
                rss_data["rss_feed_id"] = args.rss_feed_id
            if args.torrent_url is not None:
                rss_data["torrent_url"] = args.torrent_url
            if args.magnet_link is not None:
                rss_data["magnet_link"] = args.magnet_link
            if args.guid is not None:
                rss_data["guid"] = args.guid
            
            result = cli.update_rss(args.id, rss_data)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.rss_action == 'delete':
            result = cli.delete_rss(args.id)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()