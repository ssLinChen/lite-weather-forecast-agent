"""
天气API客户端
基于Bearer Token认证的天气API服务
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from weather_mcp.models import WeatherResponse, ForecastDay, WeatherCondition, Language
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class HeWeatherClient:
    """天气API客户端（基于Bearer Token认证）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 从环境变量获取Bearer Token
        self.bearer_token = os.getenv("WEATHER_API_BEARER_TOKEN", "")
        
        # API基础URL
        self.base_url = "https://kf5g7cg6t3.re.qweatherapi.com/v7"
        
        # 默认城市位置ID（北京）
        self.default_location = "101010100"
    
    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            'Authorization': f'Bearer {self.bearer_token}',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
    def get_current_weather(self, city: str, lang: Language = Language.EN) -> Optional[Dict[str, Any]]:
        """获取当前天气数据"""
        try:
            # 使用默认位置ID（北京）或根据城市名查找
            location_id = self._get_location_id(city)
            
            # 获取实时天气
            url = f"{self.base_url}/weather/now"
            params = {
                "location": location_id
            }
            
            headers = self._get_headers()
            
            self.logger.debug(f"天气API请求URL: {url}")
            self.logger.debug(f"天气API请求参数: {params}")
            self.logger.debug(f"请求头: {headers}")
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.logger.debug(f"天气API响应: {data}")
                
                # 检查API响应是否成功
                if data.get("code") == "200" or "now" in data:
                    self.logger.info(f"成功获取 {city} 实时天气数据")
                    return {
                        "location": {"id": location_id, "name": city},
                        "now": data.get("now", {})
                    }
                else:
                    self.logger.error(f"天气API错误: {data.get('code')} - {data.get('message', '未知错误')}")
                    return None
            else:
                self.logger.error(f"天气API请求失败: {response.status_code}")
                self.logger.error(f"天气API响应内容: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取天气数据异常: {e}")
            
        return None
    
    def get_forecast(self, city: str, lang: Language = Language.EN) -> Optional[Dict[str, Any]]:
        """获取3天天气预报"""
        try:
            # 使用默认位置ID（北京）或根据城市名查找
            location_id = self._get_location_id(city)
            
            # 获取3天预报
            url = f"{self.base_url}/weather/3d"
            params = {
                "location": location_id
            }
            
            headers = self._get_headers()
            
            self.logger.debug(f"预报API请求URL: {url}")
            self.logger.debug(f"预报API请求参数: {params}")
            self.logger.debug(f"请求头: {headers}")
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.logger.debug(f"预报API响应: {data}")
                
                # 检查API响应是否成功
                if data.get("code") == "200" or "daily" in data:
                    self.logger.info(f"成功获取 {city} 3天天气预报")
                    return {
                        "location": {"id": location_id, "name": city},
                        "daily": data.get("daily", [])
                    }
                else:
                    self.logger.error(f"预报API错误: {data.get('code')} - {data.get('message', '未知错误')}")
                    return None
            else:
                self.logger.error(f"预报API请求失败: {response.status_code}")
                self.logger.error(f"预报API响应内容: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取天气预报数据异常: {e}")
            
        return None
    
    def _get_location_id(self, city: str) -> str:
        """获取城市位置ID"""
        # 字符编码修复：处理乱码问题
        original_city = city
        try:
            # 检测并修复常见的UTF-8乱码
            if 'å' in city or 'ä' in city or 'º' in city:
                # 尝试从latin-1编码转换回UTF-8
                city_bytes = city.encode('latin-1')
                city = city_bytes.decode('utf-8')
                self.logger.debug(f"修复字符编码: '{original_city}' -> '{city}'")
        except Exception as e:
            self.logger.debug(f"字符编码修复失败: {e}")
        
        # 简单映射城市名到位置ID
        city_mapping = {
            "北京": "101010100",
            "beijing": "101010100",
            "上海": "101020100",
            "shanghai": "101020100",
            "广州": "101280101",
            "guangzhou": "101280101",
            "深圳": "101280601",
            "shenzhen": "101280601",
            "杭州": "101210101",
            "hangzhou": "101210101"
        }
        
        # 如果城市名在映射中，返回对应的位置ID
        if city.lower() in [k.lower() for k in city_mapping.keys()]:
            for key, value in city_mapping.items():
                if key.lower() == city.lower():
                    return value
        
        # 默认返回北京的位置ID
        self.logger.info(f"未找到城市 '{city}' (原始: '{original_city}') 的映射，使用默认位置ID")
        return self.default_location
    
    def parse_weather_data(self, current_data: Dict[str, Any], forecast_data: Dict[str, Any], lang: Language) -> WeatherResponse:
        """解析天气数据为响应模型"""
        try:
            location = current_data["location"]
            now = current_data["now"]
            daily_forecast = forecast_data["daily"]
            
            # 解析当前天气 - 适配新的API响应格式
            current_condition = WeatherCondition(
                main=now.get("text", now.get("cond_txt", "未知")),
                description=now.get("text", now.get("cond_txt", "未知天气")),
                icon=now.get("icon", now.get("cond_code", ""))
            )
            
            # 解析3天预报 - 适配新的API响应格式
            forecast_days = []
            for day_data in daily_forecast[:3]:  # 只取前3天
                forecast_days.append(ForecastDay(
                    date=day_data.get("fxDate", day_data.get("date", "")),
                    high_temp=float(day_data.get("tempMax", day_data.get("tmp_max", 0))),
                    low_temp=float(day_data.get("tempMin", day_data.get("tmp_min", 0))),
                    condition=WeatherCondition(
                        main=day_data.get("textDay", day_data.get("cond_txt_d", "未知")),
                        description=f"{day_data.get('textDay', day_data.get('cond_txt_d', '未知'))}转{day_data.get('textNight', day_data.get('cond_txt_n', '未知'))}",
                        icon=day_data.get("iconDay", day_data.get("cond_code_d", ""))
                    )
                ))
            
            # 根据位置ID确定正确的中文城市名
            location_id = location.get("id", "")
            city_mapping_by_id = {
                "101010100": "北京",
                "101020100": "上海",
                "101280101": "广州",
                "101280601": "深圳",
                "101210101": "杭州"
            }
            
            # 如果位置ID在映射中，使用对应的中文城市名
            correct_city_name = city_mapping_by_id.get(location_id, location["name"])
            
            # 构建响应 - 适配新的API字段名
            return WeatherResponse(
                city=correct_city_name,
                temperature=float(now.get("temp", now.get("tmp", 0))),
                feels_like=float(now.get("feelsLike", now.get("fl", 0))),
                humidity=int(now.get("humidity", now.get("hum", 0))),
                pressure=int(now.get("pressure", now.get("pres", 1013))),
                wind_speed=float(now.get("windSpeed", now.get("wind_spd", 0))),
                wind_direction=int(now.get("wind360", now.get("wind_deg", 0))),
                condition=current_condition,
                forecast=forecast_days,
                timestamp=now.get("obsTime", now.get("update_time", ""))
            )
        except KeyError as e:
            self.logger.error(f"解析天气数据时缺少必要字段: {e}")
            raise
        except Exception as e:
            self.logger.error(f"解析天气数据异常: {e}")
            raise


