import requests
import json

# 测试创建 RSS 项目
url = "http://localhost:8080/api/v1/rss"
headers = {"Content-Type": "application/json"}

data = {
    "title": "Test RSS",
    "link": "http://example.com",
    "description": "Test RSS Description", 
    "torrent_url": "http://example.com/test.torrent",
    "guid": "test-guid-123"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code != 200:
        print(f"Headers: {response.headers}")
except Exception as e:
    print(f"Error: {e}")