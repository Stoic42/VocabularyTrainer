#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出Alan错题记录中所有error_date完全相同的重复记录
"""

import sqlite3
from collections import defaultdict

def show_exact_duplicates():
    db = "Alan/vocabulary_classroom.db"
    alan_id = 3
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    
    # 查询所有错题记录
    cur.execute("""
        SELECT word_id, error_type, student_answer, error_date, error_id
        FROM ErrorLogs WHERE student_id = ?
        ORDER BY word_id, error_date
    """, (alan_id,))
    rows = cur.fetchall()
    
    # 分组统计四字段全等的记录
    group = defaultdict(list)
    for word_id, error_type, student_answer, error_date, error_id in rows:
        key = (word_id, error_type, student_answer, error_date)
        group[key].append(error_id)
    
    # 输出所有有重复的组
    print("=== 完全重复（四字段全等）记录 ===")
    found = False
    for (word_id, error_type, student_answer, error_date), ids in group.items():
        if len(ids) > 1:
            found = True
            print(f"单词ID: {word_id}, 错误类型: {error_type}, 答案: '{student_answer}', 时间: {error_date}")
            print(f"  记录ID: {ids}")
    if not found:
        print("没有发现任何error_date完全相同的重复记录！")
    conn.close()

if __name__ == "__main__":
    show_exact_duplicates() 