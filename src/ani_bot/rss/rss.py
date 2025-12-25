import requests
import xml.etree.ElementTree as ET
from hmac import new
from ani_bot.downloader.bt_downloader import QBittorrentDownloader


class RSSFetcher():

    def __init__(self) -> None:
        self.rss_list = []

    def add_rss(self, url: str):
        self.rss_list.append(url)

    def fetch_all(self):
        rss_contents = []
        for url in self.rss_list:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    rss_contents.append(response.text)
                else:
                    print(f"Failed to fetch RSS from {url}, status code: {response.status_code}")
            except Exception as e:
                print(f"Error fetching RSS from {url}: {e}")
        return rss_contents

class RSSParser():
    def __init__(self) -> None:
        pass

    def parse_torrent(self, data: str):
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
            

if __name__ == '__main__':
    fetcher = RSSFetcher()
    fetcher.add_rss('https://mikanani.me/RSS/Bangumi?bangumiId=3736&subgroupid=583')
    rss_list = fetcher.fetch_all()

    parser = RSSParser()
    config = {
        'qbittorrent.host': '192.168.31.88',
        'qbittorrent.port': 8085,
        'qbittorrent.username': 'admin',
        'qbittorrent.password': 'adminadmin'
    }
    downloader = QBittorrentDownloader(config)

    for rss in rss_list:
        torrent_list = parser.parse_torrent(rss)
        for torrent in torrent_list:
            downloader.add_torrent(torrent)