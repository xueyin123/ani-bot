import asyncio
from typing import Awaitable, Callable, List
import aiohttp
import xml.etree.ElementTree as ET
from ani_bot.downloader.bt_downloader import BTDownloader, QBittorrentDownloader


async def fetch_rss_feed(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Failed to fetch {url}, status: {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def fetch_all_rss(urls):
    """
    下载rss源
    
    :param urls: rss源列表
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rss_feed(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]  # 过滤失败的

def parse_torrent(data: str):
        """
        mikan 的rss解析
        TODO: 支持更多rss源
        """
        torrent_list = []

        root = ET.fromstring(data)
        channel = root.find('channel')
        title = channel.find('title')
        description = channel.find('description')
        print(f"Title: {title.text}")
        print(f"Description: {description.text}")

        for item in channel.findall('item'):
            title = item.find('title')
            print(f"Title: {title.text}")
            enclosure = item.find('enclosure')
            url = enclosure.attrib['url']
            torrent_list.append(url)
        return torrent_list
            

class RSSTask:
    def __init__(self,
                 get_rss_sources: Callable[[], Awaitable[List[str]]],
                 downloader: BTDownloader
        ):

        self.get_rss_sources = get_rss_sources
        self.downloader = downloader

    async def execute(self):
        rss_urls = await self.get_rss_sources()
        if not rss_urls:
            return

        rss_contents = await fetch_all_rss(rss_urls)
        
        all_torrents = []
        for rss in rss_contents:
            torrents = parse_torrent(rss)
            all_torrents.extend(torrents)

        if not all_torrents:
            return
        
        tasks = [self.downloader.add_torrent(torrent) for torrent in all_torrents]
        await asyncio.gather(*tasks)