#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动运行龙虎榜爬虫和韭研公社爬虫
"""

import os
import sys
from datetime import datetime
import subprocess
import json
import csv



def run_lhb_crawler():
    """运行龙虎榜爬虫"""
    try:
        # 切换到脚本目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"当前工作目录: {os.getcwd()}")
        
        # 定义文件路径
        json_file = "tdx_yzlhb_top30.json"
        data_file = "tdx_yzlhb_data.json"
        
        # 先检查是否已经有现成的top30文件
        if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
            try:
                # 读取现有文件，检查日期
                with open(json_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                existing_date = existing_data.get('date', '')
                current_date = datetime.now().strftime('%Y-%m-%d')
                
                # 如果文件中的日期是今天，直接使用
                if existing_date == current_date:
                    file_size = os.path.getsize(json_file)
                    print(f"发现当天({current_date})的龙虎榜JSON文件，大小: {file_size} 字节")
                    return True
                else:
                    print(f"发现过时的龙虎榜数据({existing_date})，需要重新获取当天({current_date})数据")
                    # 继续执行爬虫获取新数据
            except Exception as e:
                print(f"检查现有文件时出错: {e}，继续执行爬虫")
                # 继续执行爬虫获取新数据
        
        # 判断当前时间，决定获取前一天还是当天的数据
        current_time = datetime.now()
        current_hour = current_time.hour
        current_weekday = current_time.weekday()  # 0=周一, 6=周日
        
        # 判断是否是工作日（周一到周五）
        is_weekday = current_weekday < 5
        
        print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"当前星期: {current_weekday + 1}")
        print(f"是否工作日: {'是' if is_weekday else '否'}")
        
        # 修改逻辑：如果是工作日，但时间较早（上午11点前），龙虎榜数据可能还未更新
        # 龙虎榜数据通常在交易日结束后才会更新，避免在数据未发布时强制获取当天数据
        if is_weekday and current_hour >= 11:
            print("工作日且时间较晚（11点后），优先尝试获取当天龙虎榜数据...")
            subprocess.run([sys.executable, "tdx_yzlhb_crawler.py", "--force-today"], shell=True)
        else:
            print("非工作日或时间较早（11点前），获取最近一个交易日的龙虎榜数据...")
            subprocess.run([sys.executable, "tdx_yzlhb_crawler.py"], shell=True)
        
        # 添加3秒延迟
        print("等待3秒，确保爬虫运行完毕...")
        time.sleep(3)
        
        # 再次检查top30文件
        if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
            file_size = os.path.getsize(json_file)
            print(f"龙虎榜爬虫运行成功，JSON文件已生成，大小: {file_size} 字节")
            return True
        
        # 尝试从data_file生成top30文件
        if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
            print(f"找到{data_file}文件，尝试处理...")
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    # 读取文件内容
                    file_content = f.read().strip()
                    
                    # 检查文件内容是否为有效的JSON
                    if file_content.startswith('{') and file_content.endswith('}'):
                        data = json.loads(file_content)
                        
                        # 安全获取数据
                        data_list = data.get('data', [])
                        if not isinstance(data_list, list):
                            print("警告: data字段不是列表类型")
                            data_list = []
                        
                        # 创建top30数据
                        top30_data = {
                            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                            'top_30_stocks': data_list[:30] if len(data_list) > 0 else []
                        }
                        
                        # 保存文件
                        with open(json_file, 'w', encoding='utf-8') as f_out:
                            json.dump(top30_data, f_out, ensure_ascii=False, indent=2)
                        
                        print(f"成功从{data_file}生成了{json_file}")
                        return True
                    else:
                        print(f"{data_file}内容不是有效的JSON格式")
                        # 创建一个空的JSON文件作为备用
                        with open(json_file, 'w', encoding='utf-8') as f_out:
                            json.dump({
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'top_30_stocks': []
                            }, f_out, ensure_ascii=False, indent=2)
                        print(f"已创建空的{json_file}作为备用")
                        return True
                
            except json.JSONDecodeError as e:
                print(f"解析{data_file}时出错: {e}")
                # 尝试创建一个基本的JSON文件
                create_basic_json(json_file)
                return True
            except Exception as e:
                print(f"处理{data_file}时出错: {e}")
                # 创建基本JSON文件
                create_basic_json(json_file)
                return True
        
        # 如果所有尝试都失败，创建一个基本的JSON文件
        print(f"没有找到可用的数据文件，创建基本的{json_file}")
        create_basic_json(json_file)
        return True
            
    except Exception as e:
        print(f"运行龙虎榜爬虫时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_basic_json(file_path):
    """创建一个基本的JSON文件"""
    try:
        basic_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'top_30_stocks': []
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(basic_data, f, ensure_ascii=False, indent=2)
        print(f"已创建基本JSON文件: {file_path}")
    except Exception as e:
        print(f"创建基本JSON文件时出错: {e}")

import time

def run_jiuyangongshe_crawler():
    """运行韭研公社爬虫并生成Markdown文件"""
    try:
        # 切换到脚本目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查目录是否有写入权限
        if not os.access(script_dir, os.W_OK):
            print("警告: 当前目录无写入权限")
        
        # 先尝试直接运行爬虫，不捕获输出以避免编码问题
        print("开始运行韭研公社爬虫...")
        subprocess.run([sys.executable, "jiuyangongshe_crawler.py"], shell=True)
        
        # 添加10秒延迟，确保爬虫完全运行完毕
        print("等待10秒，确保爬虫运行完毕...")
        time.sleep(10)
        
        # 检查是否成功生成了JSON文件
        json_file = "jiuyangongshe_news.json"
        if os.path.exists(json_file):
            file_size = os.path.getsize(json_file)
            print(f"韭研公社爬虫运行成功，JSON文件已生成，大小: {file_size} 字节")
            
            # 尝试直接导入并运行Markdown生成函数，避免再次使用subprocess
            try:
                # 尝试导入generate_stock_markdown函数
                import importlib.util
                spec = importlib.util.spec_from_file_location("generate_stock_md", "generate_stock_md.py")
                generate_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(generate_module)
                
                # 直接调用函数生成Markdown
                md_file = generate_module.generate_stock_markdown()
                if md_file and os.path.exists(md_file):
                    print(f"成功通过直接调用生成了Markdown文件: {md_file}")
                    return True
                else:
                    # 如果直接调用失败，尝试通过subprocess运行
                    print("直接调用生成Markdown失败，尝试通过subprocess运行...")
                    subprocess.run([sys.executable, "generate_stock_md.py"], shell=True)
                    
                    md_file = "jiuyangongshe_stocks.md"
                    if os.path.exists(md_file):
                        print("通过subprocess成功生成了韭研公社Markdown文件")
                        return True
                    else:
                        print("Markdown文件未生成")
                        return False
            except Exception as e:
                print(f"直接调用生成Markdown时出错: {e}，尝试通过subprocess运行...")
                subprocess.run([sys.executable, "generate_stock_md.py"], shell=True)
                
                md_file = "jiuyangongshe_stocks.md"
                if os.path.exists(md_file):
                    print("通过subprocess成功生成了韭研公社Markdown文件")
                    return True
                else:
                    print("Markdown文件未生成")
                    return False
        else:
            print("韭研公社JSON文件未生成，爬虫可能失败")
            # 尝试手动创建一个空的JSON文件作为备用
            try:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False)
                print("已创建空的JSON文件作为备用")
                # 尝试生成Markdown
                subprocess.run([sys.executable, "generate_stock_md.py"], shell=True)
                if os.path.exists("jiuyangongshe_stocks.md"):
                    print("使用空JSON文件成功生成了Markdown文件")
                    return True
            except Exception as e:
                print(f"创建备用JSON文件时出错: {e}")
            return False
            
    except Exception as e:
        print(f"运行韭研公社爬虫时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_lhb_markdown():
    """运行龙虎榜Markdown生成脚本"""
    try:
        # 切换到脚本目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"当前工作目录: {os.getcwd()}")
        print("开始生成龙虎榜Markdown文件...")
        
        # 定义文件路径
        md_file = "龙虎榜数据.md"
        script_file = "generate_lhb_markdown.py"
        json_file = "tdx_yzlhb_top30.json"
        
        # 检查JSON文件是否存在
        if not os.path.exists(json_file):
            print(f"警告: {json_file}不存在，可能无法生成完整的Markdown文件")
        
        # 检查JSON文件是否是最新的（比较JSON文件修改时间和当前时间）
        json_is_new = False
        if os.path.exists(json_file):
            json_mtime = os.path.getmtime(json_file)
            current_time = time.time()
            # 如果JSON文件是在最近5分钟内修改的，认为是新的
            if current_time - json_mtime < 300:  # 5分钟
                json_is_new = True
                print("JSON文件是最新的，需要重新生成Markdown文件")
        
        # 如果JSON文件是最新的，或者Markdown文件不存在，或者Markdown文件为空，则重新生成
        if json_is_new or not os.path.exists(md_file) or os.path.getsize(md_file) == 0:
            print("需要重新生成龙虎榜Markdown文件...")
            
            # 运行Markdown生成脚本
            if os.path.exists(script_file):
                subprocess.run([sys.executable, script_file], shell=True)
                
                # 添加2秒延迟
                time.sleep(2)
                
                # 检查文件是否生成
                if os.path.exists(md_file) and os.path.getsize(md_file) > 0:
                    file_size = os.path.getsize(md_file)
                    print(f"生成龙虎榜Markdown文件成功，大小: {file_size} 字节")
                    return True
            else:
                print(f"警告: {script_file}不存在")
            
            # 尝试直接导入并调用函数生成Markdown
            try:
                print("尝试直接导入模块生成Markdown...")
                import importlib.util
                
                # 尝试导入正确的模块名
                try:
                    spec = importlib.util.spec_from_file_location("generate_lhb_md", script_file)
                    generate_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(generate_module)
                    
                    # 调用模块中的函数
                    if hasattr(generate_module, "generate_lhb_markdown"):
                        generate_module.generate_lhb_markdown()
                    elif hasattr(generate_module, "main"):
                        generate_module.main()
                    
                    # 检查文件是否生成
                    if os.path.exists(md_file) and os.path.getsize(md_file) > 0:
                        print(f"成功通过直接调用生成了Markdown文件: {md_file}")
                        return True
                except Exception as e:
                    print(f"导入模块时出错: {e}")
            except Exception as e:
                print(f"直接调用生成Markdown时出错: {e}")
            
            # 创建备用Markdown文件
            print("创建备用Markdown文件...")
            create_basic_lhb_markdown(md_file)
            return True
        
        # 如果不需要重新生成，直接返回成功
        else:
            file_size = os.path.getsize(md_file)
            print(f"使用现有的龙虎榜Markdown文件，大小: {file_size} 字节")
            return True
            
    except Exception as e:
        print(f"生成龙虎榜Markdown文件时出错: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试创建备用文件
        try:
            create_basic_lhb_markdown("龙虎榜数据.md")
            return True
        except:
            return False

def create_basic_lhb_markdown(file_path):
    """创建一个基本的龙虎榜Markdown文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# 龙虎榜数据报告\n\n")
            f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 注意\n")
            f.write("由于数据处理问题，当前报告为基本版本。\n\n")
            f.write("## 龙虎榜数据\n")
            f.write("数据正在更新中...\n")
        print(f"已创建基本龙虎榜Markdown文件: {file_path}")
        return True
    except Exception as e:
        print(f"创建基本龙虎榜Markdown文件时出错: {e}")
        return False


