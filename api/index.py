from flask import Flask
import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入Flask应用
from app import app

# Vercel Serverless Functions需要这个格式
# 使用WSGI应用格式
app = app

# Vercel需要这个handler
handler = app