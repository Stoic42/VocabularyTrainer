#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析2025-07-08的70条"重复"记录
"""

import sqlite3
from collections import defaultdict

def analyze_duplicates_detailed():
    """详细分析重复记录"""
    
    source_db = "Alan/vocabulary_classroom.db"
    target_db = "vocabulary.db"
    
    try:
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        alan_id = 3
        target_date = "2025-07-08"
        
        print(f"=== 详细分析 {target_date} 的重复记录 ===")
        
        # 获取源数据库该日期的所有记录
        source_cursor.execute("""
            SELECT error_id, word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ? AND DATE(error_date) = ?
            ORDER BY error_date, error_id
        """, (alan_id, target_date))
        
        source_records = source_cursor.fetchall()
        print(f"源数据库 {target_date} 总记录数: {len(source_records)}")
        
        # 获取目标数据库该日期的所有记录
        target_cursor.execute("""
            SELECT word_id, error_type, student_answer, error_date
            FROM ErrorLogs 
            WHERE student_id = ? AND DATE(error_date) = ?
            ORDER BY error_date
        """, (alan_id, target_date))
        
        target_records = set(target_cursor.fetchall())
        print(f"目标数据库 {target_date} 总记录数: {len(target_records)}")
        
        # 按唯一键分组源数据库记录
        unique_groups = defaultdict(list)
        for error_id, word_id, error_type, student_answer, error_date in source_records:
            key = (word_id, error_type, student_answer, error_date)
            unique_groups[key].append(error_id)
        
        # 找出有重复的记录组
        duplicate_groups = {key: ids for key, ids in unique_groups.items() if len(ids) > 1}
        
        print(f"\n有重复的记录组数: {len(duplicate_groups)}")
        
        # 详细显示每个重复组
        print(f"\n=== 重复组详情 ===")
        total_duplicates = 0
        
        for i, (key, error_ids) in enumerate(duplicate_groups.items(), 1):
            word_id, error_type, student_answer, error_date = key
            duplicate_count = len(error_ids) - 1  # 减去1，只计算重复的部分
            
            print(f"\n重复组 {i}:")
            print(f"  单词ID: {word_id}")
            print(f"  错误类型: {error_type}")
            print(f"  学生答案: '{student_answer}'")
            print(f"  错误时间: {error_date}")
            print(f"  重复次数: {duplicate_count}")
            print(f"  错误记录ID: {error_ids}")
            
            # 检查这些记录在目标数据库中是否存在
            if key in target_records:
                print(f"  ✅ 在目标数据库中存在")
            else:
                print(f"  ❌ 在目标数据库中不存在")
            
            total_duplicates += duplicate_count
        
        print(f"\n=== 统计信息 ===")
        print(f"总重复记录数: {total_duplicates}")
        print(f"独立记录数: {len(unique_groups)}")
        print(f"源数据库总记录数: {len(source_records)}")
        print(f"目标数据库总记录数: {len(target_records)}")
        
        # 检查是否有遗漏的记录
        print(f"\n=== 检查遗漏记录 ===")
        missing_records = []
        
        for error_id, word_id, error_type, student_answer, error_date in source_records:
            record_key = (word_id, error_type, student_answer, error_date)
            if record_key not in target_records:
                missing_records.append((error_id, word_id, error_type, student_answer, error_date))
        
        if missing_records:
            print(f"发现 {len(missing_records)} 条遗漏记录:")
            for error_id, word_id, error_type, student_answer, error_date in missing_records[:10]:
                print(f"  遗漏: {error_date} - {error_type} - '{student_answer}' (ID: {error_id})")
            if len(missing_records) > 10:
                print(f"  ... 还有 {len(missing_records) - 10} 条遗漏记录")
        else:
            print("没有发现遗漏记录")
        
        # 验证计算
        print(f"\n=== 验证计算 ===")
        expected_target = len(source_records) - total_duplicates
        print(f"源数据库记录数: {len(source_records)}")
        print(f"重复记录数: {total_duplicates}")
        print(f"期望目标数据库记录数: {len(source_records)} - {total_duplicates} = {expected_target}")
        print(f"实际目标数据库记录数: {len(target_records)}")
        
        if expected_target == len(target_records):
            print("✅ 计算验证通过，重复记录已正确去重")
        else:
            print(f"❌ 计算验证失败，期望 {expected_target}，实际 {len(target_records)}")
        
    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'source_conn' in locals():
            source_conn.close()
        if 'target_conn' in locals():
            target_conn.close()

if __name__ == "__main__":
    analyze_duplicates_detailed() 