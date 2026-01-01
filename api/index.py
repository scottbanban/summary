#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vercel Serverless Function 入口
"""

import os
import sys

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 设置工作目录
os.chdir(parent_dir)

# 导入Flask应用
from app import app

# Vercel会查找这个handler函数
def handler(event, context):
    """处理Vercel请求"""
    # 获取请求信息
    method = event.get('method', 'GET')
    path = event.get('path', '/')
    query_string = event.get('query', '')
    headers = event.get('headers', {})
    body = event.get('body', '')

    # 构建WSGI环境
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
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
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': headers.get('content-length', '0'),
    }

    # 添加HTTP头
    for key, value in headers.items():
        env_key = 'HTTP_' + key.upper().replace('-', '_')
        environ[env_key] = value

    # 响应收集器
    response_data = {
        'status': None,
        'headers': None,
        'body': []
    }

    def start_response(status, response_headers):
        response_data['status'] = status
        response_data['headers'] = response_headers

    # 调用Flask应用
    app_iter = app(environ, start_response)

    # 收集响应体
    for chunk in app_iter:
        if chunk:
            response_data['body'].append(chunk)

    body_bytes = b''.join(response_data['body'])

    # 解析状态码
    status_code = 200
    if response_data['status']:
        status_code = int(response_data['status'].split()[0])

    # 构建响应头
    resp_headers = {}
    if response_data['headers']:
        for key, value in response_data['headers']:
            resp_headers[key] = value

    return {
        'statusCode': status_code,
        'headers': resp_headers,
        'body': body_bytes.decode('utf-8', errors='replace')
    }
