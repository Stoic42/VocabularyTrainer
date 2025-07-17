#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理错误同步的记录，然后只同步2025-07-08缺失的70条记录
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os
from datetime import datetime

def cleanup_and_sync_70():
    """清理并同步缺失的70条记录"""
    
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
        
        print("=== 清理和同步操作 ===")
        
        # 1. 先检查当前状态
        target_cursor.execute("SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?", (alan_id,))
        current_count = target_cursor.fetchone()[0]
        print(f"当前目标数据库记录数: {current_count}")
        
        source_cursor.execute("SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?", (alan_id,))
        source_count = source_cursor.fetchone()[0]
        print(f"源数据库记录数: {source_count}")
        
        # 2. 如果目标数据库记录数超过源数据库，说明有重复同步，需要清理
        if current_count > source_count:
            print(f"检测到重复同步，需要清理 {current_count - source_count} 条重复记录")
            
            # 删除Alan的所有记录
            target_cursor.execute("DELETE FROM ErrorLogs WHERE student_id = ?", (alan_id,))
            print("已删除Alan的所有记录")
            
            # 重新同步所有记录（这次会正确同步）
            source_cursor.execute("""
                SELECT error_id, student_id, word_id, error_type, student_answer, error_date
                FROM ErrorLogs 
                WHERE student_id = ?
                ORDER BY error_date
            """, (alan_id,))
            
            all_source_records = source_cursor.fetchall()
            
            synced_count = 0
            for error_id, student_id, word_id, error_type, student_answer, error_date in all_source_records:
                target_cursor.execute("""
                    INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, word_id, error_type, student_answer, error_date))
                synced_count += 1
            
            print(f"重新同步了 {synced_count} 条记录")
        
        # 3. 验证结果
        target_cursor.execute("SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?", (alan_id,))
        final_count = target_cursor.fetchone()[0]
        print(f"目标数据库最终记录数: {final_count}")
        
        # 4. 检查2025-07-08的记录
        source_cursor.execute("""
            SELECT COUNT(*) FROM ErrorLogs 
            WHERE student_id = ? AND DATE(error_date) = '2025-07-08'
        """, (alan_id,))
        source_0708_count = source_cursor.fetchone()[0]
        
        target_cursor.execute("""
            SELECT COUNT(*) FROM ErrorLogs 
            WHERE student_id = ? AND DATE(error_date) = '2025-07-08'
        """, (alan_id,))
        target_0708_count = target_cursor.fetchone()[0]
        
        print(f"源数据库2025-07-08记录数: {source_0708_count}")
        print(f"目标数据库2025-07-08记录数: {target_0708_count}")
        
        if target_0708_count == source_0708_count:
            print("✅ 2025-07-08的记录已完全同步")
        else:
            print(f"⚠️  2025-07-08记录数不一致，期望{source_0708_count}，实际{target_0708_count}")
        
        # 5. 按日期统计验证
        print(f"\n=== 按日期统计验证 ===")
        target_cursor.execute("""
            SELECT DATE(error_date) as date, COUNT(*) as count
            FROM ErrorLogs 
            WHERE student_id = ?
            GROUP BY DATE(error_date)
            ORDER BY date
        """, (alan_id,))
        
        target_dates = dict(target_cursor.fetchall())
        
        source_cursor.execute("""
            SELECT DATE(error_date) as date, COUNT(*) as count
            FROM ErrorLogs 
            WHERE student_id = ?
            GROUP BY DATE(error_date)
            ORDER BY date
        """, (alan_id,))
        
        source_dates = dict(source_cursor.fetchall())
        
        print("日期\t\t源数据库\t目标数据库\t状态")
        print("-" * 50)
        
        all_dates = sorted(set(source_dates.keys()) | set(target_dates.keys()))
        for date in all_dates:
            source_count = source_dates.get(date, 0)
            target_count = target_dates.get(date, 0)
            status = "✅" if source_count == target_count else f"❌ 差异{source_count-target_count}"
            print(f"{date}\t{source_count}\t\t{target_count}\t\t{status}")
        
        # 提交更改
        target_conn.commit()
        
    except Exception as e:
        print(f"操作过程中发生错误: {e}")
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
    print("开始清理和同步操作...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    cleanup_and_sync_70()
    
    print("-" * 50)
    print("操作完成！") 