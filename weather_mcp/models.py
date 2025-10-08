"""
天气查询MCP服务数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum


class Language(str, Enum):
    """支持的语言枚举"""
    ZH = "zh"
    EN = "en"


class WeatherCondition(BaseModel):
    """天气状况模型"""
    main: str = Field(description="主要天气状况")
    description: str = Field(description="天气描述")
    icon: Optional[str] = Field(None, description="天气图标代码")


class ForecastDay(BaseModel):
    """单日天气预报"""
    date: str = Field(description="日期 (YYYY-MM-DD)")
    high_temp: float = Field(description="最高温度")
    low_temp: float = Field(description="最低温度")
    condition: WeatherCondition = Field(description="天气状况")


class WeatherResponse(BaseModel):
    """天气查询响应模型"""
    city: str = Field(description="城市名称")
    temperature: float = Field(description="当前温度")
    feels_like: float = Field(description="体感温度")
    humidity: int = Field(description="湿度百分比")
    pressure: int = Field(description="气压 (hPa)")
    wind_speed: float = Field(description="风速 (m/s)")
    wind_direction: int = Field(description="风向角度")
    condition: WeatherCondition = Field(description="当前天气状况")
    forecast: List[ForecastDay] = Field(description="3天天气预报")
    timestamp: str = Field(description="数据更新时间")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error_code: int = Field(description="错误代码")
    message: str = Field(description="错误信息")
    details: Optional[str] = Field(None, description="详细错误信息")