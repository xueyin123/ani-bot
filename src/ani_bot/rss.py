import asyncio
from typing import Awaitable, Callable, List, Tuple
import aiohttp
import xml.etree.ElementTree as ET
from ani_bot.downloader.bt_downloader import BTDownloader


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
    TODO: 限流处理
    TODO: 错误重试
    :param urls: rss源列表
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rss_feed(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]  # 过滤失败的

def parse_torrent(data: str) -> Tuple[List[str], List[str], List[str]]:
    """
    mikan 的rss解析
    TODO: 支持更多rss源
    """
    torrent_list = []
    anime_list = []
    episode_list = []

    root = ET.fromstring(data)
    channel = root.find('channel')
    if channel is None:
        raise ValueError("Invalid RSS: no <channel> found")
    
    anime_title = channel.find('title')
    anime_title_text = anime_title.text if anime_title is not None else ""
    anime_description = channel.find('description')
    anime_description_text = anime_description.text if anime_description is not None else ""
    print(f"Title: {anime_title_text}")
    print(f"Description: {anime_description_text}")

    for item in channel.findall('item'):
        episode_title = item.find('title')
        episode_title_text = episode_title.text if episode_title is not None else ""
        episode_description = item.find('description')
        episode_description_text = episode_description.text if episode_description is not None else ""
        print(f"Title: {episode_title_text}")
        enclosure = item.find('enclosure')
        url = enclosure.attrib['url'] if enclosure is not None else ""
        torrent_list.append(url)

    return torrent_list, anime_list, episode_list



class RSSParseTask:
    """
    rss解析任务
    TODO: 解析ani元数据、解析torrent文件
    TODO: 将解析添加到数据库,分为RSS解析任务和 rss下载任务
    """

    def __init__(self,
                 get_rss_sources: Callable[[], Awaitable[List[str]]],
                 downloader: BTDownloader
        ):

        self.get_rss_sources = get_rss_sources
        self.downloader = downloader

    async def run(self):
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