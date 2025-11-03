from flask import Flask
import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

# Vercel需要这个handler
handler = app