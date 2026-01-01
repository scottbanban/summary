# 配置文件
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

    # 飞书应用配置
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', 'cli_a9de76e17bb81cd4')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', 'GTkw0Ffj4NYNuXPjsYa8kf2cURExGhoE')

    # 多维表格配置
    BASE_ID = os.getenv('BASE_ID', 'Sq5Eb7CJJa0BhDs6ycecghcCnEg')
    TABLE_ID = os.getenv('TABLE_ID', 'tblAN4yQHOIGRBVI')

    # API配置
    FEISHU_API_BASE = 'https://open.feishu.cn/open-apis'

    # 缓存配置（单位：秒）
    CACHE_TIME = 300  # 5分钟