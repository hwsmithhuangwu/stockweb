from models import db, DragonTiger, JiuYan, WenCai, QuantData, JiuYanNews
from datetime import datetime, date
import random
import re

def import_dragontiger_data():
    """导入龙虎榜数据（从CSV文件）"""
    import csv
    import os
    
    # CSV文件路径
    csv_file = "龙虎榜数据.csv"
    
    # 检查CSV文件是否存在
    if not os.path.exists(csv_file):
        print(f"警告: 龙虎榜CSV文件 {csv_file} 不存在")
        return False
    
    # 读取CSV文件
    try:
        # 先清空现有数据
        DragonTiger.query.delete()
        db.session.commit()
        print("已清空现有龙虎榜数据")
        
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            record_count = 0
            for row in reader:
                # 解析日期
                date_str = row['date']
                try:
                    data_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    print(f"警告: 日期格式错误: {date_str}")
                    continue
                
                # 创建新的龙虎榜记录
                dragon_tiger = DragonTiger(
                    rank=int(row['rank']),
                    date=data_date,
                    stock_code=row['stock_code'],
                    stock_name=row['stock_name'],
                    buyers=row['buyers'],
                    change_percent=row['change_percent'],
                    net_buy_amount=row['net_buy_amount']
                )
                db.session.add(dragon_tiger)
                record_count += 1
            
            db.session.commit()
            print(f"成功导入龙虎榜数据，共 {record_count} 条记录")
            return True
            
    except Exception as e:
        print(f"导入龙虎榜数据时出错: {e}")
        db.session.rollback()
        return False

def import_jiuyan_data():
    """导入韭研公社模拟数据"""
    # 检查是否已有今日数据
    today = date.today()
    existing = JiuYan.query.filter_by(date=today).first()
    if existing:
        return
    
    # 模拟股票数据
    stocks = [
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("000063", "中兴通讯"),
        ("000651", "格力电器"),
        ("000858", "五粮液"),
        ("002475", "立讯精密"),
        ("300015", "爱尔眼科"),
        ("300750", "宁德时代"),
        ("600036", "招商银行"),
        ("600519", "贵州茅台")
    ]
    
    for i in range(5):  # 每天导入5条模拟数据
        stock = random.choice(stocks)
        jiu_yan = JiuYan(
            date=today,
            stock_code=stock[0],
            stock_name=stock[1],
            price=round(random.uniform(10, 100), 2),
            change_percent=round(random.uniform(-5, 10), 2),
            volume=random.randint(100000, 10000000),
            market_value=round(random.uniform(1000000000, 10000000000), 2),
            pe_ratio=round(random.uniform(5, 50), 2) if random.random() > 0.2 else None,
            pb_ratio=round(random.uniform(1, 10), 2) if random.random() > 0.2 else None,
            dividend_yield=round(random.uniform(0, 5), 2) if random.random() > 0.3 else None,
            roe=round(random.uniform(0, 30), 2) if random.random() > 0.2 else None
        )
        db.session.add(jiu_yan)
    
    db.session.commit()

def import_wencai_data():
    """导入i问财模拟数据"""
    # 检查是否已有今日数据
    today = date.today()
    existing = WenCai.query.filter_by(date=today).first()
    if existing:
        return
    
    # 模拟股票数据
    stocks = [
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("000063", "中兴通讯"),
        ("000651", "格力电器"),
        ("000858", "五粮液"),
        ("002475", "立讯精密"),
        ("300015", "爱尔眼科"),
        ("300750", "宁德时代"),
        ("600036", "招商银行"),
        ("600519", "贵州茅台")
    ]
    
    indicators = [
        ("市盈率", "PE Ratio"),
        ("市净率", "PB Ratio"),
        ("净资产收益率", "ROE"),
        ("毛利率", "Gross Margin"),
        ("净利润增长率", "Net Profit Growth"),
        ("营收增长率", "Revenue Growth"),
        ("负债率", "Debt Ratio"),
        ("现金流", "Cash Flow")
    ]
    
    for i in range(8):  # 每天导入8条模拟数据
        stock = random.choice(stocks)
        indicator = random.choice(indicators)
        wen_cai = WenCai(
            date=today,
            stock_code=stock[0],
            stock_name=stock[1],
            indicator_name=indicator[0],
            indicator_value=round(random.uniform(0, 100), 2),
            industry=random.choice(["金融", "房地产", "科技", "消费", "医药", "工业"]),
            market=random.choice(["主板", "中小板", "创业板"])
        )
        db.session.add(wen_cai)
    
    db.session.commit()

