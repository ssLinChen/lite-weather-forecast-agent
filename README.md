<<<<<<< HEAD
# 轻量级天气查询MCP服务

基于Bearer Token认证的天气API服务，提供实时天气和天气预报查询功能。

## 功能特性

- ✅ 实时天气查询（当前温度、湿度、气压、风速等）
- ✅ 3天天气预报
- ✅ 多语言支持（中文、英文）
- ✅ 内存缓存机制（10分钟TTL）
- ✅ 多数据源回退（API失败时使用模拟数据）
- ✅ RESTful API接口

## 快速开始

### 环境要求

- Python 3.7+
- 依赖包：`requests`, `pydantic`, `cachetools`, `python-dotenv`

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

编辑 `.env` 文件：

```env
# 天气API配置
HEWEATHER_API_KEY=kf5g7cg6t3.re.qweatherapi.com
WEATHER_API_BEARER_TOKEN=eyJhbGciOiJFZERTQSIsImtpZCI6Iks3SDI1QURERjYifQ.eyJzdWIiOiIyR0RZQkI1QzdHIiwiaWF0IjoxNzU5MjI5Nzg4LCJleHAiOjE3NTkyNDYyMjB9.q15_rtCkOD8dfwJC0YUUWIQIQjWtOLQhdL0K--J5H9Mrpv3IflU8eOnqSlnRVJgsqPGeYyJUybn0tRBGRaGXDQ

# 服务配置
WEATHER_MCP_HOST=0.0.0.0
WEATHER_MCP_PORT=8000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=weather_mcp.log
```

### 启动服务

```bash
python weather_mcp/simple_server.py
```

或

```bash
python -c "from weather_mcp.simple_server import run_server; run_server()"
```

服务启动后将在 `http://localhost:8000` 运行。

## API接口

### 1. 健康检查

**GET** `/health`

检查服务状态和缓存统计。

**响应示例：**
```json
{
  "status": "healthy",
  "service_info": {
    "status": "running",
    "cache_stats": {
      "current_size": 0,
      "max_size": 1000,
      "ttl": 600
    },
    "data_sources": {
      "primary": "WeatherAPI (Bearer Token)",
      "mock": "MockData"
    },
    "current_mode": "api"
  }
}
```

### 2. 天气查询

**GET** `/weather?city={城市名}&lang={语言}`

查询指定城市的天气信息。

**参数：**
- `city` (必需): 城市名称（支持中文和英文）
- `lang` (可选): 语言类型，默认 `en`，支持 `zh`（中文）和 `en`（英文）

**示例请求：**

### curl命令行测试

```bash
# 查询北京天气（中文）
curl -X GET "http://localhost:8000/weather?city=北京&lang=zh" -H "Accept: application/json; charset=utf-8"

# 查询上海天气（英文）
curl -X GET "http://localhost:8000/weather?city=Shanghai&lang=en" -H "Accept: application/json; charset=utf-8"

# 查询广州天气（默认英文）
curl -X GET "http://localhost:8000/weather?city=广州" -H "Accept: application/json; charset=utf-8"

# 健康检查
curl -X GET "http://localhost:8000/health"

# 缓存统计
curl -X GET "http://localhost:8000/cache/stats"
```

### 浏览器测试

直接在浏览器地址栏输入以下URL进行测试：

```
# 查询北京天气（中文）
http://localhost:8000/weather?city=北京&lang=zh

# 查询上海天气（英文）
http://localhost:8000/weather?city=Shanghai&lang=en

# 健康检查
http://localhost:8000/health

# 缓存统计
http://localhost:8000/cache/stats
```

**注意：** 如果浏览器显示乱码，请确保浏览器编码设置为UTF-8，或使用开发者工具查看JSON响应。

