#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于时间记录详细排查增量同步情况
"""

from utils import get_database_connection, get_database_path
import sqlite3
from collections import defaultdict

def check_time_based_sync():
    """基于时间记录详细排查"""
    
    source_db = "Alan/vocabulary_classroom.db"
    target_db = get_database_path()
    
    try:
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        alan_id = 3
        
        print("=== 基于时间记录的详细排查 ===")
        
        # 获取源数据库按时间分组的记录
        source_cursor.execute("""
            SELECT DATE(error_date) as date, COUNT(*) as count
            FROM ErrorLogs 
            WHERE student_id = ?
            GROUP BY DATE(error_date)
            ORDER BY date
        """, (alan_id,))
        
        source_dates = dict(source_cursor.fetchall())
        
        # 获取目标数据库按时间分组的记录
        target_cursor.execute("""
            SELECT DATE(error_date) as date, COUNT(*) as count
            FROM ErrorLogs 
            WHERE student_id = ?
            GROUP BY DATE(error_date)
            ORDER BY date
        """, (alan_id,))
        
        target_dates = dict(target_cursor.fetchall())
        
        print("按日期统计对比:")
        print("日期\t\t源数据库\t目标数据库\t差异")
        print("-" * 50)
        
        all_dates = sorted(set(source_dates.keys()) | set(target_dates.keys()))
        total_source = 0
        total_target = 0
        
        for date in all_dates:
            source_count = source_dates.get(date, 0)
            target_count = target_dates.get(date, 0)
            diff = source_count - target_count
            total_source += source_count
            total_target += target_count
            
            status = "✅" if diff == 0 else f"⚠️ 缺少{diff}条"
            print(f"{date}\t{source_count}\t\t{target_count}\t\t{status}")
        
        print("-" * 50)
        print(f"总计\t\t{total_source}\t\t{total_target}\t\t{total_source - total_target}")
        
        # 检查具体缺失的记录
        print(f"\n=== 详细检查缺失记录 ===")
        
        for date in all_dates:
            source_count = source_dates.get(date, 0)
            target_count = target_dates.get(date, 0)
            
            if source_count > target_count:
                print(f"\n日期 {date} 缺少 {source_count - target_count} 条记录:")
                
                # 获取源数据库该日期的所有记录
                source_cursor.execute("""
                    SELECT error_id, word_id, error_type, student_answer, error_date
                    FROM ErrorLogs 
                    WHERE student_id = ? AND DATE(error_date) = ?
                    ORDER BY error_date
                """, (alan_id, date))
                
                source_records = source_cursor.fetchall()
                
                # 获取目标数据库该日期的所有记录
                target_cursor.execute("""
                    SELECT word_id, error_type, student_answer, error_date
                    FROM ErrorLogs 
                    WHERE student_id = ? AND DATE(error_date) = ?
                    ORDER BY error_date
                """, (alan_id, date))
                
                target_records = set(target_cursor.fetchall())
                
                # 找出缺失的记录
                missing_count = 0
                for error_id, word_id, error_type, student_answer, error_date in source_records:
                    record_key = (word_id, error_type, student_answer, error_date)
                    if record_key not in target_records:
                        missing_count += 1
                        if missing_count <= 5:  # 只显示前5条
                            print(f"  缺失: {error_date} - {error_type} - '{student_answer}' (ID: {error_id})")
                        elif missing_count == 6:
                            print(f"  ... 还有 {len(source_records) - len(target_records) - 5} 条缺失记录")
                            break
                
                print(f"  该日期实际缺失: {missing_count} 条记录")
        
        # 检查是否有重复记录导致的问题
        print(f"\n=== 检查重复记录情况 ===")
        
        source_cursor.execute("""
            SELECT word_id, error_type, student_answer, error_date, COUNT(*) as count
            FROM ErrorLogs 
            WHERE student_id = ?
            GROUP BY word_id, error_type, student_answer, error_date
            HAVING COUNT(*) > 1
            ORDER BY error_date
        """, (alan_id,))
        
        duplicate_groups = source_cursor.fetchall()
        
        if duplicate_groups:
            print(f"发现 {len(duplicate_groups)} 组重复记录:")
            for word_id, error_type, student_answer, error_date, count in duplicate_groups[:10]:
                print(f"  {error_date} - {error_type} - '{student_answer}' (重复{count}次)")
            if len(duplicate_groups) > 10:
                print(f"  ... 还有 {len(duplicate_groups) - 10} 组重复记录")
        else:
            print("没有发现重复记录")
        
        # 总结
        print(f"\n=== 总结 ===")
        if total_source == total_target:
            print("✅ 完全同步成功！所有记录都已同步")
        else:
            print(f"⚠️  还有 {total_source - total_target} 条记录未同步")
            print("这些可能是重复记录，在目标数据库中只保留了一份")
        
    except Exception as e:
        print(f"检查过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'source_conn' in locals():
            source_conn.close()
        if 'target_conn' in locals():
            target_conn.close()

if __name__ == "__main__":
    check_time_based_sync() 