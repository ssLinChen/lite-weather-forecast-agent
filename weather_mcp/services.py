"""
天气查询业务逻辑服务
"""

import logging
import os
from typing import Optional
from weather_mcp.models import WeatherResponse, Language, ErrorResponse
from weather_mcp.clients.heweather_api import HeWeatherClient, MockWeatherClient
from weather_mcp.cache import WeatherCache
from utils.encoding_service import ProfessionalEncodingService


class WeatherService:
    """天气查询服务 - 支持多数据源回退"""
    
    def __init__(self):
        self.primary_client = HeWeatherClient()
        self.mock_client = MockWeatherClient()
        self.cache = WeatherCache()
        self.logger = logging.getLogger(__name__)
        self.use_mock_data = False
        self.encoding_service = ProfessionalEncodingService()
        self.encoding_service.set_logger(self.logger)
        
        # 检查API密钥可用性
        self._check_api_keys()
    
    def _check_api_keys(self):
        """检查API密钥可用性"""
        bearer_token = os.getenv("WEATHER_API_BEARER_TOKEN", "")
        
        if not bearer_token:
            self.logger.warning("未检测到有效的Bearer Token，启用模拟数据模式")
            self.use_mock_data = True
    
    def get_weather(self, city: str, lang: Language = Language.EN) -> WeatherResponse:
        """
        获取城市天气信息 - 支持多数据源回退
        
        Args:
            city: 城市名称
            lang: 语言类型
            
        Returns:
            WeatherResponse: 天气响应数据
        """
        # 使用专业编码修复服务处理乱码问题
        original_city = city
        city = self.encoding_service.fix_text(city)
        
        if city != original_city:
            self.logger.info(f"专业编码修复: '{original_city}' -> '{city}'")
        
        self.logger.info(f"查询天气: city={city}, lang={lang.value}")
        
        # 检查缓存
        cached_data = self.cache.get(city, lang)
        if cached_data:
            self.logger.info(f"从缓存获取 {city} 天气数据")
            return cached_data
        
        # 如果启用模拟数据模式
        if self.use_mock_data:
            weather_response = self._get_mock_weather(city, lang)
            self.cache.set(city, lang, weather_response)
            return weather_response
        
        # 尝试主数据源（和风天气）
        try:
            weather_response = self._try_primary_source(city, lang)
            if weather_response:
                self.cache.set(city, lang, weather_response)
                return weather_response
        except Exception as e:
            self.logger.error(f"和风天气数据源失败: {e}")
        
        # 所有数据源都失败，使用模拟数据
        self.logger.warning("所有数据源均失败，使用模拟数据")
        weather_response = self._get_mock_weather(city, lang)
        self.cache.set(city, lang, weather_response)
        return weather_response
        
    def _try_primary_source(self, city: str, lang: Language) -> WeatherResponse:
        """尝试主数据源（和风天气）"""
        self.logger.info(f"尝试和风天气获取 {city} 天气数据")
        
        try:
            # 和风天气是同步API
            current_data = self.primary_client.get_current_weather(city, lang)
            forecast_data = self.primary_client.get_forecast(city, lang)
            
            if not current_data or not forecast_data:
                raise Exception("无法获取天气数据")
            
            # 解析数据
            weather_response = self.primary_client.parse_weather_data(current_data, forecast_data, lang)
            
            self.logger.info(f"和风天气成功获取 {city} 天气数据")
            return weather_response
            
        except Exception as e:
            raise Exception(f"和风天气数据源异常: {e}")
            
    def _get_mock_weather(self, city: str, lang: Language) -> WeatherResponse:
        """获取模拟天气数据"""
        try:
            current_data = self.mock_client.get_current_weather(city, lang)
            forecast_data = self.mock_client.get_forecast(city, lang)
            weather_response = self.mock_client.parse_weather_data(
                current_data, forecast_data, lang
            )
            
            self.logger.info(f"生成模拟天气数据 for {city}")
            return weather_response
            
        except Exception as e:
            raise Exception(f"模拟数据生成异常: {e}")
    
    def get_service_status(self) -> dict:
        """获取服务状态信息"""
        cache_stats = self.cache.get_stats()
        status_info = {
            "status": "running",
            "cache_stats": cache_stats,
            "data_sources": {
                "primary": "WeatherAPI (Bearer Token)",
                "mock": "MockData"
            },
            "current_mode": "mock" if self.use_mock_data else "api"
        }
        return status_info


class LocalizationService:
    """多语言本地化服务"""
    
    def __init__(self):
        self.translations = {
            "clear": {"zh": "晴朗", "en": "Clear"},
            "clear sky": {"zh": "晴朗天空", "en": "clear sky"},
            "clouds": {"zh": "多云", "en": "Clouds"},
            "few clouds": {"zh": "少云", "en": "few clouds"},
            "rain": {"zh": "下雨", "en": "Rain"},
            "light rain": {"zh": "小雨", "en": "light rain"},
            "snow": {"zh": "下雪", "en": "Snow"},
            "mist": {"zh": "薄雾", "en": "Mist"},
            "thunderstorm": {"zh": "雷暴", "en": "Thunderstorm"},
            "drizzle": {"zh": "毛毛雨", "en": "Drizzle"}
        }
    
    def translate_weather_description(self, description: str, lang: Language) -> str:
        """翻译天气描述"""
        key = description.lower()
        if key in self.translations:
            return self.translations[key][lang.value]
        return description