#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成按发布时间排序的股票新闻Markdown文档
"""

import json
import os
from datetime import datetime

def generate_stock_markdown():
    """生成按发布时间排序的股票新闻Markdown文档"""
    
    # 读取JSON文件
    json_file = "jiuyangongshe_news.json"
    
    if not os.path.exists(json_file):
        print(f"错误: 文件 {json_file} 不存在")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    # 按发布时间排序（从新到旧）
    def get_publish_time(news):
        try:
            # 解析时间格式：2025-09-30 12:02:50
            return datetime.strptime(news['publish_time'], '%Y-%m-%d %H:%M:%S')
        except:
            # 如果时间格式异常，返回一个很早的时间
            return datetime.min
    
    sorted_news = sorted(news_data, key=get_publish_time, reverse=True)
    
    # 生成Markdown内容
    md_content = "# 韭研公社股票相关新闻\n\n"
    md_content += f"**数据更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += f"**新闻总数**: {len(sorted_news)} 条\n\n"
    
    # 按日期分组
    news_by_date = {}
    for news in sorted_news:
        date_str = news['publish_time'][:10]  # 提取日期部分
        if date_str not in news_by_date:
            news_by_date[date_str] = []
        news_by_date[date_str].append(news)
    
    # 生成按日期分组的Markdown
    for date_str in sorted(news_by_date.keys(), reverse=True):
        md_content += f"## {date_str}\n\n"
        
        for news in news_by_date[date_str]:
            # 提取股票名称（去重）
            stock_names = set()
            
            # 从stock_info中提取股票名称
            if news.get('stock_info'):
                for stock in news['stock_info']:
                    if stock['type'] == 'linked_stock':
                        stock_names.add(stock['value'])
                    elif stock['type'] == 'name':
                        stock_names.add(stock['value'])
            
            # 从stock_links中提取股票名称
            if news.get('stock_links'):
                for stock_link in news['stock_links']:
                    stock_names.add(stock_link['name'])
            
            # 过滤掉两个字的通用名称（如股份、集团、科技等）
            filtered_stocks = set()
            generic_words = {'股份', '集团', '科技', '电子', '生物', '教育', '健康', '设计', '矿业', '金属'}
            
            for stock_name in stock_names:
                # 只保留长度大于2个字符且不在通用词列表中的股票名称
                if len(stock_name) > 2 and stock_name not in generic_words:
                    filtered_stocks.add(stock_name)
            
            # 格式化股票名称列表
            if filtered_stocks:
                stocks_str = ", ".join(sorted(filtered_stocks))
                md_content += f"- **{news['publish_time'][11:]}** - {stocks_str}\n"
            else:
                md_content += f"- **{news['publish_time'][11:]}** - 无具体股票\n"
        
        md_content += "\n"
    
    # 保存Markdown文件
    md_file = "jiuyangongshe_stocks.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Markdown文档已生成: {md_file}")
    print(f"包含 {len(sorted_news)} 条新闻，按发布时间排序")
    
    # 统计股票总数（过滤后的具体股票）
    all_stocks = set()
    generic_words = {'股份', '集团', '科技', '电子', '生物', '教育', '健康', '设计', '矿业', '金属'}
    
    for news in sorted_news:
        if news.get('stock_info'):
            for stock in news['stock_info']:
                if stock['type'] == 'linked_stock':
                    if len(stock['value']) > 2 and stock['value'] not in generic_words:
                        all_stocks.add(stock['value'])
                elif stock['type'] == 'name':
                    if len(stock['value']) > 2 and stock['value'] not in generic_words:
                        all_stocks.add(stock['value'])
        if news.get('stock_links'):
            for stock_link in news['stock_links']:
                if len(stock_link['name']) > 2 and stock_link['name'] not in generic_words:
                    all_stocks.add(stock_link['name'])
    
    print(f"共涉及 {len(all_stocks)} 个不同的具体股票（已过滤通用名称）")
    
    return md_file

if __name__ == "__main__":
    generate_stock_markdown()