import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

# Vercel Serverless Functions需要这个格式
# 直接导出app对象，Vercel会自动处理
handler = app