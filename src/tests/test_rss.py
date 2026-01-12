import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import List

from ani_bot.rss import RSSParseTask, fetch_rss_feed, fetch_all_rss, parse_torrent


@pytest.fixture
def mock_downloader():
    """创建mock的BTDownloader"""
    downloader = Mock()
    downloader.add_torrent = AsyncMock(return_value=True)
    return downloader


@pytest.fixture
def sample_rss_content():
    """示例RSS内容"""
    return '''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>Test RSS Feed</title>
<link>https://test.com</link>
<description>Test feed</description>
<item>
<title>[Test] Anime Title - 01</title>
<link>https://test.com/torrent1.torrent</link>
<enclosure url="https://test.com/torrent1.torrent" type="application/x-bittorrent"/>
</item>
<item>
<title>[Test] Anime Title - 02</title>
<link>https://test.com/torrent2.torrent</link>
<enclosure url="https://test.com/torrent2.torrent" type="application/x-bittorrent"/>
</item>
</channel>
</rss>'''


class TestRSSParseTask:
    
    @pytest.mark.asyncio
    async def test_execute_with_valid_data(self, mock_downloader, sample_rss_content):
        """测试正常执行流程"""
        # 准备mock数据
        async def mock_get_rss_sources():
            return ["https://test.com/rss"]
        
        # mock fetch_all_rss函数返回示例内容
        with patch('ani_bot.rss.fetch_all_rss', return_value=[sample_rss_content]):
            # 创建任务实例
            task = RSSParseTask(mock_get_rss_sources, mock_downloader)
            
            # 执行任务
            await task.execute()
            
            # 验证downloader被正确调用
            assert mock_downloader.add_torrent.call_count == 2
            mock_downloader.add_torrent.assert_any_call("https://test.com/torrent1.torrent")
            mock_downloader.add_torrent.assert_any_call("https://test.com/torrent2.torrent")
    
    @pytest.mark.asyncio
    async def test_execute_with_empty_rss_sources(self, mock_downloader):
        """测试RSS源为空的情况"""
        async def mock_get_rss_sources():
            return []  # 返回空列表
        
        task = RSSParseTask(mock_get_rss_sources, mock_downloader)
        
        # 执行任务
        await task.execute()
        
        # 验证downloader没有被调用
        mock_downloader.add_torrent.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_with_no_torrents(self, mock_downloader):
        """测试解析不到torrent的情况"""
        async def mock_get_rss_sources():
            return ["https://test.com/rss"]
        
        # mock空的RSS内容（不包含torrent链接）
        empty_rss = '''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>Empty RSS</title>
</channel>
</rss>'''
        
        with patch('ani_bot.rss.fetch_all_rss', return_value=[empty_rss]):
            task = RSSParseTask(mock_get_rss_sources, mock_downloader)
            await task.execute()
            
            # 验证downloader没有被调用
            mock_downloader.add_torrent.assert_not_called()


class TestFetchFunctions:
    
    @pytest.mark.asyncio
    async def test_fetch_rss_feed_success(self):
        """测试成功获取RSS feed"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<rss>test content</rss>"
        
        mock_session = Mock()
        # 正确mock异步上下文管理器
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock()
        
        result = await fetch_rss_feed(mock_session, "https://test.com/rss")
        assert result == "<rss>test content</rss>"
    
    @pytest.mark.asyncio
    async def test_fetch_rss_feed_failure(self):
        """测试获取RSS feed失败"""
        mock_response = AsyncMock()
        mock_response.status = 404
        
        mock_session = Mock()
        # 正确mock异步上下文管理器
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock()
        
        result = await fetch_rss_feed(mock_session, "https://test.com/rss")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_all_rss_success(self):
        """测试批量获取RSS成功情况"""
        urls = ["https://test1.com/rss", "https://test2.com/rss"]
        
        # mock fetch_rss_feed函数
        with patch('ani_bot.rss.fetch_rss_feed') as mock_fetch:
            mock_fetch.side_effect = ["content1", "content2"]  # 两个都成功
            
            # mock aiohttp session
            with patch('aiohttp.ClientSession'):
                result = await fetch_all_rss(urls)
                
                # 验证结果
                assert result == ["content1", "content2"]
    
    @pytest.mark.asyncio
    async def test_fetch_all_rss_with_failures(self):
        """测试批量获取RSS包含失败情况"""
        urls = ["https://test1.com/rss", "https://test2.com/rss", "https://test3.com/rss"]
        
        # mock fetch_rss_feed函数，模拟部分失败
        with patch('ani_bot.rss.fetch_rss_feed') as mock_fetch:
            mock_fetch.side_effect = ["content1", None, "content3"]  # 第二个失败
            
            # mock aiohttp session
            with patch('aiohttp.ClientSession'):
                result = await fetch_all_rss(urls)
                
                # 验证结果过滤了None值
                assert result == ["content1", "content3"]


class TestParseTorrent:
    
    def test_parse_torrent_success(self, sample_rss_content):
        """测试成功解析torrent链接"""
        torrents = parse_torrent(sample_rss_content)
        assert len(torrents) == 2
        assert "https://test.com/torrent1.torrent" in torrents
        assert "https://test.com/torrent2.torrent" in torrents
    
    def test_parse_torrent_invalid_xml(self):
        """测试解析无效XML"""
        invalid_xml = "invalid xml content"
        
        with pytest.raises(Exception):  # ET.fromstring会抛出异常
            parse_torrent(invalid_xml)
    
    def test_parse_torrent_no_channel(self):
        """测试缺少channel标签的RSS"""
        no_channel_rss = '''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
</rss>'''
        
        with pytest.raises(ValueError, match="Invalid RSS: no <channel> found"):
            parse_torrent(no_channel_rss)


if __name__ == "__main__":
    # 可以直接运行测试
    pytest.main([__file__, "-v"])