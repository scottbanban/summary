#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vercel Serverless Function 入口
"""

import os
import sys

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入Flask应用
from app import app as flask_app

# Vercel serverless handler
def handler(event, context):
    """
    Vercel会调用这个handler函数
    event: 包含HTTP请求信息
    context: 包含调用上下文
    """
    from werkzeug.wrappers import Request
    from werkzeug.wrappers import Response

    # 构建WSGI环境
    headers = event.get('headers', {})

    environ = {
        'REQUEST_METHOD': event.get('method', 'GET'),
        'PATH_INFO': event.get('path', '/'),
        'QUERY_STRING': event.get('query', ''),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'HTTP_HOST': headers.get('host', 'localhost'),
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # 添加HTTP头到环境
    for key, value in headers.items():
        env_key = 'HTTP_' + key.upper().replace('-', '_')
        environ[env_key] = value

    # 响应状态和头
    response_status = None
    response_headers = None

    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers

    # 调用Flask应用
    result = flask_app(environ, start_response)

    # 获取响应体
    body = b''.join(result)

    # 解析状态码
    status_code = 200
    if response_status:
        status_code = int(response_status.split(' ')[0])

    # 构建响应头字典
    headers_dict = {}
    if response_headers:
        for key, value in response_headers:
            headers_dict[key] = value

    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': body.decode('utf-8')
    }
