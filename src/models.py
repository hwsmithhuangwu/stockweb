from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DragonTiger(db.Model):
    """龙虎榜数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)  # 排名
    date = db.Column(db.Date, nullable=False)
    stock_code = db.Column(db.String(10), nullable=False)
    stock_name = db.Column(db.String(50), nullable=False)
    buyers = db.Column(db.String(200), nullable=True)  # 购买人/机构
    change_percent = db.Column(db.String(20), nullable=False)  # 涨跌幅（百分比字符串）
    net_buy_amount = db.Column(db.String(50), nullable=False)  # 净买入金额（带单位）
    
    def __repr__(self):
        return f'<DragonTiger {self.rank} {self.stock_code} {self.date}>'

class JiuYan(db.Model):
    """韭研公社数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    stock_code = db.Column(db.String(10), nullable=False)
    stock_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)  # 价格
    change_percent = db.Column(db.Float, nullable=False)  # 涨跌幅
    volume = db.Column(db.Integer, nullable=False)  # 成交量
    market_value = db.Column(db.Float, nullable=False)  # 市值
    pe_ratio = db.Column(db.Float, nullable=True)  # 市盈率
    pb_ratio = db.Column(db.Float, nullable=True)  # 市净率
    dividend_yield = db.Column(db.Float, nullable=True)  # 股息率
    roe = db.Column(db.Float, nullable=True)  # 净资产收益率
    
    def __repr__(self):
        return f'<JiuYan {self.stock_code} {self.date}>'

class WenCai(db.Model):
    """i问财数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    stock_code = db.Column(db.String(10), nullable=False)
    stock_name = db.Column(db.String(50), nullable=False)
    indicator_name = db.Column(db.String(100), nullable=False)  # 指标名称
    indicator_value = db.Column(db.Float, nullable=False)  # 指标值
    industry = db.Column(db.String(50), nullable=True)  # 所属行业
    market = db.Column(db.String(20), nullable=True)  # 市场板块
    
    def __repr__(self):
        return f'<WenCai {self.stock_code} {self.date}>'

class QuantData(db.Model):
    """量化分析数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    stock_code = db.Column(db.String(10), nullable=False)
    stock_name = db.Column(db.String(50), nullable=False)
    strategy_name = db.Column(db.String(100), nullable=False)  # 策略名称
    signal = db.Column(db.String(20), nullable=False)  # 信号类型（买入/卖出）
    confidence = db.Column(db.Float, nullable=False)  # 信号置信度
    target_price = db.Column(db.Float, nullable=True)  # 目标价格
    stop_loss = db.Column(db.Float, nullable=True)  # 止损价格
    period = db.Column(db.Integer, nullable=True)  # 持有期（天）
    
    def __repr__(self):
        return f'<QuantData {self.stock_code} {self.date}>'

class JiuYanNews(db.Model):
    """韭研公社新闻数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    news_date = db.Column(db.Date, nullable=False)  # 新闻日期
    news_time = db.Column(db.String(10), nullable=False)  # 新闻时间
    stock_codes = db.Column(db.Text, nullable=False)  # 股票代码列表（逗号分隔）
    stock_names = db.Column(db.Text, nullable=False)  # 股票名称列表（逗号分隔）
    news_content = db.Column(db.Text, nullable=False)  # 新闻内容
    news_summary = db.Column(db.String(100), nullable=False)  # 新闻简介（前30个字）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    def __repr__(self):
        return f'<JiuYanNews {self.news_date} {self.news_time}>'