**响应示例：**
```json
{
  "city": "北京",
  "temperature": 23.0,
  "feels_like": 25.0,
  "humidity": 70,
  "pressure": 1005,
  "wind_speed": 0.0,
  "wind_direction": 0,
  "condition": {
    "main": "阴",
    "description": "阴",
    "icon": "104"
  },
  "forecast": [
    {
      "date": "2025-09-30",
      "high_temp": 29.0,
      "low_temp": 16.0,
      "condition": {
        "main": "晴",
        "description": "晴转多云",
        "icon": "100"
      }
    },
    {
      "date": "2025-10-01",
      "high_temp": 30.0,
      "low_temp": 17.0,
      "condition": {
        "main": "晴",
        "description": "晴转晴",
        "icon": "100"
      }
    },
    {
      "date": "2025-10-02",
      "high_temp": 29.0,
      "low_temp": 17.0,
      "condition": {
        "main": "晴",
        "description": "晴转多云",
        "icon": "100"
      }
    }
  ],
  "timestamp": "2025-09-30T19:40+08:00"
}
```

### 3. 缓存统计

**GET** `/cache/stats`

获取缓存统计信息。

**响应示例：**
```json
{
  "cache_stats": {
    "current_size": 2,
    "max_size": 1000,
    "ttl": 600
  }
}
```

## 支持的城市

目前支持以下城市（支持中英文名称）：

- 北京 / Beijing
- 上海 / Shanghai  
- 广州 / Guangzhou
- 深圳 / Shenzhen
- 杭州 / Hangzhou

其他城市将默认返回北京天气数据。

## 项目结构

```
lite-weather-forecast-agent/
├── weather_mcp/
│   ├── __init__.py
│   ├── simple_server.py      # HTTP服务器
│   ├── services.py           # 业务逻辑服务
│   ├── models.py             # 数据模型
│   ├── cache.py              # 缓存实现
│   └── clients/
│       ├── __init__.py
│       └── heweather_api.py  # 天气API客户端
├── utils/
├── version_system/
├── .env                      # 环境变量配置
├── requirements.txt          # 依赖包
└── README.md                # 本文档
```

## 技术架构

### 核心组件

1. **HTTP服务器** (`simple_server.py`)
   - 基于Python标准库的HTTP服务器
   - RESTful API接口
   - 请求路由和错误处理

2. **天气服务** (`services.py`)
   - 多数据源回退机制
   - 缓存管理
   - 业务逻辑处理

3. **API客户端** (`clients/heweather_api.py`)
   - Bearer Token认证
   - 实时天气和预报查询
   - 数据解析和格式化

4. **缓存系统** (`cache.py`)
   - 内存缓存（TTL机制）
   - 缓存键管理
   - 统计信息

### 数据流

1. 客户端发送HTTP请求
2. 服务器解析请求参数
3. 检查缓存是否存在有效数据
4. 调用天气API获取数据
5. 解析和格式化响应数据
6. 更新缓存并返回结果

## 错误处理

服务提供标准的HTTP状态码和错误信息：

- `200`: 成功
- `400`: 请求参数错误
- `404`: 接口不存在
- `500`: 服务器内部错误

错误响应格式：
```json
{
  "error_code": 400,
  "message": "Missing city parameter"
}
```

## 部署说明

### 开发环境

1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量
4. 启动服务：`python weather_mcp/simple_server.py`

### 生产环境建议

- 使用Gunicorn或uWSGI作为WSGI服务器
- 配置Nginx反向代理
- 设置适当的日志轮转
- 监控服务健康状态

## 故障排除

### 常见问题

1. **端口占用**
   - 错误：`Address already in use`
   - 解决：修改端口号或停止占用端口的进程

2. **API密钥错误**
   - 错误：`天气API请求失败: 401`
   - 解决：检查Bearer Token配置

3. **网络连接问题**
   - 错误：`连接超时`
   - 解决：检查网络连接和防火墙设置

### 日志查看

服务日志保存在 `weather_mcp.log` 文件中，包含详细的调试信息。

## 许可证

本项目基于MIT许可证开源。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。
=======
# lite-weather-forecast-agent
一款轻量级天气预报智能体
>>>>>>> 29a4574a86e4ae3e8a9f57fa4ccb04e1ee6c829e
