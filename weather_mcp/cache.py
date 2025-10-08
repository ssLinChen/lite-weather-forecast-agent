"""
内存缓存实现
"""

import time
from cachetools import TTLCache
from typing import Any, Optional
from weather_mcp.models import Language


class WeatherCache:
    """天气数据内存缓存"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 600):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存生存时间（秒），默认10分钟
        """
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)
    
    def get_cache_key(self, city: str, lang: Language) -> str:
        """生成缓存键"""
        return f"{city.lower()}:{lang.value}"
    
    def get(self, city: str, lang: Language) -> Optional[Any]:
        """从缓存获取数据"""
        key = self.get_cache_key(city, lang)
        return self.cache.get(key)
    
    def set(self, city: str, lang: Language, data: Any) -> None:
        """设置缓存数据"""
        key = self.get_cache_key(city, lang)
        self.cache[key] = data
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        return {
            "current_size": len(self.cache),
            "max_size": self.cache.maxsize,
            "ttl": self.cache.ttl
        }