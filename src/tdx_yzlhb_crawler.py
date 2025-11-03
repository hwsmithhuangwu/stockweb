#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同花顺游资龙虎榜爬虫
爬取 http://page.tdx.com.cn:7615/site/kggx/tk_yzlhb_yz.html 上的游资龙虎榜信息
"""

print("模块开始加载")

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

print("模块导入完成")

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置为DEBUG级别以查看更多详细信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tdx_yzlhb_crawler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class TDXYZLHBSpider:
    """同花顺游资龙虎榜爬虫"""
    
    def __init__(self):
        print("TDXYZLHBSpider.__init__开始执行")
        self.base_url = "http://page.tdx.com.cn:7615"
        self.api_url = f"{self.base_url}/tdx/Exec"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'{self.base_url}/site/kggx/tk_yzlhb_yz.html',
            'Origin': self.base_url
        })
        print("TDXYZLHBSpider.__init__执行完成")
    
    def call_api(self, func_name: str, params: List[Any], reqtype: str = "cwserv") -> Optional[Dict[str, Any]]:
        """
        调用同花顺API
        
        Args:
            func_name: 函数名
            params: 参数列表
            reqtype: 请求类型
            
        Returns:
            API响应数据
        """
        try:
            # 格式化参数（按照JavaScript中的FormatParams函数格式）
            params_str = '"Params":['
            param_list = []
            for param in params:
                if isinstance(param, str):
                    param_list.append(f'"{param}"')
                elif isinstance(param, (int, float)):
                    param_list.append(str(param))
                else:
                    param_list.append(f'"{str(param)}"')
            
            params_str += ','.join(param_list) + ']'
            
            # 构建请求参数
            data = {
                'funcid': f"CWServ.{func_name}",
                'bodystr': '{' + params_str + '}',
                'timeout': 30000
            }
            
            # 添加随机参数避免缓存
            import random
            data['_'] = str(int(time.time() * 1000))
            data['rnd'] = str(random.randint(1000, 9999))
            
            logger.info(f"调用API: {func_name}, 参数: {params}")
            
            response = self.session.get(self.api_url, params=data, timeout=30)
            response.raise_for_status()
            
            # 正确处理编码问题
            try:
                response_text = response.content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    response_text = response.content.decode('gbk')
                except UnicodeDecodeError:
                    response_text = response.text
            
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应内容前500字符: {response_text[:500]}")
            
            # 解析响应
            if response_text.startswith("success|"):
                json_str = response_text[8:]  # 去掉 "success|" 前缀
                result = json.loads(json_str)
                
                if result.get("ErrorCode") == 0:
                    logger.info(f"API调用成功")
                    return result
                else:
                    logger.error(f"API返回错误: {result.get('ErrorInfo', 'Unknown error')}")
                    return None
            else:
                # 尝试直接解析JSON响应（有些响应可能没有success|前缀）
                try:
                    result = json.loads(response_text)
                    print(f"直接解析JSON结果类型: {type(result)}")
                    print(f"直接解析JSON结果: {result}")
                    if result.get("ErrorCode") == 0:
                        logger.info(f"API调用成功（无success前缀）")
                        return result
                    else:
                        logger.error(f"API返回错误: {result.get('ErrorInfo', 'Unknown error')}")
                        return None
                except json.JSONDecodeError:
                    logger.error(f"API响应格式错误: {response_text[:200]}")
                    return None
                
        except requests.RequestException as e:
            logger.error(f"网络请求错误: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None
    
    def get_yzlhb_data(self, date_str: Optional[str] = None, type_code: str = "jm", sort_field: str = "jmr") -> Optional[Dict[str, Any]]:
        """
        获取游资龙虎榜数据
        
        Args:
            date_str: 日期字符串 (格式: YYYY-MM-DD)，默认为当天
            type_code: 类型代码 ("pt"-普通, "jm"-游资, "jg"-机构)
            sort_field: 排序字段 ("jmr"-净买入, "zdf"-涨跌幅等)
            
        Returns:
            游资龙虎榜数据
        """
        print(f"进入get_yzlhb_data方法，date_str: {date_str}, type_code: {type_code}, sort_field: {sort_field}")
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            print(f"日期未指定，使用默认日期: {date_str}")
        
        # 调用游资龙虎榜接口
        # 参数: [类型, 日期, 排序方式, 页码]
        # 类型: "pt"-普通, "jm"-游资, "jg"-机构
        # 尝试不同的参数组合
        params = [type_code, date_str, sort_field, 1]  # 使用指定类型获取数据
        print(f"准备调用API，参数: {params}")
        
        result = self.call_api("cfg_fx_yzlhb_lhb", params)
        
        print(f"call_api返回结果类型: {type(result)}")
        print(f"call_api返回结果: {result}")
        
        # 检查result是否为None
        if result is None:
            print("call_api返回了None")
            return None
            
        # 检查result中是否有tables或ResultSets字段
        if "tables" in result:
            table_key = "tables"
        elif "ResultSets" in result:
            table_key = "ResultSets"
        else:
            print(f"result中没有tables或ResultSets字段，result的keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
            return None
            
        if len(result[table_key]) == 0:
            print(f"{table_key}列表为空")
            return None
            
        if result and table_key in result and len(result[table_key]) > 0:
                table_data = result[table_key][0]
                # 打印完整的表结构信息
                print(f"表结构信息: {table_data}")
                
                # 检查数据结构
                if "Content" in table_data:
                    rows = table_data.get("Content", [])
                    print(f"使用Content字段，获取到 {len(rows)} 条数据")
                elif "rows" in table_data:
                    rows = table_data.get("rows", [])
                    print(f"使用rows字段，获取到 {len(rows)} 条数据")
                else:
                    print(f"table_data中没有Content或rows字段，keys: {table_data.keys()}")
                    rows = []
                
                col_names = table_data.get("ColName", [])
                print(f"列名: {col_names}")
                logger.debug(f"获取到 {len(rows)} 条原始数据")
                
                # 解析二维数组数据
                parsed_rows = []
                
                # 在解析开始前添加明显的分隔符
                print("\n" + "="*50)
                print("开始解析原始数据")
                print("="*50)
                
                for i, row in enumerate(rows):
                    # 打印完整的行数据用于调试
                    print(f"第{i+1}行完整数据: {row}")
                    
                    if len(row) >= 3:  # 至少包含市场代码、股票代码、股票名称
                        try:
                            # 根据用户提供的完整数据结构:
                            # ['0', '深科技', '000021', 'dr', 190430079, 'T王,机构专用,欢乐海岸,深股通专用', '9.98']
                            # 索引0: '0' - 市场代码
                            # 索引1: '深科技' - 股票名称  
                            # 索引2: '000021' - 股票代码
                            # 索引3: 'dr' - 上榜类型
                            # 索引4: 190430079 - 净买入数据
                            # 索引5: 'T王,机构专用,欢乐海岸,深股通专用' - 购买人
                            # 索引6: '9.98' - 涨跌幅（9.98%）
                            
                            parsed_row = {
                                "sc": row[0] if len(row) > 0 else "",  # 市场代码
                                "gpmc": row[1] if len(row) > 1 else "",  # 股票名称
                                "gpdm": row[2] if len(row) > 2 else "",  # 股票代码
                                "sblx": row[3] if len(row) > 3 else "",  # 上榜类型
                                "jmr": float(row[4]) if len(row) > 4 and row[4] else 0,  # 净买入
                                "yzmc": row[5] if len(row) > 5 else "未知",  # 购买人
                                "zdf": float(row[6]) if len(row) > 6 and row[6] else 0,  # 涨跌幅
                            }
                            
                            parsed_rows.append(parsed_row)
                            print(f"成功解析第{i+1}行数据: {parsed_row}")
                        except Exception as e:
                            print(f"解析第{i+1}行数据失败: {e}")
                
                # 在解析结束后添加明显的分隔符
                print("="*50)
                print("解析完成")
                print("="*50 + "\n")
                
                logger.info(f"原始数据行数: {len(rows)}")
                logger.info(f"解析后数据行数: {len(parsed_rows)}")
                if parsed_rows:
                    logger.info(f"解析后的第一条数据: {parsed_rows[0]}")
                return parsed_rows
        
        logger.warning(f"API返回数据格式异常: {result}")
        return None
    
    def get_yz_detail_data(self, date_str: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取游资详情数据
        
        Args:
            date_str: 日期字符串 (格式: YYYY-MM-DD)，默认为当天
            
        Returns:
            游资详情数据
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 调用游资详情接口
        params = [date_str]
        
        result = self.call_api("cfg_fx_yzlhb_yz", params)
        
        if result and "tables" in result and len(result["tables"]) > 0:
            return result["tables"][0].get("rows", [])
        
        return None
    
    def parse_stock_data(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        解析股票数据
        
        Args:
            raw_data: 原始数据
            
        Returns:
            解析后的股票数据
        """
        parsed_data = []
        
        for item in raw_data:
            stock_info = {
                "股票代码": item.get("gpdm", ""),
                "股票名称": item.get("gpmc", ""),
                "市场代码": item.get("sc", ""),
                "涨幅": item.get("zdf", 0),
                "净买入": item.get("jmr", 0),
                "购买人": item.get("yzmc", "未知"),
                "上榜类型": item.get("sblx", ""),
            }
            parsed_data.append(stock_info)
        
        return parsed_data
    
    def parse_yz_data(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        解析游资数据
        
        Args:
            raw_data: 原始数据
            
        Returns:
            解析后的游资数据
        """
        parsed_data = []
        
        for item in raw_data:
            yz_info = {
                "游资名称": item.get("yzmc", ""),
                "操作股票": item.get("gpmc", ""),
                "股票代码": item.get("gpdm", ""),
                "市场代码": item.get("sc", ""),
                "净买入": item.get("jmr", 0),
                "买入金额": item.get("mrje", 0),
                "卖出金额": item.get("mcje", 0),
                "上榜日期": item.get("rq", "")
            }
            parsed_data.append(yz_info)
        
        return parsed_data
    
    def crawl_recent_data(self, days: int = 5) -> Dict[str, Any]:
        """
        爬取最近几天的数据
        
        Args:
            days: 天数
            
        Returns:
            包含多天数据的字典
        """
        result = {
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": {}
        }
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            logger.info(f"爬取 {date_str} 的数据...")
            
            # 获取游资龙虎榜数据，尝试不同的参数组合
            stock_data = None
            # 尝试不同的参数组合
            test_cases = [
                ("jm", "jmr"),  # 游资类型，按净买入排序
                ("pt", "jmr"),  # 普通类型，按净买入排序
                ("jg", "jmr"),  # 机构类型，按净买入排序
                ("jm", "zdf"),  # 游资类型，按涨跌幅排序
            ]
            
            print(f"在crawl_recent_data中尝试不同的参数组合，日期: {date_str}")
            for type_code, sort_field in test_cases:
                print(f"调用get_yzlhb_data({date_str}, {type_code}, {sort_field})")
                stock_data = self.get_yzlhb_data(date_str, type_code, sort_field)
                if stock_data and len(stock_data) > 0:
                    logger.info(f"使用参数组合 类型={type_code}, 排序={sort_field} 获取到数据")
                    break
            
            if stock_data:
                parsed_stocks = self.parse_stock_data(stock_data)
                result["data"][date_str] = {
                    "stocks": parsed_stocks,
                    "stock_count": len(parsed_stocks)
                }
            else:
                result["data"][date_str] = {
                    "stocks": [],
                    "stock_count": 0
                }
            
            # 获取游资详情数据
            yz_data = self.get_yz_detail_data(date_str)
            if yz_data:
                parsed_yz = self.parse_yz_data(yz_data)
                result["data"][date_str]["yz_details"] = parsed_yz
                result["data"][date_str]["yz_count"] = len(parsed_yz)
            else:
                result["data"][date_str]["yz_details"] = []
                result["data"][date_str]["yz_count"] = 0
            
            # 避免请求过于频繁
            time.sleep(1)
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], filename: str = "tdx_yzlhb_data.json"):
        """
        保存数据到JSON文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
    
    def print_summary(self, data: Dict[str, Any]):
        """
        打印数据摘要
        
        Args:
            data: 爬取的数据
        """
        print("=== 同花顺游资龙虎榜数据摘要 ===")
        print(f"爬取时间: {data.get('crawl_time', 'N/A')}")
        print()
        
        for date_str, date_data in data.get("data", {}).items():
            print(f"日期: {date_str}")
            print(f"  上榜股票数量: {date_data.get('stock_count', 0)}")
            print(f"  游资操作记录: {date_data.get('yz_count', 0)}")
            
            # 显示前几个股票
            stocks = date_data.get("stocks", [])[:3]
            if stocks:
                print("  上榜股票(前3个):")
                for stock in stocks:
                    print(f"    - {stock.get('股票名称', 'N/A')} ({stock.get('股票代码', 'N/A')}): "
                          f"涨幅 {stock.get('涨幅', 0)}%, 净买入 {stock.get('净买入', 0):.2f}万")
            
            # 显示前几个游资
            yz_details = date_data.get("yz_details", [])[:3]
            if yz_details:
                print("  游资操作(前3个):")
                for yz in yz_details:
                    print(f"    - {yz.get('游资名称', 'N/A')}: "
                          f"操作 {yz.get('操作股票', 'N/A')}, 净买入 {yz.get('净买入', 0):.2f}万")
            
            print()


def format_number(num):
    """格式化数字显示，将净买入金额转换为亿单位"""
    if num >= 100000000:  # 大于等于1亿
        return f"{num/100000000:.2f}亿"
    elif num >= 10000:  # 大于等于1万
        return f"{num/10000:.2f}万"
    else:
        return str(num)


def main(days_to_fetch=1):
    """主函数 - 获取净买入前30的股票信息，自动查找最新可用数据
    
    Args:
        days_to_fetch: 要获取的天数，默认为1天(只获取最新的一天数据)
    """
    import sys
    import time
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='同花顺游资龙虎榜数据爬虫')
    parser.add_argument('--days', type=int, default=days_to_fetch, 
                        help='要获取的天数，默认为1天')
    parser.add_argument('--force-today', action='store_true', 
                        help='强制尝试获取当天数据')
    args = parser.parse_args()
    days_to_fetch = max(1, min(30, args.days))  # 限制在1-30天范围内
    force_today = args.force_today
    
    print(f"=== 开始获取最近{days_to_fetch}天的龙虎榜数据 ===")
    
    spider = TDXYZLHBSpider()
    
    # 获取日期
    from datetime import datetime, timedelta
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    # 定义参数组合，用于尝试不同的数据获取方式
    param_combinations = [
        ("jm", "jmr"),  # 游资类型，按净买入排序
        ("pt", "jmr"),  # 普通类型，按净买入排序
        ("jg", "jmr"),  # 机构类型，按净买入排序
        ("jm", "zdf"),  # 游资类型，按涨跌幅排序
    ]
    
    # 最大尝试天数（往前查找最近的数据）
    max_attempt_days = 30  # 增加到30天以覆盖更长的假期
    all_stock_data = {}
    success_days = 0
    
    # 优先尝试获取当天数据（工作日下午4点后通常有数据）
    current_hour = today.hour
    current_minute = today.minute
    current_time = current_hour * 60 + current_minute
    target_time = 16 * 60  # 下午4点
    
    # 如果是工作日且时间在下午4点后，或者强制获取当天数据，则首先尝试今天
    is_weekday = today.weekday() < 5  # 0-4表示周一到周五
    
    # 修改逻辑：如果当前是工作日，无论时间都优先尝试获取当天数据
    # 因为龙虎榜数据通常在交易日结束后就会更新
    attempt_today_first = force_today or is_weekday
    
    if attempt_today_first:
        print(f"优先尝试获取当天数据: {today_str}")
        found_today = False
        
        # 尝试所有参数组合获取今天的数据
        for type_code, sort_field in param_combinations:
            print(f"  尝试参数组合: 类型={type_code}, 排序={sort_field}")
            try:
                temp_data = spider.get_yzlhb_data(today_str, type_code, sort_field)
                
                if temp_data is not None and len(temp_data) > 0:
                    print(f"  ✅ 成功获取到当天数据，共{len(temp_data)}条")
                    all_stock_data[today_str] = temp_data
                    success_days += 1
                    found_today = True
                    break
                else:
                    print(f"  ❌ 未获取到当天数据")
            except Exception as e:
                print(f"  ❌ 获取当天数据出错: {e}")
                # 继续尝试下一个参数组合
        
        if found_today:
            print(f"  ✅ 成功获取当天龙虎榜数据")
        else:
            print(f"  ⚠️ 未能获取到当天数据，将尝试获取历史数据")
    
    # 如果当天数据未获取到或需要获取更多天数的数据，则从昨天开始往前查找
    if success_days < days_to_fetch:
        print(f"\n开始查找历史数据，还需获取{days_to_fetch - success_days}天的数据")
        
        for days_ago in range(1, max_attempt_days + 1):
            if success_days >= days_to_fetch:
                break
                
            current_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # 跳过已经获取到的日期
            if current_date in all_stock_data:
                continue
                
            print(f"尝试获取日期: {current_date} (前{days_ago}天)")
            
            # 尝试所有参数组合
            found_for_date = False
            for type_code, sort_field in param_combinations:
                print(f"  尝试参数组合: 类型={type_code}, 排序={sort_field}")
                try:
                    temp_data = spider.get_yzlhb_data(current_date, type_code, sort_field)
                    
                    if temp_data is not None and len(temp_data) > 0:
                        print(f"  ✅ 成功获取到数据，共{len(temp_data)}条")
                        all_stock_data[current_date] = temp_data
                        success_days += 1
                        found_for_date = True
                        break
                    else:
                        print(f"  ❌ 未获取到数据")
                except Exception as e:
                    print(f"  ❌ 请求出错: {e}")
                    # 继续尝试下一个参数组合
            
            if not found_for_date:
                print(f"  ⚠️ 该日期所有参数组合均未获取到数据")
            
            # 避免请求过于频繁
            time.sleep(1)
    
    if all_stock_data:
        print(f"\n=== 成功获取到{success_days}天的龙虎榜数据 ===")
        
        # 处理每一天的数据
        latest_date = None
        all_top_stocks = []
        
        for date_str in sorted(all_stock_data.keys(), reverse=True):
            if latest_date is None:
                latest_date = date_str
                
            stock_data = all_stock_data[date_str]
            print(f"\n日期: {date_str}")
            print(f"数据条数: {len(stock_data)}")
            
            # 按净买入金额排序并取前30
            sorted_stocks = sorted(stock_data, key=lambda x: x.get('jmr', 0), reverse=True)
            top_30 = sorted_stocks[:30]
            all_top_stocks.extend(top_30)
            
            # 只打印最新一天的详细排名
            if date_str == latest_date:
                print(f"\n=== 净买入前30的股票信息 (日期: {date_str}) ===")
                print("排名 | 股票名称 | 股票代码 | 购买人 | 涨跌幅 | 净买入")
                print("-" * 80)
                
                for i, stock in enumerate(top_30, 1):
                    # 确保所有字符串值都存在且不为None
                    stock_name = str(stock.get('gpmc', '')).strip()
                    stock_code = str(stock.get('gpdm', '')).strip()
                    buyer = str(stock.get('yzmc', '未知')).strip()
                    
                    # 确保change_rate是一个有效的浮点数
                    change_rate_val = stock.get('zdf')
                    try:
                        change_rate = float(change_rate_val) if change_rate_val is not None else 0.0
                    except (ValueError, TypeError):
                        change_rate = 0.0
                    
                    # 确保net_buy是一个有效的浮点数
                    net_buy_val = stock.get('jmr')
                    try:
                        net_buy = float(net_buy_val) if net_buy_val is not None else 0.0
                    except (ValueError, TypeError):
                        net_buy = 0.0
                    
                    formatted_net_buy = format_number(net_buy)
                    
                    # 使用安全的格式化
                    print(f"{i:2d}   | {stock_name[:8]:8s} | {stock_code[:8]:8s} | {buyer[:30]:30s} | {change_rate:6.2f}% | {formatted_net_buy}")
                
                print("-" * 80)
        
        # 保存最新一天的数据到主文件
        latest_data = all_stock_data[latest_date]
        sorted_latest_stocks = sorted(latest_data, key=lambda x: x.get('jmr', 0), reverse=True)
        latest_top_30 = sorted_latest_stocks[:30]
        
        result_data = {
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": latest_date,
            "top_30_stocks": latest_top_30,
            "days_fetched": success_days
        }
        
        spider.save_to_json(result_data, "tdx_yzlhb_top30.json")
        print(f"\n最新数据已保存到 tdx_yzlhb_top30.json")
        
        # 同时更新tdx_yzlhb_data.json文件
        full_data = {
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": latest_date,
            "data": latest_top_30,
            "days_fetched": success_days
        }
        spider.save_to_json(full_data, "tdx_yzlhb_data.json")
        print("最新数据已保存到 tdx_yzlhb_data.json")
        
        # 如果获取了多天数据，额外保存完整历史数据
        if len(all_stock_data) > 1:
            historical_data = {
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "days_fetched": success_days,
                "data_by_date": {}
            }
            
            for date_str, stocks in all_stock_data.items():
                sorted_stocks = sorted(stocks, key=lambda x: x.get('jmr', 0), reverse=True)
                historical_data["data_by_date"][date_str] = sorted_stocks[:30]
            
            spider.save_to_json(historical_data, f"tdx_yzlhb_history_{success_days}d.json")
            print(f"历史数据已保存到 tdx_yzlhb_history_{success_days}d.json")
        
        # 简单统计分析
        print("\n=== 数据统计分析 ===")
        print(f"总共获取到{len(all_top_stocks)}条记录")
        
        # 计算平均净买入金额
        total_net_buy = sum(stock.get('jmr', 0) for stock in all_top_stocks)
        avg_net_buy = total_net_buy / len(all_top_stocks) if all_top_stocks else 0
        print(f"平均净买入金额: {format_number(avg_net_buy)}")
        
        # 找出净买入最多的股票
        if all_top_stocks:
            max_buy_stock = max(all_top_stocks, key=lambda x: x.get('jmr', 0))
            print(f"净买入最多的股票: {max_buy_stock.get('gpmc', '')}({max_buy_stock.get('gpdm', '')}) - {format_number(max_buy_stock.get('jmr', 0))}")
            
    else:
        print(f"在最近{max_attempt_days}天内未获取到任何股票数据，请检查网络连接或API状态")
    
    print("\n程序执行完成")


print("检查__name__:", __name__)
if __name__ == "__main__":
    print("即将执行main函数")
    import sys
    sys.stderr.write("=== 程序入口开始执行 ===\n")
    sys.stderr.flush()
    try:
        main()
        print("main函数执行完成")
    except Exception as e:
        print(f"main函数执行出错: {e}")
        import traceback
        traceback.print_exc()