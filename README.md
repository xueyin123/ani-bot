# Ani-Bot: 自动追番工具

Ani-Bot是一个自动追番工具，部署在NAS上，可以在后台爬取动漫，然后使用BT下载。

## 功能特性

- 自动爬取动漫信息
- 支持多种BT客户端（Transmission、qBittorrent）
- 定时检查新剧集
- 自动下载新剧集
- 数据库管理动漫和剧集信息
- 日志记录和管理
- 配置文件管理

## 项目结构

```
ani-bot/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      # 配置管理
│   │   └── config.yaml      # 配置文件
│   ├── models/
│   │   ├── __init__.py
│   │   ├── anime.py         # 动漫数据模型
│   │   └── database.py      # 数据库管理
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── base_crawler.py  # 爬虫基类
│   │   ├── bangumi_crawler.py # Bangumi爬虫
│   │   └── subsource_crawler.py # 资源站爬虫
│   ├── downloaders/
│   │   ├── __init__.py
│   │   ├── bt_downloader.py # BT下载器
│   │   └── transmission_client.py # Transmission客户端
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── task_scheduler.py # 任务调度器
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py        # 日志管理
│   │   └── helpers.py       # 辅助函数
│   └── main.py              # 主程序入口
├── tests/
│   ├── __init__.py
│   ├── test_crawlers.py
│   └── test_models.py
├── requirements.txt         # 依赖包
├── README.md
└── .env
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

编辑 `app/config/config.yaml` 文件来配置Ani-Bot的行为：

```yaml
crawler:
  interval_minutes: 30      # 爬取间隔（分钟）
  timeout: 30              # 网络请求超时（秒）
  retry_times: 3           # 重试次数
  user_agent: "Mozilla/5.0..." # 用户代理

download:
  save_path: "./downloads"  # 下载保存路径
  bt_client: "transmission" # BT客户端类型
  max_download_speed: -1    # 最大下载速度（-1为无限制）
  max_upload_speed: -1      # 最大上传速度（-1为无限制）

database:
  type: "sqlite"           # 数据库类型
  path: "./data/anime.db"   # 数据库路径

scheduler:
  check_interval: 1800      # 检查间隔（秒）
  enable_auto_download: true # 是否启用自动下载

logging:
  level: "INFO"            # 日志级别
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/ani_bot.log" # 日志文件路径
```

## 使用方法

1. 安装依赖包
2. 配置 `app/config/config.yaml`
3. 运行主程序:

```bash
python app/main.py
```

## 部署到NAS

可以使用以下方式部署到NAS：

1. 使用Docker容器化部署
2. 使用systemd服务管理
3. 使用supervisor进程管理

## 开发

运行测试:

```bash
python -m pytest tests/
```

## 许可证

MIT License