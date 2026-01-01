# 配置文件
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # 飞书应用配置（必须从环境变量读取）
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', '')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', '')

    # 多维表格配置（必须从环境变量读取）
    BASE_ID = os.getenv('BASE_ID', '')
    TABLE_ID = os.getenv('TABLE_ID', '')

    # API配置
    FEISHU_API_BASE = 'https://open.feishu.cn/open-apis'

    # 缓存配置（单位：秒）
    CACHE_TIME = int(os.getenv('CACHE_TIME', '300'))