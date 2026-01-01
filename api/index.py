#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vercel Serverless Function 入口
将Flask应用适配为Vercel函数
"""

import os
import sys

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入Flask应用
from app import app

# Vercel会自动识别并调用这个WSGI应用
# 不需要额外的handler函数
