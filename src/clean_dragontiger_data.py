import pandas as pd
import csv
from datetime import datetime

def clean_dragontiger_data():
    """清理龙虎榜数据，去除重复并保留每日前20只股票"""
    
    # 读取原始CSV文件
    input_file = "src/龙虎榜数据.csv"
    output_file = "src/龙虎榜数据_清理后.csv"
    
    try:
        # 读取CSV文件
        df = pd.read_csv(input_file)
        
        print(f"原始数据记录数: {len(df)}")
        print(f"原始数据日期范围: {df['date'].unique()}")
        
        # 检查重复记录
        duplicates = df.duplicated(subset=['date', 'stock_code'], keep=False)
        if duplicates.any():
            print(f"发现重复记录: {duplicates.sum()} 条")
            
            # 显示重复记录
            duplicate_records = df[duplicates]
            print("重复记录详情:")
            for _, row in duplicate_records.iterrows():
                print(f"股票代码: {row['stock_code']}, 股票名称: {row['stock_name']}, 日期: {row['date']}, 排名: {row['rank']}")
        
        # 按日期分组，每个日期保留排名前20的股票
        cleaned_data = []
        
        for date in df['date'].unique():
            date_data = df[df['date'] == date]
            
            # 按排名排序
            date_data_sorted = date_data.sort_values('rank')
            
            # 去除重复股票（保留排名靠前的记录）
            date_data_deduplicated = date_data_sorted.drop_duplicates(subset=['stock_code'], keep='first')
            
            # 保留前20只股票
            top_20 = date_data_deduplicated.head(20)
            
            # 重新排名
            top_20 = top_20.reset_index(drop=True)
            top_20['rank'] = top_20.index + 1
            
            cleaned_data.append(top_20)
            
            print(f"日期 {date}: 原始记录 {len(date_data)} 条, 去重后 {len(date_data_deduplicated)} 条, 保留前20条")
        
        # 合并所有日期的数据
        if cleaned_data:
            final_df = pd.concat(cleaned_data, ignore_index=True)
            
            print(f"\n清理后总记录数: {len(final_df)}")
            print(f"清理后数据日期范围: {final_df['date'].unique()}")
            
            # 保存清理后的数据
            final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"清理后的数据已保存到: {output_file}")
            
            # 显示清理后的数据统计
            print("\n清理后的数据统计:")
            for date in final_df['date'].unique():
                date_count = len(final_df[final_df['date'] == date])
                print(f"日期 {date}: {date_count} 条记录")
            
            return True
        else:
            print("没有数据需要清理")
            return False
            
    except FileNotFoundError:
        print(f"文件 {input_file} 不存在")
        return False
    except Exception as e:
        print(f"清理数据时出错: {e}")
        return False

if __name__ == "__main__":
    clean_dragontiger_data()