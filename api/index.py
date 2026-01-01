#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vercel Serverless Function 入口
"""

import os
import sys

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量（Vercel会自动注入环境变量，但确保 dotenv 也被加载）
from dotenv import load_dotenv
load_dotenv()

# 导入Flask应用
from app import app

# Vercel Python Runtime会查找这个handler
def handler(event, context):
    """
    Vercel serverless handler
    """
    from werkzeug.wrappers import Response

    # 解析请求
    method = event.get('method', 'GET')
    path = event.get('path', '/')
    query_string = event.get('query', '')
    headers = event.get('headers', {})

    # 构建WSGI环境字典
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'SERVER_NAME': headers.get('host', 'vercel.app'),
        'SERVER_PORT': '443',
        'HTTP_HOST': headers.get('host', 'vercel.app'),
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }

    # 添加所有HTTP头
    for key, value in headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value

    # 收集响应
    response_status = None
    response_headers = None

    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers

    # 调用Flask应用
    body_iter = app(environ, start_response)
    body = b''.join(body_iter)

    # 解析状态码
    status_code = 200
    if response_status:
        try:
            status_code = int(response_status.split()[0])
        except:
            status_code = 200

    # 构建响应头
    headers_dict = {}
    if response_headers:
        headers_dict = dict(response_headers)

    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': body.decode('utf-8')
    }