def import_quant_data():
    """导入量化分析模拟数据"""
    # 检查是否已有今日数据
    today = date.today()
    existing = QuantData.query.filter_by(date=today).first()
    if existing:
        return
    
    # 模拟股票数据
    stocks = [
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("000063", "中兴通讯"),
        ("000651", "格力电器"),
        ("000858", "五粮液"),
        ("002475", "立讯精密"),
        ("300015", "爱尔眼科"),
        ("300750", "宁德时代"),
        ("600036", "招商银行"),
        ("600519", "贵州茅台")
    ]
    
    strategies = [
        ("均线突破策略", "MA Breakout Strategy"),
        ("布林带策略", "Bollinger Bands Strategy"),
        ("MACD金叉策略", "MACD Golden Cross Strategy"),
        ("RSI超卖策略", "RSI Oversold Strategy"),
        ("动量策略", "Momentum Strategy")
    ]
    
    signals = ["买入", "卖出"]
    
    for i in range(5):  # 每天导入5条模拟数据
        stock = random.choice(stocks)
        strategy = random.choice(strategies)
        signal = random.choice(signals)
        quant_data = QuantData(
            date=today,
            stock_code=stock[0],
            stock_name=stock[1],
            strategy_name=strategy[0],
            signal=signal,
            confidence=round(random.uniform(0.6, 0.95), 2),
            target_price=round(random.uniform(10, 150), 2),
            stop_loss=round(random.uniform(5, 100), 2),
            period=random.randint(5, 30)
        )
        db.session.add(quant_data)
    
    db.session.commit()

def import_jiuyan_news_data():
    """导入韭研公社新闻数据"""
    import os
    import json
    
    # 新闻数据文件路径
    news_file = "jiuyangongshe_news.json"
    
    # 检查文件是否存在
    if not os.path.exists(news_file):
        print(f"警告: 韭研公社新闻文件 {news_file} 不存在")
        return False
    
    try:
        # 先清空现有新闻数据
        JiuYanNews.query.delete()
        db.session.commit()
        print("已清空现有韭研公社新闻数据")
        
        # 读取新闻文件
        with open(news_file, 'r', encoding='utf-8') as file:
            news_data = json.load(file)
        
        # 解析新闻数据
        record_count = 0
        
        for news_item in news_data:
            # 解析发布时间
            publish_time = news_item.get('publish_time', '')
            if not publish_time:
                continue
                
            # 提取日期和时间
            try:
                # 格式: "2025-10-31 09:44:12"
                publish_datetime = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')
                news_date = publish_datetime.date()
                news_time = publish_datetime.strftime('%H:%M:%S')
            except ValueError:
                print(f"警告: 时间格式错误: {publish_time}")
                continue
            
            # 提取股票信息
            stock_links = news_item.get('stock_links', [])
            stock_names = [stock['name'] for stock in stock_links if 'name' in stock]
            stock_codes = [stock.get('code', '') for stock in stock_links if 'name' in stock]
            
            # 如果没有关联股票，使用股票信息中的名称
            if not stock_names:
                stock_info = news_item.get('stock_info', [])
                stock_names = [info['value'] for info in stock_info if info.get('type') == 'linked_stock']
                stock_codes = [info.get('code', '') for info in stock_info if info.get('type') == 'linked_stock']
            
            # 获取新闻内容
            news_content = news_item.get('content_preview', '')
            
            # 生成新闻简介（前30个字）
            news_summary = news_content[:30] + "..." if len(news_content) > 30 else news_content
            
            # 创建新闻记录
            jiu_yan_news = JiuYanNews(
                news_date=news_date,
                news_time=news_time,
                stock_codes=", ".join(stock_codes),
                stock_names=", ".join(stock_names),
                news_content=news_content,
                news_summary=news_summary
            )
            db.session.add(jiu_yan_news)
            record_count += 1
        
        db.session.commit()
        print(f"成功导入韭研公社新闻数据，共 {record_count} 条记录")
        return True
        
    except Exception as e:
        print(f"导入韭研公社新闻数据时出错: {e}")
        db.session.rollback()
        return False