class MockWeatherClient:
    """模拟天气数据客户端（用于演示）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        from weather_mcp.services import LocalizationService
        self.localization = LocalizationService()
    
    def get_current_weather(self, city: str, lang: Language = Language.EN) -> Optional[Dict[str, Any]]:
        """生成模拟当前天气数据"""
        # 字符编码修复：处理城市名称乱码
        from utils.encoding_service import ProfessionalEncodingService
        encoding_service = ProfessionalEncodingService()
        fixed_city = encoding_service.fix_text(city)
        
        if fixed_city != city:
            self.logger.debug(f"当前天气数据城市名称修复: '{city}' -> '{fixed_city}'")
            
        mock_data = {
            "name": fixed_city,  # 使用修复后的城市名称
            "main": {
                "temp": 25.5,
                "feels_like": 26.0,
                "humidity": 60,
                "pressure": 1013
            },
            "wind": {
                "speed": 5.2,
                "deg": 180
            },
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "dt": 1696060800
        }
        self.logger.info(f"生成模拟天气数据 for {fixed_city}")
        return mock_data
    
    def get_forecast(self, city: str, lang: Language = Language.EN) -> Optional[Dict[str, Any]]:
        """生成模拟预报数据"""
        import datetime
        
        # 字符编码修复：处理城市名称乱码
        from utils.encoding_service import ProfessionalEncodingService
        encoding_service = ProfessionalEncodingService()
        fixed_city = encoding_service.fix_text(city)
        
        if fixed_city != city:
            self.logger.debug(f"预报数据城市名称修复: '{city}' -> '{fixed_city}'")
        
        base_date = datetime.datetime.now().date()
        forecast_list = []
        
        for i in range(3):
            date = base_date + datetime.timedelta(days=i)
            forecast_list.append({
                "dt_txt": f"{date} 12:00:00",
                "main": {
                    "temp_max": 26 + i,
                    "temp_min": 18 + i
                },
                "weather": [
                    {
                        "main": ["Clear", "Clouds", "Rain"][i],
                        "description": ["clear sky", "few clouds", "light rain"][i]
                    }
                ]
            })
        
        mock_data = {
            "list": forecast_list,
            "city": {"name": fixed_city}  # 使用修复后的城市名称
        }
        return mock_data
    
    def parse_weather_data(self, current_data: Dict[str, Any], forecast_data: Dict[str, Any], lang: str) -> WeatherResponse:
        """解析模拟数据"""
        import datetime
        from weather_mcp.models import Language
        
        try:
            # 字符编码修复：处理城市名称乱码
            city_name = current_data["name"]
            original_city = city_name
            
            # 使用专业编码修复服务
            from utils.encoding_service import ProfessionalEncodingService
            encoding_service = ProfessionalEncodingService()
            city_name = encoding_service.fix_text(city_name)
            
            if city_name != original_city:
                self.logger.debug(f"专业编码修复: '{original_city}' -> '{city_name}'")
            
            # 将字符串语言参数转换为Language枚举
            lang_enum = Language.ZH if lang.lower() == 'zh' else Language.EN
            
            # 解析当前天气数据
            current_main = current_data["main"]
            current_weather = current_data["weather"][0]
            
            # 解析预报数据
            forecast_days = []
            for i, day_data in enumerate(forecast_data["list"]):
                date = datetime.datetime.now().date() + datetime.timedelta(days=i)
                
                # 本地化天气描述
                main_condition = day_data["weather"][0]["main"]
                description = day_data["weather"][0]["description"]
                
                localized_main = self.localization.translate_weather_description(main_condition, lang_enum)
                localized_description = self.localization.translate_weather_description(description, lang_enum)
                
                forecast_days.append(ForecastDay(
                    date=str(date),
                    high_temp=float(day_data["main"]["temp_max"]),
                    low_temp=float(day_data["main"]["temp_min"]),
                    condition=WeatherCondition(
                        main=localized_main,
                        description=localized_description,
                        icon=day_data["weather"][0].get("icon", "")
                    )
                ))
            
            # 本地化当前天气描述
            current_main_condition = current_weather["main"]
            current_description = current_weather["description"]
            
            localized_current_main = self.localization.translate_weather_description(current_main_condition, lang_enum)
            localized_current_description = self.localization.translate_weather_description(current_description, lang_enum)
            
            # 构建响应
            return WeatherResponse(
                city=city_name,  # 使用修复后的城市名称
                temperature=float(current_main["temp"]),
                feels_like=float(current_main["feels_like"]),
                humidity=int(current_main["humidity"]),
                pressure=int(current_main["pressure"]),
                wind_speed=float(current_data["wind"]["speed"]),
                wind_direction=int(current_data["wind"]["deg"]),
                condition=WeatherCondition(
                    main=localized_current_main,
                    description=localized_current_description,
                    icon=current_weather["icon"]
                ),
                forecast=forecast_days,
                timestamp=str(datetime.datetime.now())
            )
        except Exception as e:
            self.logger.error(f"解析模拟数据错误: {e}")
            raise