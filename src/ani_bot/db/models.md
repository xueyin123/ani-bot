# RSS 示例

## mikan

```xml
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
    <channel>
        <title>Mikan Project - 古诺希亚</title>
        <link>http://mikanime.tv/RSS/Bangumi?bangumiId=3780&amp;subgroupid=583</link>
        <description>Mikan Project - 古诺希亚</description>
        <item>
            <guid isPermaLink="false">[ANi] GNOSIA / GNOSIA - 13 [1080P][Baha][WEB-DL][AAC
                AVC][CHT][MP4]</guid>
            <link>https://mikanime.tv/Home/Episode/796d92943aed09fa4a417e73b3e5afc4cb63d6ba</link>
            <title>[ANi] GNOSIA / GNOSIA - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]</title>
            <description>[ANi] GNOSIA / GNOSIA - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4][461.1
                MB]</description>
            <torrent xmlns="https://mikanime.tv/0.1/">
                <link>https://mikanime.tv/Home/Episode/796d92943aed09fa4a417e73b3e5afc4cb63d6ba</link>
                <contentLength>483498400</contentLength>
                <pubDate>2026-01-11T00:31:24.196106</pubDate>
            </torrent>
            <enclosure type="application/x-bittorrent" length="483498400"
                url="https://mikanime.tv/Download/20260111/796d92943aed09fa4a417e73b3e5afc4cb63d6ba.torrent" />
        </item>
    </channel>
</rss>
```



# 功能模块

## RSS 模块

1. 管理 rss 订阅源
2. 定期拉取 rss 数据
3. 解析 rss ，解析出以下内容
   1. Anime 动漫数据
   2. Episode 剧集数据
   3. Torrent 种子数据



### rss 解析模块

title 示例

```
[ANi] GNOSIA / GNOSIA - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]
```

1. 从 title 里解析出元数据，可以自定义解析规则
   1. 动漫名称
   2. 集数
   3. 画质

2. 从 imdb 匹配动漫（可选）

## Anime 模块

1. 管理 Anime 数据
   1. 管理 anime 元数据 （可选）
2. 管理 Episode 数据
   1. 管理 Episode 元数据（可选）



## Torrent 模块

1. 管理 Torrent 数据
2. 调用bt下载器进行下载



