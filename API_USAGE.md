# Ani-Bot API 和 CLI 使用说明

## API 接口

Ani-Bot 提供了基于 FastAPI 的 RESTful API 接口，用于管理动漫信息。

### 启动 API 服务

```bash
# 启动包含API服务的Ani-Bot
python -m ani_bot.main --api --api-port 8000

# 指定不同端口
python -m ani_bot.main --api --api-port 8080
```

### API 端点

#### 获取所有动漫
- **GET** `/anime`
- 获取数据库中所有动漫的列表

#### 获取特定动漫
- **GET** `/anime/{anime_id}`
- 根据ID获取特定动漫信息

#### 搜索动漫
- **GET** `/anime/search?keyword={keyword}`
- 根据关键词搜索动漫（名称或原始名称）

#### 添加动漫
- **POST** `/anime`
- 请求体: 
```json
{
  "name": "动漫名称",
  "original_name": "原始名称",
  "season": 1,
  "episode": 0,
  "total_episodes": 12,
  "status": "ongoing",
  "description": "描述",
  "cover_image_url": "封面图片URL",
  "source_url": "源URL",
  "download_status": "pending",
  "download_path": "下载路径"
}
```

#### 更新动漫
- **PUT** `/anime/{anime_id}`
- 请求体（只包含需要更新的字段）:
```json
{
  "name": "新名称",
  "episode": 5,
  "status": "finished"
}
```

#### 删除动漫
- **DELETE** `/anime/{anime_id}`
- 根据ID删除动漫及其相关剧集

## CLI 客户端

Ani-Bot 提供了命令行客户端来操作 API 服务。

### 使用方法

```bash
# 指定API服务地址
python -m ani_bot.cli.client --base-url http://localhost:8000 [command] [options]
```

### 命令列表

#### 列出所有动漫
```bash
python -m ani_bot.cli.client --base-url http://localhost:8000 list
```

#### 获取特定动漫
```bash
python -m ani_bot.cli.client --base-url http://localhost:8000 get 1
```

#### 添加动漫
```bash
python -m ani_bot.cli.client --base-url http://localhost:8000 add \
  --name "动漫名称" \
  --original-name "原始名称" \
  --season 1 \
  --total-episodes 12 \
  --status ongoing \
  --description "描述"
```

#### 更新动漫
```bash
python -m ani_bot.cli.client --base-url http://localhost:8000 update 1 \
  --episode 5 \
  --status finished
```

#### 删除动漫
```bash
python -m ani_bot.cli.client --base-url http://localhost:8000 delete 1
```

#### 搜索动漫
```bash
python -m ani_bot.cli.client --base-url http://localhost:8000 search "关键词"
```

## 依赖安装

需要安装以下额外依赖：

```bash
pip install fastapi uvicorn
```

这些依赖已添加到 requirements.txt 文件中。