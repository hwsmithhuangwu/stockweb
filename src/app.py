from flask import Flask, render_template, request, redirect, url_for
import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, DragonTiger, JiuYan, WenCai, QuantData, JiuYanNews
from data_import import import_dragontiger_data, import_jiuyan_data, import_wencai_data, import_quant_data, import_jiuyan_news_data

app = Flask(__name__)

# 生产环境配置
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Railway生产环境
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/stock.db'
    app.config['DEBUG'] = False
elif os.environ.get('VERCEL'):
    # Vercel生产环境
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/stock.db'
    app.config['DEBUG'] = False
else:
    # 本地开发环境
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock.db'
    app.config['DEBUG'] = True

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')

@app.route('/dragontiger')
def dragontiger():
    """龙虎榜数据页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    dragontiger_data = DragonTiger.query.order_by(DragonTiger.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('dragontiger.html', data=dragontiger_data)

@app.route('/jiuyan')
def jiuyan():
    """韭研公社数据页面 - 重定向到韭研公社新闻页面"""
    return redirect(url_for('jiuyan_news'))

@app.route('/wencai')
def wencai():
    """i问财数据页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    wencai_data = WenCai.query.order_by(WenCai.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('wencai.html', data=wencai_data)

@app.route('/quant')
def quant():
    """量化分析数据页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    quant_data = QuantData.query.order_by(QuantData.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 预先计算置信度百分比，避免在模板中使用复杂表达式
    processed_items = []
    for item in quant_data.items:
        processed_item = {
            'id': item.id,
            'date': item.date,
            'stock_code': item.stock_code,
            'stock_name': item.stock_name,
            'strategy_name': item.strategy_name,
            'signal': item.signal,
            'confidence': item.confidence,
            'confidence_percent': round(item.confidence * 100),
            'target_price': item.target_price,
            'stop_loss': item.stop_loss,
            'period': item.period
        }
        processed_items.append(processed_item)
    
    # 创建一个简单的分页对象替代方案
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
            
        def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if num <= left_edge or \
                   (num > self.page - left_current - 1 and num < self.page + right_current) or \
                   num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    processed_pagination = SimplePagination(
        items=processed_items,
        page=quant_data.page,
        per_page=quant_data.per_page,
        total=quant_data.total
    )
    
    return render_template('quant.html', data=processed_pagination)

@app.route('/jiuyan_news')
def jiuyan_news():
    """韭研公社新闻数据页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    jiuyan_news_data = JiuYanNews.query.order_by(JiuYanNews.news_date.desc(), JiuYanNews.news_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('jiuyan_news.html', data=jiuyan_news_data)

@app.route('/import_data')
def import_data():
    """导入数据路由（模拟）"""
    # 这里应该是实际的数据导入逻辑
    # 暂时用模拟数据演示
    import_dragontiger_data()
    import_jiuyan_data()
    import_wencai_data()
    import_quant_data()
    return "数据导入完成"

@app.route('/import_jiuyan_news')
def import_jiuyan_news():
    """导入韭研公社新闻数据"""
    result = import_jiuyan_news_data()
    if result:
        return "韭研公社新闻数据导入完成"
    else:
        return "韭研公社新闻数据导入失败，请检查文件是否存在"

@app.route('/import_today_data')
def import_today_data():
    """导入今日数据 - 运行爬虫并导入最新数据"""
    import subprocess
    import sys
    import os
    
    # 获取当前脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # 1. 运行爬虫程序获取最新数据
        print("开始运行爬虫程序获取最新数据...")
        result = subprocess.run([sys.executable, "get_stock_data.py"], 
                              cwd=script_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"爬虫程序运行失败: {result.stderr}")
            return "爬虫程序运行失败，请检查爬虫脚本"
        
        print("爬虫程序运行成功，开始导入数据...")
        
        # 2. 导入龙虎榜数据
        try:
            import_dragontiger_data()
            print("龙虎榜数据导入成功")
        except Exception as e:
            print(f"龙虎榜数据导入失败: {e}")
        
        # 3. 导入韭研公社新闻数据
        try:
            import_jiuyan_news_data()
            print("韭研公社新闻数据导入成功")
        except Exception as e:
            print(f"韭研公社新闻数据导入失败: {e}")
        
        # 4. 导入其他数据（可选）
        try:
            import_jiuyan_data()
            print("韭研公社数据导入成功")
        except Exception as e:
            print(f"韭研公社数据导入失败: {e}")
        
        print("今日数据导入完成")
        
        # 返回成功页面，包含跳转链接
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>数据导入成功</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="alert alert-success" role="alert">
                    <h4 class="alert-heading">数据导入成功！</h4>
                    <p>今日数据已成功导入数据库，您可以查看最新数据：</p>
                    <hr>
                    <div class="d-flex gap-3">
                        <a href="/dragontiger" class="btn btn-primary">查看龙虎榜</a>
                        <a href="/jiuyan_news" class="btn btn-success">查看韭研新闻</a>
                        <a href="/" class="btn btn-secondary">返回首页</a>
                    </div>
                </div>
            </div>
            <script>
                // 3秒后自动跳转到龙虎榜页面
                setTimeout(function() {
                    window.location.href = '/dragontiger';
                }, 3000);
            </script>
        </body>
        </html>
        '''
        
    except Exception as e:
        print(f"导入今日数据时发生错误: {e}")
        return f"数据导入失败: {str(e)}"

# 确保在Vercel环境中也能正确初始化数据库
with app.app_context():
    db.create_all()

# Vercel环境检测和启动
if __name__ == '__main__':
    # 获取环境变量中的端口，Railway会提供PORT环境变量
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])
else:
    # Vercel Serverless环境
    # 确保应用在导入时就能正确初始化
    print("Vercel环境检测到，应用已初始化")