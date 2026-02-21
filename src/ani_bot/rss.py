import asyncio
from datetime import datetime
from typing import Awaitable, Callable, List, Tuple
import aiohttp
import xml.etree.ElementTree as ET
from ani_bot.db.models import Anime, Episode, Torrent
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
        
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                if result is not None:
                    yield result  # 完成一个立即产出
            except Exception as e:
                print(f"任务失败: {e}")
                continue

def parse_torrent(data: str) -> Tuple[Anime, List[Episode], List[Torrent]]:
    """
    mikan 的rss解析
    TODO: 支持更多rss源
    """
    torrent_list = []
    episode_list = []

    root = ET.fromstring(data)
    channel = root.find('channel')
    if channel is None:
        raise ValueError("Invalid RSS: no <channel> found")
    
    anime_title = channel.find('title')
    anime_title_text = (anime_title.text if anime_title is not None else "") or ""
    anime_description = channel.find('description')
    anime_description_text = (anime_description.text if anime_description is not None else "") or ""

    anime = Anime(original_title=anime_title_text, description=anime_description_text)

    # 定义命名空间
    namespaces = {'torrent': 'https://mikanime.tv/0.1/'}

    for item in channel.findall('item'):
        episode_title = item.find('title')
        episode_title_text = (episode_title.text if episode_title is not None else "") or ""
        episode = Episode(original_title=episode_title_text)
        episode_list.append(episode)
    
        # 从 <torrent> 标签中获取信息
        torrent_elem = item.find('torrent:torrent', namespaces)
        torrent_url = ""
        size = 0
        publish_date = None
        
        if torrent_elem is not None:
            # 获取 torrent 链接
            torrent_link = torrent_elem.find('torrent:link', namespaces)
            if torrent_link is not None and torrent_link.text:
                torrent_url = torrent_link.text
        
        # 如果 <torrent> 中没有链接，回退到 <enclosure> 中的链接
        if not torrent_url:
            enclosure = item.find('enclosure')
            if enclosure is not None and 'url' in enclosure.attrib:
                torrent_url = enclosure.attrib['url']
        
        # 解析 contentLength
        if torrent_elem is not None:
            content_length = torrent_elem.find('torrent:contentLength', namespaces)
            if content_length is not None and content_length.text:
                try:
                    size = int(content_length.text)
                except ValueError:
                    pass
        
        # 解析 pubDate
        if torrent_elem is not None:
            pub_date = torrent_elem.find('torrent:pubDate', namespaces)
            if pub_date is not None and pub_date.text:
                try:
                    publish_date = datetime.fromisoformat(pub_date.text)
                except ValueError:
                    pass
        
        torrent = Torrent(
            torrent_url=torrent_url,
            size=size,
            publish_date=publish_date
        )
        torrent_list.append(torrent)

    return anime, episode_list, torrent_list



class RSSParseTask:
    """
    rss解析任务
    TODO: 解析ani元数据、解析torrent文件
    TODO: 将解析添加到数据库,分为RSS解析任务和 rss下载任务
    """

    def __init__(self,
                 get_rss_sources: Callable[[], Awaitable[List[str]]],
                 save_parse_result: Callable[[Anime, List[Episode], List[Torrent]], Awaitable[None]]
        ):

        self.get_rss_sources = get_rss_sources
        self.save_parse_result = save_parse_result  

    async def run(self):
        rss_urls = await self.get_rss_sources()
        if not rss_urls:
            return

        async for result in fetch_all_rss(rss_urls):
            if result is not None:
                try:
                    anime, episode_list, torrent_list = parse_torrent(result)
                    await self.save_parse_result(anime, episode_list, torrent_list)
                except Exception as e:
                    print(f"解析失败: {e}")
                    continue