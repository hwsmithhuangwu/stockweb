#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将龙虎榜数据转换为Markdown表格格式
"""

import json
import os
from datetime import datetime

def format_number(num):
    """格式化数字显示，将净买入金额转换为亿单位"""
    if num >= 100000000:  # 大于等于1亿
        return f"{num/100000000:.2f}亿"
    elif num >= 10000:  # 大于等于1万
        return f"{num/10000:.2f}万"
    else:
        return str(num)

def generate_lhb_markdown(json_file_path, output_file_path):
    """
    从龙虎榜JSON文件生成Markdown表格
    
    Args:
        json_file_path: JSON文件路径
        output_file_path: 输出Markdown文件路径
    """
    try:
        # 读取JSON数据
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取股票数据
        stocks = data.get('top_30_stocks', [])
        # 确保stocks不是None，如果是None则设为空列表
        if stocks is None:
            stocks = []
        crawl_time = data.get('crawl_time', '')
        date = data.get('date', '')
        
        # 判断数据日期类型
        from datetime import datetime
        current_datetime = datetime.now()
        
        # 判断是否是当天数据
        if date == current_datetime.strftime('%Y-%m-%d'):
            date_description = "当天"
        else:
            date_description = "前一天"
        
        # 生成Markdown内容
        markdown_content = f"""# 龙虎榜数据 - {date} ({date_description})

**爬取时间**: {crawl_time}  
**数据日期**: {date} ({date_description})  
**股票数量**: {len(stocks)}只

## 净买入前30股票信息

| 排名 | 股票名称 | 股票代码 | 购买人 | 涨跌幅 | 净买入 |
|------|----------|----------|--------|--------|--------|
"""
        
        # 添加表格行
        for i, stock in enumerate(stocks, 1):
            stock_name = stock.get('gpmc', '')
            stock_code = stock.get('gpdm', '')
            buyer = stock.get('yzmc', '未知')
            change_rate = stock.get('zdf', 0)
            net_buy = stock.get('jmr', 0)
            formatted_net_buy = format_number(net_buy)
            
            # 处理购买人信息，如果太长则截断
            if buyer is not None and len(buyer) > 20:
                buyer = buyer[:20] + "..."
            
            markdown_content += f"| {i} | {stock_name} | {stock_code} | {buyer} | {change_rate:.2f}% | {formatted_net_buy} |\n"
        
        # 添加统计信息
        markdown_content += f"""
## 统计信息

- **总净买入金额**: {format_number(sum(stock.get('jmr', 0) for stock in stocks))}
- **平均净买入金额**: {format_number(sum(stock.get('jmr', 0) for stock in stocks) / len(stocks) if stocks else 0)}
- **最大净买入**: {format_number(max(stock.get('jmr', 0) for stock in stocks) if stocks else 0)}
- **最小净买入**: {format_number(min(stock.get('jmr', 0) for stock in stocks) if stocks else 0)}

## 备注

- 数据来源: 同花顺龙虎榜
- 统计范围: 净买入前30的股票
- 金额单位: 自动转换为亿/万单位显示
"""
        
        # 写入Markdown文件
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Markdown文件已生成: {output_file_path}")
        print(f"共处理 {len(stocks)} 条股票数据")
        
        return True
        
    except Exception as e:
        print(f"生成Markdown文件失败: {e}")
        return False

def main():
    """主函数"""
    # 文件路径
    json_file_path = "tdx_yzlhb_top30.json"
    output_file_path = "龙虎榜数据.md"
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file_path):
        print(f"JSON文件不存在: {json_file_path}")
        print("请先运行爬虫脚本获取数据")
        return
    
    # 生成Markdown表格
    success = generate_lhb_markdown(json_file_path, output_file_path)
    
    if success:
        print("\nMarkdown表格生成成功！")
        print("您可以在浏览器或Markdown编辑器中查看生成的文件")
    else:
        print("Markdown表格生成失败")

if __name__ == "__main__":
    main()