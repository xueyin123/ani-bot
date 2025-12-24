import os
import yaml
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "ani_bot/config/config.yaml"): 
        self.config_path = config_path
        self.config_data = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # 默认配置
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "crawler": {
                "interval_minutes": 30,
                "timeout": 30,
                "retry_times": 3,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "download": {
                "save_path": "./downloads",
                "bt_client": "transmission",
                "max_download_speed": -1,  # -1 表示无限制
                "max_upload_speed": -1
            },
            "database": {
                "type": "sqlite",
                "path": "./data/anime.db"
            },
            "scheduler": {
                "check_interval": 1800,  # 30分钟
                "enable_auto_download": True
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "./logs/ani_bot.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持嵌套键，如 'crawler.interval_minutes'"""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)


# 全局配置实例
config = Config()