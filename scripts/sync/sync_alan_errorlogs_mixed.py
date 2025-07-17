#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合策略：处理已经部分同步的情况
基于(student_id, word_id, error_type, student_answer, error_date)判断是否已存在
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os
from datetime import datetime

def sync_alan_errorlogs_mixed():
    """混合策略同步Alan的错词记录"""
    
    # 数据库文件路径
    source_db = "Alan/vocabulary_classroom.db"
    target_db = get_database_path()
    
    # 检查源数据库是否存在
    if not os.path.exists(source_db):
        print(f"错误：源数据库文件 {source_db} 不存在")
        return
    
    if not os.path.exists(target_db):
        print(f"错误：目标数据库文件 {target_db} 不存在")
        return
    
    try:
        # 连接数据库
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        # 获取Alan的用户ID
        source_cursor.execute("SELECT id FROM Users WHERE username = 'Alan'")
        alan_id = source_cursor.fetchone()
        
        if not alan_id:
            print("错误：在源数据库中找不到Alan用户")
            return
        
        alan_id = alan_id[0]
        print(f"Alan的用户ID: {alan_id}")
        
        # 获取目标数据库中已存在的记录的唯一标识
        target_cursor.execute("""
            SELECT student_id, word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ?
        """, (alan_id,))
        
        existing_records = set(target_cursor.fetchall())
        print(f"目标数据库中已存在的记录数: {len(existing_records)}")
        
        # 获取源数据库中所有的错词记录
        source_cursor.execute("""
            SELECT error_id, student_id, word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ?
            ORDER BY error_date
        """, (alan_id,))
        
        all_source_records = source_cursor.fetchall()
        print(f"源数据库中的错词记录总数: {len(all_source_records)}")
        
        # 开始同步
        synced_count = 0
        skipped_count = 0
        
        for record in all_source_records:
            error_id, student_id, word_id, error_type, student_answer, error_date = record
            
            # 检查是否已存在相同的记录（基于除error_id外的所有字段）
            record_key = (student_id, word_id, error_type, student_answer, error_date)
            
            if record_key not in existing_records:
                # 插入新记录（不指定error_id，让数据库自动生成）
                target_cursor.execute("""
                    INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, word_id, error_type, student_answer, error_date))
                synced_count += 1
                if synced_count <= 10:  # 只显示前10条，避免输出过多
                    print(f"同步记录: {error_date} - {error_type} - '{student_answer}'")
                elif synced_count == 11:
                    print("... (更多记录正在同步)")
            else:
                skipped_count += 1
        
        # 提交更改
        target_conn.commit()
        
        print(f"\n同步完成:")
        print(f"- 成功同步: {synced_count} 条记录")
        print(f"- 跳过已存在: {skipped_count} 条记录")
        print(f"- 总计处理: {len(all_source_records)} 条记录")
        
        # 验证同步结果
        target_cursor.execute("SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?", (alan_id,))
        final_count = target_cursor.fetchone()[0]
        print(f"目标数据库中Alan的错词记录总数: {final_count}")
        
        # 分析结果
        if synced_count == 0:
            print("✅ 所有记录都已同步，无需额外操作")
        elif synced_count > 0:
            print(f"✅ 成功同步了 {synced_count} 条新记录")
        
        # 检查是否完全同步
        if final_count == len(all_source_records):
            print("✅ 同步成功！所有记录都已同步")
        else:
            print(f"⚠️  目标数据库记录数({final_count})与源数据库记录数({len(all_source_records)})不一致")
            print("注意：这可能是因为源数据库中有重复记录，目标数据库只保留了一份")
        
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
    print("开始混合策略同步Alan的错词记录...")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    sync_alan_errorlogs_mixed()
    
    print("-" * 50)
    print("同步完成！") 