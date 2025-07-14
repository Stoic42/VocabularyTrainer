#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Alan错词记录同步问题
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os

def debug_sync():
    """调试同步问题"""
    
    source_db = "Alan/vocabulary_classroom.db"
    target_db = get_database_path()
    
    try:
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        alan_id = 3
        
        # 直接查询记录数
        source_cursor.execute("SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?", (alan_id,))
        source_count = source_cursor.fetchone()[0]
        
        target_cursor.execute("SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?", (alan_id,))
        target_count = target_cursor.fetchone()[0]
        
        print(f"直接查询 - 源数据库记录数: {source_count}")
        print(f"直接查询 - 目标数据库记录数: {target_count}")
        
        # 获取源数据库中的所有记录（包括重复）
        source_cursor.execute("""
            SELECT word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ?
            ORDER BY error_date
        """, (alan_id,))
        
        source_records = source_cursor.fetchall()
        source_unique_records = set(source_records)
        
        # 获取目标数据库中的所有记录（包括重复）
        target_cursor.execute("""
            SELECT word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ?
            ORDER BY error_date
        """, (alan_id,))
        
        target_records = target_cursor.fetchall()
        target_unique_records = set(target_records)
        
        print(f"\n去重后 - 源数据库唯一记录数: {len(source_unique_records)}")
        print(f"去重后 - 目标数据库唯一记录数: {len(target_unique_records)}")
        print(f"源数据库重复记录数: {len(source_records) - len(source_unique_records)}")
        print(f"目标数据库重复记录数: {len(target_records) - len(target_unique_records)}")
        
        # 找出缺失的记录
        missing_records = source_unique_records - target_unique_records
        print(f"\n缺失的记录数: {len(missing_records)}")
        
        if missing_records:
            print("\n缺失的记录:")
            for record in sorted(missing_records, key=lambda x: x[3]):  # 按时间排序
                word_id, error_type, student_answer, error_date = record
                print(f"  {word_id}|{error_type}|{student_answer}|{error_date}")
        
        # 找出多余的记录
        extra_records = target_unique_records - source_unique_records
        print(f"\n多余的记录数: {len(extra_records)}")
        
        if extra_records:
            print("\n多余的记录:")
            for record in sorted(extra_records, key=lambda x: x[3]):  # 按时间排序
                word_id, error_type, student_answer, error_date = record
                print(f"  {word_id}|{error_type}|{student_answer}|{error_date}")
        
        # 检查重复记录
        print("\n检查重复记录:")
        source_duplicates = {}
        for record in source_records:
            if record in source_duplicates:
                source_duplicates[record] += 1
            else:
                source_duplicates[record] = 1
        
        target_duplicates = {}
        for record in target_records:
            if record in target_duplicates:
                target_duplicates[record] += 1
            else:
                target_duplicates[record] = 1
        
        source_dup_count = sum(1 for count in source_duplicates.values() if count > 1)
        target_dup_count = sum(1 for count in target_duplicates.values() if count > 1)
        
        print(f"源数据库有重复的记录数: {source_dup_count}")
        print(f"目标数据库有重复的记录数: {target_dup_count}")
        
        # 按日期统计差异
        print("\n按日期统计:")
        source_dates = {}
        target_dates = {}
        
        for record in source_records:
            date = record[3].split()[0]  # 取日期部分
            source_dates[date] = source_dates.get(date, 0) + 1
        
        for record in target_records:
            date = record[3].split()[0]  # 取日期部分
            target_dates[date] = target_dates.get(date, 0) + 1
        
        all_dates = sorted(set(source_dates.keys()) | set(target_dates.keys()))
        
        for date in all_dates:
            source_count = source_dates.get(date, 0)
            target_count = target_dates.get(date, 0)
            diff = source_count - target_count
            print(f"  {date}: 源={source_count}, 目标={target_count}, 差异={diff}")
        
    except Exception as e:
        print(f"调试过程中发生错误: {e}")
    finally:
        if 'source_conn' in locals():
            source_conn.close()
        if 'target_conn' in locals():
            target_conn.close()

if __name__ == "__main__":
    debug_sync() 