#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门同步那70条被判定为"重复"的记录
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os
from datetime import datetime

def sync_missing_70():
    """同步缺失的70条记录"""
    
    # 数据库文件路径
    source_db = "Alan/vocabulary_classroom.db"
    target_db = get_database_path()
    
    try:
        # 连接数据库
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        alan_id = 3
        
        print("=== 同步缺失的70条记录 ===")
        
        # 获取源数据库2025-07-08的所有记录
        source_cursor.execute("""
            SELECT error_id, student_id, word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ? AND DATE(error_date) = '2025-07-08'
            ORDER BY error_date, error_id
        """, (alan_id,))
        
        source_records = source_cursor.fetchall()
        print(f"源数据库2025-07-08记录数: {len(source_records)}")
        
        # 获取目标数据库2025-07-08的所有记录
        target_cursor.execute("""
            SELECT student_id, word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ? AND DATE(error_date) = '2025-07-08'
        """, (alan_id,))
        
        target_records = set(target_cursor.fetchall())
        print(f"目标数据库2025-07-08记录数: {len(target_records)}")
        
        # 找出缺失的记录
        missing_records = []
        for error_id, student_id, word_id, error_type, student_answer, error_date in source_records:
            record_key = (student_id, word_id, error_type, student_answer, error_date)
            if record_key not in target_records:
                missing_records.append((error_id, student_id, word_id, error_type, student_answer, error_date))
        
        print(f"需要同步的记录数: {len(missing_records)}")
        
        if not missing_records:
            print("没有需要同步的记录")
            return
        
        # 开始同步
        synced_count = 0
        
        for error_id, student_id, word_id, error_type, student_answer, error_date in missing_records:
            # 插入新记录
            target_cursor.execute("""
                INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, word_id, error_type, student_answer, error_date))
            
            synced_count += 1
            if synced_count <= 10:
                print(f"同步记录: {error_date} - {error_type} - '{student_answer}' (原ID: {error_id})")
            elif synced_count == 11:
                print("... (更多记录正在同步)")
        
        # 提交更改
        target_conn.commit()
        
        print(f"\n同步完成:")
        print(f"- 成功同步: {synced_count} 条记录")
        
        # 验证结果
        target_cursor.execute("SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?", (alan_id,))
        final_count = target_cursor.fetchone()[0]
        print(f"目标数据库中Alan的错词记录总数: {final_count}")
        
        # 检查2025-07-08的记录数
        target_cursor.execute("""
            SELECT COUNT(*) FROM ErrorLogs 
            WHERE student_id = ? AND DATE(error_date) = '2025-07-08'
        """, (alan_id,))
        
        target_0708_count = target_cursor.fetchone()[0]
        print(f"目标数据库2025-07-08记录数: {target_0708_count}")
        
        if target_0708_count == len(source_records):
            print("✅ 2025-07-08的记录已完全同步")
        else:
            print(f"⚠️  2025-07-08记录数不一致，期望{len(source_records)}，实际{target_0708_count}")
        
    except Exception as e:
        print(f"同步过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        if 'target_conn' in locals():
            target_conn.rollback()
    finally:
        if 'source_conn' in locals():
            source_conn.close()
        if 'target_conn' in locals():
            target_conn.close()

if __name__ == "__main__":
    print("开始同步缺失的70条记录...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    sync_missing_70()
    
    print("-" * 50)
    print("同步完成！") 