def generate_lhb_csv(json_file_path, csv_file_path):
    """
    生成龙虎榜CSV文件
    
    Args:
        json_file_path: JSON文件路径
        csv_file_path: CSV文件路径
    """
    try:
        # 检查JSON文件是否存在
        if not os.path.exists(json_file_path):
            print(f"错误: JSON文件 {json_file_path} 不存在")
            return False
        
        # 读取JSON数据
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stocks = data.get('top_30_stocks', [])
        data_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 定义CSV字段
        fieldnames = ['rank', 'stock_code', 'stock_name', 'buyers', 'change_percent', 'net_buy_amount', 'date']
        
        # 写入CSV文件
        with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, stock in enumerate(stocks, 1):
                # 格式化数据
                rank = str(i)  # 排名
                stock_code = stock.get('gpdm', '')  # 股票代码
                stock_name = stock.get('gpmc', '')  # 股票名称
                buyers = stock.get('yzmc', '')  # 购买人
                
                # 格式化涨跌幅为文本格式，如 "10.00%"
                change_percent = f"{stock.get('zdf', 0):.2f}%"
                
                # 格式化净买入金额为文本格式，如 "3.93亿"
                net_buy_amount_value = stock.get('jmr', 0)
                if abs(net_buy_amount_value) >= 100000000:
                    net_buy_amount = f"{net_buy_amount_value/100000000:.2f}亿"
                elif abs(net_buy_amount_value) >= 10000:
                    net_buy_amount = f"{net_buy_amount_value/10000:.2f}万"
                else:
                    net_buy_amount = f"{net_buy_amount_value:.2f}元"
                
                date = data_date  # 日期
                
                # 写入行数据
                writer.writerow({
                    'rank': rank,
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'buyers': buyers,
                    'change_percent': change_percent,
                    'net_buy_amount': net_buy_amount,
                    'date': date
                })
        
        print(f"成功生成龙虎榜CSV文件: {csv_file_path}")
        return True
        
    except Exception as e:
        print(f"生成龙虎榜CSV文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"开始执行自动任务: {current_time}")
        
        # 1. 运行龙虎榜爬虫
        if not run_lhb_crawler():
            print("龙虎榜爬虫运行失败，任务终止")
            return
        
        # 2. 生成龙虎榜Markdown文件
        if not run_lhb_markdown():
            print("龙虎榜Markdown生成失败，任务终止")
            return
        
        # 3. 运行韭研公社爬虫并生成Markdown文件
        if not run_jiuyangongshe_crawler():
            print("韭研公社爬虫运行失败，任务终止")
            return
        
        # 4. 生成龙虎榜CSV文件
        json_file = "tdx_yzlhb_top30.json"
        csv_file = "龙虎榜数据.csv"
        if not generate_lhb_csv(json_file, csv_file):
            print("龙虎榜CSV文件生成失败")
            # 即使CSV生成失败，我们仍然继续执行其他任务
        
        # 5. 显示任务完成信息
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stocks = data.get('top_30_stocks', [])
            total_net_buy = sum(stock.get('jmr', 0) for stock in stocks)
            
            # 判断数据日期类型
            data_date = data.get('date', '未知')
            current_datetime = datetime.now()
            
            # 判断是否是当天数据
            if data_date == current_datetime.strftime('%Y-%m-%d'):
                date_description = "当天"
            else:
                date_description = "前一天"
            
            print(f"\n=== 任务执行完成 ===")
            print(f"执行时间: {current_time}")
            print(f"数据日期: {data_date} ({date_description})")
            print(f"龙虎榜股票数量: {len(stocks)}只")
            print(f"总净买入金额: {total_net_buy/100000000:.2f}亿")
            print(f"生成的文件:")
            print(f"- {json_file}")
            print(f"- 龙虎榜数据.md")
            print(f"- {csv_file}")
            print(f"- jiuyangongshe_stocks.md")
            print("=== 任务完成 ===\n")
        else:
            print("JSON文件不存在，但其他任务已完成")
            
    except Exception as e:
        print(f"自动任务执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()