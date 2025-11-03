#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
韭研公社新闻爬虫
爬取网站：https://www.jiuyangongshe.com/
只爬取包含股票名称的新闻，并提取股票名称和相关信息
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

class JiuYanGongSheCrawler:
    """韭研公社新闻爬虫类"""
    
    def __init__(self):
        self.base_url = "https://www.jiuyangongshe.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        # 常见股票名称和代码模式
        self.stock_patterns = [
            # 股票代码模式（6位数字）
            r'\b(0|3|6)\d{5}\b',
            # 股票名称模式（2-4个中文字符）
            r'[\u4e00-\u9fa5]{2,4}(股份|集团|控股|科技|药业|银行|证券|保险|信托|基金|地产|建设|能源|电力|化工|机械|电子|通信|软件|网络|传媒|教育|医疗|旅游|食品|饮料|农业|林业|牧业|渔业|矿业|金属|钢铁|有色|煤炭|石油|燃气|水务|环保|交通|运输|物流|仓储|零售|批发|贸易|服务|咨询|设计|工程|建筑|装饰|家具|家电|汽车|摩托车|自行车|船舶|航空|航天|兵器|军工|医药|生物|基因|疫苗|诊断|器械|养老|健康|体育|文化|艺术|娱乐|游戏|动漫|影视|音乐|出版|报纸|广播|电视|广告|会展|酒店|餐饮|物业|租赁|商务|中介|代理|拍卖|典当|担保|小贷|租赁|投资|资产|管理|开发|实业|国际|中国|北京|上海|深圳|广州|天津|重庆|江苏|浙江|山东|福建|广东|湖南|湖北|河南|河北|四川|陕西|辽宁|吉林|黑龙江|安徽|江西|山西|云南|贵州|广西|海南|甘肃|宁夏|青海|新疆|西藏|内蒙古)\b',
            # 常见股票简称
            r'\b(茅台|五粮液|格力|美的|海尔|万科|保利|招商|平安|太保|国寿|新华|人保|太平|中信|光大|民生|浦发|兴业|华夏|广发|深发展|宁波|南京|北京|上海|深圳|广州|杭州|苏州|无锡|常州|南通|扬州|镇江|泰州|徐州|淮安|盐城|连云港|宿迁|绍兴|嘉兴|湖州|金华|衢州|舟山|台州|丽水|温州|福州|厦门|泉州|漳州|龙岩|三明|南平|宁德|莆田|济南|青岛|淄博|枣庄|东营|烟台|潍坊|济宁|泰安|威海|日照|临沂|德州|聊城|滨州|菏泽|郑州|开封|洛阳|平顶山|安阳|鹤壁|新乡|焦作|濮阳|许昌|漯河|三门峡|南阳|商丘|信阳|周口|驻马店|武汉|黄石|十堰|宜昌|襄阳|鄂州|荆门|孝感|荆州|黄冈|咸宁|随州|恩施|长沙|株洲|湘潭|衡阳|邵阳|岳阳|常德|张家界|益阳|郴州|永州|怀化|娄底|湘西|合肥|芜湖|蚌埠|淮南|马鞍山|淮北|铜陵|安庆|黄山|滁州|阜阳|宿州|六安|亳州|池州|宣城|南昌|景德镇|萍乡|九江|新余|鹰潭|赣州|吉安|宜春|抚州|上饶|石家庄|唐山|秦皇岛|邯郸|邢台|保定|张家口|承德|沧州|廊坊|衡水|太原|大同|阳泉|长治|晋城|朔州|晋中|运城|忻州|临汾|吕梁|呼和浩特|包头|乌海|赤峰|通辽|鄂尔多斯|呼伦贝尔|巴彦淖尔|乌兰察布|沈阳|大连|鞍山|抚顺|本溪|丹东|锦州|营口|阜新|辽阳|盘锦|铁岭|朝阳|葫芦岛|长春|吉林|四平|辽源|通化|白山|松原|白城|延边|哈尔滨|齐齐哈尔|鸡西|鹤岗|双鸭山|大庆|伊春|佳木斯|七台河|牡丹江|黑河|绥化|大兴安岭|南京|无锡|徐州|常州|苏州|南通|连云港|淮安|盐城|扬州|镇江|泰州|宿迁|杭州|宁波|温州|嘉兴|湖州|绍兴|金华|衢州|舟山|台州|丽水|合肥|芜湖|蚌埠|淮南|马鞍山|淮北|铜陵|安庆|黄山|滁州|阜阳|宿州|六安|亳州|池州|宣城|福州|厦门|莆田|三明|泉州|漳州|南平|龙岩|宁德|南昌|景德镇|萍乡|九江|新余|鹰潭|赣州|吉安|宜春|抚州|上饶|济南|青岛|淄博|枣庄|东营|烟台|潍坊|济宁|泰安|威海|日照|临沂|德州|聊城|滨州|菏泽|郑州|开封|洛阳|平顶山|安阳|鹤壁|新乡|焦作|濮阳|许昌|漯河|三门峡|南阳|商丘|信阳|周口|驻马店|武汉|黄石|十堰|宜昌|襄阳|鄂州|荆门|孝感|荆州|黄冈|咸宁|随州|恩施|长沙|株洲|湘潭|衡阳|邵阳|岳阳|常德|张家界|益阳|郴州|永州|怀化|娄底|湘西|广州|韶关|深圳|珠海|汕头|佛山|江门|湛江|茂名|肇庆|惠州|梅州|汕尾|河源|阳江|清远|东莞|中山|潮州|揭阳|云浮|南宁|柳州|桂林|梧州|北海|防城港|钦州|贵港|玉林|百色|贺州|河池|来宾|崇左|海口|三亚|三沙|儋州|成都|自贡|攀枝花|泸州|德阳|绵阳|广元|遂宁|内江|乐山|南充|眉山|宜宾|广安|达州|雅安|巴中|资阳|阿坝|甘孜|凉山|贵阳|六盘水|遵义|安顺|毕节|铜仁|黔西南|黔东南|黔南|昆明|曲靖|玉溪|保山|昭通|丽江|普洱|临沧|楚雄|红河|文山|西双版纳|大理|德宏|怒江|迪庆|拉萨|昌都|山南|日喀则|那曲|阿里|林芝|西安|铜川|宝鸡|咸阳|渭南|延安|汉中|榆林|安康|商洛|兰州|嘉峪关|金昌|白银|天水|武威|张掖|平凉|酒泉|庆阳|定西|陇南|临夏|甘南|西宁|海东|海北|黄南|海南|果洛|玉树|海西|银川|石嘴山|吴忠|固原|中卫|乌鲁木齐|克拉玛依|吐鲁番|哈密|昌吉|博尔塔拉|巴音郭楞|阿克苏|克孜勒苏|喀什|和田|伊犁|塔城|阿勒泰)\b'
        ]
    
    def extract_stock_info(self, text: str) -> List[Dict]:
        """从文本中提取股票名称和代码信息"""
        stock_info = []
        
        # 检查股票代码
        code_pattern = r'\b(0|3|6)\d{5}\b'
        code_matches = re.findall(code_pattern, text)
        for code in code_matches:
            stock_info.append({
                'type': 'code',
                'value': code,
                'description': f'股票代码: {code}'
            })
        
        # 检查股票名称
        name_pattern = r'[\u4e00-\u9fa5]{2,4}(股份|集团|控股|科技|药业|银行|证券|保险|信托|基金|地产|建设|能源|电力|化工|机械|电子|通信|软件|网络|传媒|教育|医疗|旅游|食品|饮料|农业|林业|牧业|渔业|矿业|金属|钢铁|有色|煤炭|石油|燃气|水务|环保|交通|运输|物流|仓储|零售|批发|贸易|服务|咨询|设计|工程|建筑|装饰|家具|家电|汽车|摩托车|自行车|船舶|航空|航天|兵器|军工|医药|生物|基因|疫苗|诊断|器械|养老|健康|体育|文化|艺术|娱乐|游戏|动漫|影视|音乐|出版|报纸|广播|电视|广告|会展|酒店|餐饮|物业|租赁|商务|中介|代理|拍卖|典当|担保|小贷|租赁|投资|资产|管理|开发|实业|国际|中国|北京|上海|深圳|广州|天津|重庆|江苏|浙江|山东|福建|广东|湖南|湖北|河南|河北|四川|陕西|辽宁|吉林|黑龙江|安徽|江西|山西|云南|贵州|广西|海南|甘肃|宁夏|青海|新疆|西藏|内蒙古)\b'
        name_matches = re.findall(name_pattern, text)
        for name in name_matches:
            stock_info.append({
                'type': 'name',
                'value': name,
                'description': f'股票名称: {name}'
            })
        
        # 检查常见股票简称
        short_pattern = r'\b(茅台|五粮液|格力|美的|海尔|万科|保利|招商|平安|太保|国寿|新华|人保|太平|中信|光大|民生|浦发|兴业|华夏|广发|深发展|宁波|南京|北京|上海|深圳|广州|杭州|苏州|无锡|常州|南通|扬州|镇江|泰州|徐州|淮安|盐城|连云港|宿迁|绍兴|嘉兴|湖州|金华|衢州|舟山|台州|丽水|温州|福州|厦门|泉州|漳州|龙岩|三明|南平|宁德|莆田|济南|青岛|淄博|枣庄|东营|烟台|潍坊|济宁|泰安|威海|日照|临沂|德州|聊城|滨州|菏泽|郑州|开封|洛阳|平顶山|安阳|鹤壁|新乡|焦作|濮阳|许昌|漯河|三门峡|南阳|商丘|信阳|周口|驻马店|武汉|黄石|十堰|宜昌|襄阳|鄂州|荆门|孝感|荆州|黄冈|咸宁|随州|恩施|长沙|株洲|湘潭|衡阳|邵阳|岳阳|常德|张家界|益阳|郴州|永州|怀化|娄底|湘西|合肥|芜湖|蚌埠|淮南|马鞍山|淮北|铜陵|安庆|黄山|滁州|阜阳|宿州|六安|亳州|池州|宣城|南昌|景德镇|萍乡|九江|新余|鹰潭|赣州|吉安|宜春|抚州|上饶|石家庄|唐山|秦皇岛|邯郸|邢台|保定|张家口|承德|沧州|廊坊|衡水|太原|大同|阳泉|长治|晋城|朔州|晋中|运城|忻州|临汾|吕梁|呼和浩特|包头|乌海|赤峰|通辽|鄂尔多斯|呼伦贝尔|巴彦淖尔|乌兰察布|沈阳|大连|鞍山|抚顺|本溪|丹东|锦州|营口|阜新|辽阳|盘锦|铁岭|朝阳|葫芦岛|长春|吉林|四平|辽源|通化|白山|松原|白城|延边|哈尔滨|齐齐哈尔|鸡西|鹤岗|双鸭山|大庆|伊春|佳木斯|七台河|牡丹江|黑河|绥化|大兴安岭|南京|无锡|徐州|常州|苏州|南通|连云港|淮安|盐城|扬州|镇江|泰州|宿迁|杭州|宁波|温州|嘉兴|湖州|绍兴|金华|衢州|舟山|台州|丽水|合肥|芜湖|蚌埠|淮南|马鞍山|淮北|铜陵|安庆|黄山|滁州|阜阳|宿州|六安|亳州|池州|宣城|福州|厦门|莆田|三明|泉州|漳州|南平|龙岩|宁德|南昌|景德镇|萍乡|九江|新余|鹰潭|赣州|吉安|宜春|抚州|上饶|济南|青岛|淄博|枣庄|东营|烟台|潍坊|济宁|泰安|威海|日照|临沂|德州|聊城|滨州|菏泽|郑州|开封|洛阳|平顶山|安阳|鹤壁|新乡|焦作|濮阳|许昌|漯河|三门峡|南阳|商丘|信阳|周口|驻马店|武汉|黄石|十堰|宜昌|襄阳|鄂州|荆门|孝感|荆州|黄冈|咸宁|随州|恩施|长沙|株洲|湘潭|衡阳|邵阳|岳阳|常德|张家界|益阳|郴州|永州|怀化|娄底|湘西|广州|韶关|深圳|珠海|汕头|佛山|江门|湛江|茂名|肇庆|惠州|梅州|汕尾|河源|阳江|清远|东莞|中山|潮州|揭阳|云浮|南宁|柳州|桂林|梧州|北海|防城港|钦州|贵港|玉林|百色|贺州|河池|来宾|崇左|海口|三亚|三沙|儋州|成都|自贡|攀枝花|泸州|德阳|绵阳|广元|遂宁|内江|乐山|南充|眉山|宜宾|广安|达州|雅安|巴中|资阳|阿坝|甘孜|凉山|贵阳|六盘水|遵义|安顺|毕节|铜仁|黔西南|黔东南|黔南|昆明|曲靖|玉溪|保山|昭通|丽江|普洱|临沧|楚雄|红河|文山|西双版纳|大理|德宏|怒江|迪庆|拉萨|昌都|山南|日喀则|那曲|阿里|林芝|西安|铜川|宝鸡|咸阳|渭南|延安|汉中|榆林|安康|商洛|兰州|嘉峪关|金昌|白银|天水|武威|张掖|平凉|酒泉|庆阳|定西|陇南|临夏|甘南|西宁|海东|海北|黄南|海南|果洛|玉树|海西|银川|石嘴山|吴忠|固原|中卫|乌鲁木齐|克拉玛依|吐鲁番|哈密|昌吉|博尔塔拉|巴音郭楞|阿克苏|克孜勒苏|喀什|和田|伊犁|塔城|阿勒泰)\b'
        short_matches = re.findall(short_pattern, text)
        for short_name in short_matches:
            stock_info.append({
                'type': 'short_name',
                'value': short_name,
                'description': f'股票简称: {short_name}'
            })
        
        return stock_info
    
    def contains_stock_info(self, text: str) -> bool:
        """检查文本是否包含股票信息"""
        for pattern in self.stock_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def get_news_list(self, limit: int = 10) -> List[Dict]:
        """获取新闻列表"""
        try:
            print(f"正在请求韭研公社网站: {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return []
            
            # 处理Brotli压缩内容
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            
            if 'br' in content_encoding:
                # 手动处理Brotli压缩
                import brotli
                try:
                    decompressed_content = brotli.decompress(response.content)
                    html_content = decompressed_content.decode('utf-8', errors='ignore')
                    print("成功解压缩Brotli内容")
                except Exception as e:
                    print(f"Brotli解压缩失败: {e}")
                    # 回退到普通处理
                    response.encoding = 'utf-8'
                    html_content = response.text
            else:
                # 普通处理
                response.encoding = 'utf-8'
                html_content = response.text
            
            print("请求成功，开始解析页面...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 分析页面结构，提取新闻信息
            news_items = self._parse_news_items(soup)
            print(f"静态解析找到 {len(news_items)} 条新闻")
            
            # 如果静态解析不够，尝试动态数据获取
            if len(news_items) < limit:
                dynamic_items = self._parse_dynamic_data(soup)
                print(f"动态解析找到 {len(dynamic_items)} 条新闻")
                news_items.extend(dynamic_items)
            
            # 去重
            seen_titles = set()
            unique_news = []
            for item in news_items:
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    unique_news.append(item)
            
            print(f"去重后剩余 {len(unique_news)} 条新闻")
            return unique_news[:limit]
            
        except Exception as e:
            print(f"获取新闻列表失败: {e}")
            return []
    
    def _is_pinned_news(self, title: str, content: str) -> bool:
        """判断是否为置顶新闻"""
        # 置顶新闻的关键词
        pinned_keywords = [
            '置顶', '长韭杯', '牛股逻辑大赛', '官方合集', '公社招聘',
            '文章排序', '清朗行动', '工分指南', '异动关注', '社群搜公告',
            '产业库', '时间轴', '公社AI', '通知', '私信', '登录注册',
            '我的主页', '退出', '新帖播报', '个股研究', '题材行业',
            '纪要转载', '资讯荟萃'
        ]
        
        # 检查标题是否包含置顶关键词
        for keyword in pinned_keywords:
            if keyword in title:
                return True
        
        # 检查内容是否包含置顶关键词
        for keyword in pinned_keywords:
            if keyword in content:
                return True
        
        return False
    
    def _parse_news_items(self, soup: BeautifulSoup) -> List[Dict]:
        """解析新闻条目"""
        news_items = []
        
        # 方法1：查找包含时间戳的新闻条目
        # 韭研公社的新闻通常有时间戳和标题
        
        # 查找可能的新闻容器
        containers = soup.find_all(['div', 'article', 'li'], class_=True)
        
        for container in containers:
            # 检查容器是否包含时间信息
            container_text = container.get_text()
            
            # 查找时间戳（格式如：2025-09-30 16:25:27）
            time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            time_matches = re.findall(time_pattern, container_text)
            
            if time_matches:
                # 查找标题
                title_elements = container.find_all(['a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div'])
                
                for elem in title_elements:
                    title = elem.get_text(strip=True)
                    if len(title) > 10 and len(title) < 200:  # 合理的标题长度
                        # 检查是否为置顶新闻
                        if self._is_pinned_news(title, container_text):
                            continue  # 跳过置顶新闻
                        
                        # 获取链接
                        href = None
                        if elem.name == 'a' and elem.get('href'):
                            href = elem['href']
                            if not href.startswith('http'):
                                href = self.base_url + href
                        
                        # 获取作者信息
                        author = self._extract_author(container_text)
                        
                        # 提取股票链接信息
                        stock_links = self._extract_stock_links(container)
                        
                        # 检查是否包含股票信息（包括链接股票）
                        has_stock_info = self.contains_stock_info(title) or self.contains_stock_info(container_text) or len(stock_links) > 0
                        
                        if has_stock_info:
                            # 提取文本中的股票信息
                            text_stock_info = self.extract_stock_info(title + ' ' + container_text)
                            
                            # 将链接股票信息转换为标准格式
                            linked_stock_info = []
                            for stock_link in stock_links:
                                linked_stock_info.append({
                                    'type': 'linked_stock',
                                    'value': stock_link['name'],
                                    'description': f'关联股票: {stock_link["name"]}',
                                    'url': stock_link['url'],
                                    'code': stock_link['code']
                                })
                            
                            # 合并所有股票信息
                            all_stock_info = text_stock_info + linked_stock_info
                            
                            news_item = {
                                'title': title,
                                'url': href,
                                'publish_time': time_matches[0],
                                'author': author,
                                'source': '韭研公社',
                                'content_preview': self._extract_content_preview(container_text),
                                'stock_info': all_stock_info,
                                'stock_links': stock_links,  # 保留原始链接信息
                                'has_stock': len(all_stock_info) > 0
                            }
                            
                            news_items.append(news_item)
                            break  # 每个容器只取一个标题
        
        # 方法2：查找特定的新闻列表结构
        # 尝试查找常见的新闻列表选择器
        common_selectors = [
            '.news-item', '.article-item', '.post-item',
            '.list-item', '.item', '[class*="news"]', '[class*="article"]'
        ]
        
        for selector in common_selectors:
            items = soup.select(selector)
            for item in items:
                news_data = self._parse_news_item(item)
                if news_data:
                    news_items.append(news_data)
        
        return news_items
    
    def _parse_dynamic_data(self, soup: BeautifulSoup) -> List[Dict]:
        """解析动态加载的数据"""
        news_items = []
        
        # 查找script标签中的JSON数据
        scripts = soup.find_all('script')
        
        for script in scripts:
            if not script.string:
                continue
            
            script_content = script.string
            
            # 尝试查找JSON数据
            json_patterns = [
                r'\{[^{}]*"title"[^{}]*\}',  # 简单的JSON对象
                r'\[[^\]]*\{[^{}]*"title"[^{}]*\}[^\]]*\]',  # JSON数组
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, script_content)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, dict) and 'title' in data:
                            news_item = self._parse_json_news(data)
                            if news_item:
                                news_items.append(news_item)
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and 'title' in item:
                                    news_item = self._parse_json_news(item)
                                    if news_item:
                                        news_items.append(news_item)
                    except json.JSONDecodeError:
                        continue
        
        return news_items
    
    def _parse_json_news(self, data: Dict) -> Optional[Dict]:
        """解析JSON格式的新闻数据"""
        try:
            title = data.get('title', '').strip()
            if not title or len(title) < 5:
                return None
            
            # 检查是否包含股票信息
            content_text = data.get('content') or data.get('summary') or data.get('description', '')
            
            # 检查是否为置顶新闻
            if self._is_pinned_news(title, content_text):
                return None  # 跳过置顶新闻
            
            # 提取股票链接信息（从内容中提取）
            stock_links = self._extract_stock_links_from_text(content_text)
            
            # 检查是否包含股票信息（包括链接股票）
            has_stock_info = self.contains_stock_info(title) or self.contains_stock_info(content_text) or len(stock_links) > 0
            
            if has_stock_info:
                # 提取文本中的股票信息
                text_stock_info = self.extract_stock_info(title + ' ' + content_text)
                
                # 将链接股票信息转换为标准格式
                linked_stock_info = []
                for stock_link in stock_links:
                    linked_stock_info.append({
                        'type': 'linked_stock',
                        'value': stock_link['name'],
                        'description': f'关联股票: {stock_link["name"]}',
                        'url': stock_link['url'],
                        'code': stock_link['code']
                    })
                
                # 合并所有股票信息
                all_stock_info = text_stock_info + linked_stock_info
                
                return {
                    'title': title,
                    'url': data.get('url'),
                    'publish_time': data.get('publish_time') or data.get('time') or data.get('date'),
                    'author': data.get('author') or data.get('username'),
                    'source': '韭研公社',
                    'content_preview': content_text[:200],
                    'stock_info': all_stock_info,
                    'stock_links': stock_links,  # 保留原始链接信息
                    'has_stock': len(all_stock_info) > 0
                }
            
            return None
        except Exception:
            return None
    
    def _extract_stock_links(self, item) -> List[Dict]:
        """从新闻条目中提取股票链接信息"""
        stock_links = []
        
        # 查找股票链接容器
        stock_containers = item.find_all('div', class_='source-box')
        
        for container in stock_containers:
            # 查找股票链接
            stock_link = container.find('a', class_='text')
            if stock_link and stock_link.get('href') and stock_link.get_text(strip=True):
                stock_name = stock_link.get_text(strip=True)
                stock_url = stock_link['href']
                if not stock_url.startswith('http'):
                    stock_url = self.base_url + stock_url
                
                # 查找股票代码（如果有的话）
                stock_code = None
                code_elem = container.find('div', class_='round')
                if code_elem:
                    code_text = code_elem.get_text(strip=True)
                    # 检查是否是股票代码格式
                    if re.match(r'^[A-Z]$', code_text):
                        stock_code = code_text
                
                stock_links.append({
                    'name': stock_name,
                    'url': stock_url,
                    'code': stock_code,
                    'type': 'linked_stock'
                })
        
        return stock_links
    
    def _extract_stock_links_from_text(self, text):
        """从文本中提取股票链接信息"""
        stock_links = []
        
        # 使用BeautifulSoup解析HTML文本
        soup = BeautifulSoup(text, 'html.parser')
        
        # 查找包含股票链接的容器
        source_boxes = soup.find_all('div', class_='source-box')
        
        for box in source_boxes:
            # 查找股票名称链接
            stock_link = box.find('a', class_='text')
            if stock_link and stock_link.text.strip():
                stock_name = stock_link.text.strip()
                stock_url = stock_link.get('href', '')
                
                # 从URL中提取股票代码（如果有）
                stock_code = None
                if 'k=' in stock_url:
                    # 从URL参数中提取股票代码
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(stock_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    if 'k' in query_params:
                        stock_code = query_params['k'][0]
                
                stock_links.append({
                    'name': stock_name,
                    'url': stock_url,
                    'code': stock_code
                })
        
        return stock_links
    
    def _parse_news_item(self, item) -> Optional[Dict]:
        """解析单个新闻条目"""
        try:
            # 查找标题
            title_elem = item.find(['a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if len(title) < 5:
                return None
            
            # 获取容器文本
            item_text = item.get_text()
            
            # 检查是否为置顶新闻
            if self._is_pinned_news(title, item_text):
                return None  # 跳过置顶新闻
            
            # 获取链接
            href = None
            if title_elem.name == 'a' and title_elem.get('href'):
                href = title_elem['href']
                if not href.startswith('http'):
                    href = self.base_url + href
            
            # 查找时间
            time_text = ''
            time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            time_matches = re.findall(time_pattern, item_text)
            if time_matches:
                time_text = time_matches[0]
            
            # 查找作者
            author = self._extract_author(item_text)
            
            # 提取内容预览
            content_preview = self._extract_content_preview(item_text)
            
            # 提取股票链接信息
            stock_links = self._extract_stock_links(item)
            
            # 检查是否包含股票信息（包括链接股票）
            has_stock_info = self.contains_stock_info(title) or self.contains_stock_info(item_text) or len(stock_links) > 0
            
            if has_stock_info:
                # 提取文本中的股票信息
                text_stock_info = self.extract_stock_info(title + ' ' + item_text)
                
                # 将链接股票信息转换为标准格式
                linked_stock_info = []
                for stock_link in stock_links:
                    linked_stock_info.append({
                        'type': 'linked_stock',
                        'value': stock_link['name'],
                        'description': f'关联股票: {stock_link["name"]}',
                        'url': stock_link['url'],
                        'code': stock_link['code']
                    })
                
                # 合并所有股票信息
                all_stock_info = text_stock_info + linked_stock_info
                
                return {
                    'title': title,
                    'url': href,
                    'publish_time': time_text,
                    'author': author,
                    'source': '韭研公社',
                    'content_preview': content_preview,
                    'stock_info': all_stock_info,
                    'stock_links': stock_links,  # 保留原始链接信息
                    'has_stock': len(all_stock_info) > 0
                }
            
            return None
            
        except Exception:
            return None
    
    def _extract_author(self, text: str) -> str:
        """从文本中提取作者信息"""
        # 韭研公社的作者通常在用户名后面
        author_patterns = [
            r'作者[:：]\s*([^\s]+)',
            r'发布者[:：]\s*([^\s]+)',
            r'编辑[:：]\s*([^\s]+)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return '未知作者'
    
    def _extract_content_preview(self, text: str, max_length: int = 200) -> str:
        """提取内容预览"""
        # 清理文本，移除多余空格和换行
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        # 移除时间戳等无关信息
        cleaned_text = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', cleaned_text)
        
        # 截取前max_length个字符
        if len(cleaned_text) > max_length:
            return cleaned_text[:max_length] + '...'
        
        return cleaned_text
    
    def save_to_json(self, news_items: List[Dict], filename: str = 'jiuyangongshe_news.json'):
        """保存新闻数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            print(f"新闻数据已保存到: {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def print_news(self, news_items: List[Dict]):
        """打印新闻列表"""
        print(f"\n=== 韭研公社股票相关新闻列表（共{len(news_items)}条） ===")
        
        for i, news in enumerate(news_items, 1):
            print(f"\n{i}. {news['title']}")
            print(f"   时间: {news.get('publish_time', '未知时间')}")
            print(f"   作者: {news.get('author', '未知作者')}")
            
            # 显示股票信息
            stock_info = news.get('stock_info', [])
            if stock_info:
                print(f"   股票信息: ")
                for stock in stock_info:
                    print(f"     - {stock['description']}")
            
            # 显示股票链接信息
            if news.get('stock_links'):
                print("   股票链接:")
                for stock_link in news['stock_links']:
                    print(f"     - {stock_link['name']}")
                    if stock_link.get('code'):
                        print(f"       代码: {stock_link['code']}")
                    print(f"       链接: {stock_link['url']}")
            
            if news.get('url'):
                print(f"   链接: {news['url']}")
            if news.get('content_preview'):
                print(f"   预览: {news['content_preview']}")
            print("   " + "-" * 50)

def main():
    """主函数"""
    crawler = JiuYanGongSheCrawler()
    
    print("开始爬取韭研公社股票相关新闻...")
    print("注意：只爬取包含股票名称或代码的新闻")
    
    # 获取新闻列表
    news_items = crawler.get_news_list(limit=20)
    
    if news_items:
        # 打印新闻
        crawler.print_news(news_items)
        
        # 保存到文件
        crawler.save_to_json(news_items)
        
        # 统计股票信息
        total_stocks = sum(len(news.get('stock_info', [])) for news in news_items)
        print(f"\n爬取完成！共获取 {len(news_items)} 条股票相关新闻。")
        print(f"共识别出 {total_stocks} 个股票相关信息。")
    else:
        print("未能获取到包含股票信息的新闻数据。")

if __name__ == "__main__":
    main()