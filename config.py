import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class APIConfig:
    def __init__(self):
        # DeepSeek API配置
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
        
        # 新浪财经API配置
        self.SINA_API_URL = os.getenv("SINA_API_URL", "http://hq.sinajs.cn/list=")
        self.SINA_REFERER = os.getenv("SINA_REFERER", "https://finance.sina.com.cn")
        
        # Tushare API配置
        self.TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "")
        self.TUSHARE_API_URL = os.getenv("TUSHARE_API_URL", "http://api.tushare.pro")
        
        # 应用信息
        self.APP_TITLE = os.getenv("APP_TITLE", "投资理财分析助手")
        self.APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "基于DeepSeek AI的投资理财分析工具，提供市场行情、投资分析、目标追踪和风险控制等功能。")
        
        # 数据库配置
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./investment.db")
        
        # 应用设置
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
        
        # 缓存配置
        self.CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
        self.CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "app.log")
        
        # 安全配置
        self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # 性能配置
        self.MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "100"))
        self.TIMEOUT = int(os.getenv("TIMEOUT", "30"))
        
        # 其他配置
        self.CURRENCY = os.getenv("CURRENCY", "CNY")
        self.DATE_FORMAT = os.getenv("DATE_FORMAT", "%Y-%m-%d")
        self.TIME_FORMAT = os.getenv("TIME_FORMAT", "%H:%M:%S")

    @classmethod
    def get_config(cls) -> dict:
        """获取所有配置"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }

# 应用配置
APP_TITLE = "投资理财分析助手"
APP_DESCRIPTION = "基于DeepSeek AI的投资理财分析工具" 