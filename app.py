#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书多维表格驱动的个人博客网站
支持苹果设计风格和中国红主题色
"""

import os
import json
import time
import requests
import functools
from datetime import datetime, timedelta
from flask import Flask, render_template, abort, jsonify
from config import Config

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 缓存字典，用于存储API响应结果
_cache = {}
_cache_time = {}

def cache_response(key, duration=Config.CACHE_TIME):
    """装饰器：缓存函数结果"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            cache_key = f"{key}:{args}:{kwargs}"

            # 检查缓存是否存在且未过期
            if cache_key in _cache and _cache_time.get(cache_key, 0) + duration > current_time:
                return _cache[cache_key]

            # 调用函数获取结果
            result = func(*args, **kwargs)

            # 缓存结果
            _cache[cache_key] = result
            _cache_time[cache_key] = current_time
            return result
        return wrapper
    return decorator

def get_feishu_token():
    """获取飞书应用访问令牌"""
    url = f"{Config.FEISHU_API_BASE}/auth/v3/app_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "app_id": Config.FEISHU_APP_ID,
        "app_secret": Config.FEISHU_APP_SECRET
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()

        result = response.json()
        if result.get("code") == 0:
            return result.get("app_access_token")
        else:
            app.logger.error(f"获取飞书token失败: {result.get('msg')}")
            return None
    except requests.exceptions.RequestException as e:
        app.logger.error(f"请求飞书API失败: {str(e)}")
        return None

@cache_response("feishu_records", Config.CACHE_TIME)
def get_feishu_records():
    """从飞书多维表格获取记录数据"""
    token = get_feishu_token()
    if not token:
        return []

    url = f"{Config.FEISHU_API_BASE}/bitable/v1/apps/{Config.BASE_ID}/tables/{Config.TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        result = response.json()
        if result.get("code") == 0:
            records = result.get("data", {}).get("items", [])
            return process_records(records)
        else:
            app.logger.error(f"获取多维表格数据失败: {result.get('msg')}")
            return []
    except requests.exceptions.RequestException as e:
        app.logger.error(f"请求多维表格API失败: {str(e)}")
        return []

def process_records(records):
    """处理从飞书获取的原始记录"""
    processed = []

    for record in records:
        fields = record.get("fields", {})

        processed_record = {
            "id": record.get("record_id", ""),
            "title": fields.get("标题", "").strip(),
            "golden_sentence": fields.get("金句输出", "").strip(),
            "comment": fields.get("斯高特点评", "").strip(),
            "content": fields.get("概要内容输出", "").strip(),
            "created_time": record.get("created_time", datetime.now().isoformat()),
        }

        # 确保所有字段都有值
        if any(processed_record.values()):
            processed.append(processed_record)

    return processed

def truncate_text(text, max_length=100):
    """截断文本，用于首页预览"""
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    truncated = text[:max_length].strip()
    return truncated + "..."

@app.route("/")
def index():
    """首页：显示博客列表"""
    records = get_feishu_records()

    # 为每条记录添加预览文本
    for record in records:
        record["preview"] = truncate_text(record["content"], 100)

    return render_template("index.html",
                         records=records,
                         title="个人博客",
                         year=datetime.now().year)

@app.route("/article/<string:article_id>")
def article_detail(article_id):
    """文章详情页"""
    records = get_feishu_records()

    # 查找指定ID的记录
    article = None
    for record in records:
        if record["id"] == article_id:
            article = record
            break

    if not article:
        abort(404)

    return render_template("detail.html",
                         article=article,
                         title=f"{article['title']} - 个人博客",
                         year=datetime.now().year)

@app.route("/api/health")
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(_cache)
    })

@app.errorhandler(404)
def page_not_found(error):
    """404错误处理"""
    return render_template("error.html",
                         title="页面未找到",
                         message="抱歉，您访问的页面不存在。",
                         year=datetime.now().year), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template("error.html",
                         title="服务器错误",
                         message="抱歉，服务器发生了内部错误。",
                         year=datetime.now().year), 500

def clear_expired_cache():
    """清理过期的缓存"""
    current_time = time.time()
    expired_keys = []

    for key, expired_at in _cache_time.items():
        if expired_at + Config.CACHE_TIME < current_time:
            expired_keys.append(key)

    for key in expired_keys:
        _cache.pop(key, None)
        _cache_time.pop(key, None)

    if expired_keys:
        app.logger.info(f"清理了{len(expired_keys)}个过期缓存")

if __name__ == "__main__":
    # 确保模板和静态文件目录存在
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)

    # 定时清理缓存（在实际生产环境中应该使用Celery或APScheduler）
    @app.before_request
    def before_request():
        clear_expired_cache()

    # Render会通过环境变量PORT指定端口
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])