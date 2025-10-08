"""
轻量级天气查询MCP服务 - 简化版本
使用标准库实现，避免依赖冲突
"""

import json
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from weather_mcp.services import WeatherService, LocalizationService
from weather_mcp.models import Language

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()


class WeatherMCPHandler(BaseHTTPRequestHandler):
    """天气MCP服务HTTP处理器"""
    
    def __init__(self, *args, **kwargs):
        self.weather_service = WeatherService()
        self.localization_service = LocalizationService()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # 路由处理
            if path == '/health':
                self._handle_health()
            elif path == '/weather':
                self._handle_weather(query_params)
            elif path == '/cache/stats':
                self._handle_cache_stats()
            else:
                self._send_error(404, "Not Found")
                
        except Exception as e:
            logging.error(f"请求处理错误: {e}")
            self._send_error(500, "Internal Server Error")
    
    def _handle_health(self):
        """健康检查"""
        status = self.weather_service.get_service_status()
        response = {
            "status": "healthy",
            "service_info": status
        }
        self._send_response(200, response)
    
    def _handle_weather(self, query_params):
        """天气查询处理"""
        # 处理URL编码的城市名
        import urllib.parse
        city = query_params.get('city', [None])[0]
        if city:
            # 正确处理URL编码的中文字符
            city = urllib.parse.unquote(city, encoding='utf-8')
        lang_str = query_params.get('lang', ['en'])[0]
        
        if not city:
            self._send_error(400, "Missing city parameter")
            return
        
        try:
            lang = Language(lang_str)
            weather_data = self.weather_service.get_weather(city, lang)
            
            # 调试：打印weather_data的类型和内容
            logging.info(f"weather_data类型: {type(weather_data)}")
            logging.info(f"weather_data内容: {weather_data}")
            
            # 转换为字典格式
            response = weather_data.dict()
            logging.info(f"转换后的response: {response}")
            
            self._send_response(200, response)
            
        except ValueError:
            self._send_error(400, "Invalid language parameter")
        except Exception as e:
            logging.error(f"天气查询错误: {e}", exc_info=True)
            import traceback
            logging.error(f"详细错误堆栈: {traceback.format_exc()}")
            self._send_error(500, f"Weather service error: {str(e)}")
    
    def _handle_cache_stats(self):
        """缓存统计"""
        stats = self.weather_service.get_service_status()
        response = {"cache_stats": stats["cache_stats"]}
        self._send_response(200, response)
    
    def _send_response(self, status_code, data):
        """发送成功响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """发送错误响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_response = {
            "error_code": status_code,
            "message": message
        }
        error_json = json.dumps(error_response, ensure_ascii=False)
        self.wfile.write(error_json.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        # 确保中文字符正确编码
        message = format % args
        try:
            # 尝试UTF-8编码
            message = message.encode('utf-8').decode('utf-8')
        except:
            pass
        logging.info(f"{self.client_address[0]} - {message}")


def run_server(host='localhost', port=8000):
    """启动MCP服务"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        handlers=[
            logging.FileHandler("weather_mcp.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    server = HTTPServer((host, port), WeatherMCPHandler)
    logging.info(f"天气MCP服务启动成功: http://{host}:{port}")
    logging.info("可用接口:")
    logging.info("  GET /health - 健康检查")
    logging.info("  GET /weather?city=Beijing&lang=en - 天气查询")
    logging.info("  GET /cache/stats - 缓存统计")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("服务停止")
    finally:
        server.server_close()


if __name__ == '__main__':
    run_server()