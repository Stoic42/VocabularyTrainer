#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复错误历史中的单词显示问题：
更新ErrorLogs表中关联的Words数据，确保错误历史显示正确的单词信息
"""

import sqlite3
import re

DATABASE_FILE = 'vocabulary.db'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def fix_error_history_display():
    """修复错误历史中的单词显示问题"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("开始修复错误历史中的单词显示问题...")
    
    # 1. 查找所有有问题的错误记录
    print("1. 查找有问题的错误记录...")
    cursor.execute("""
        SELECT DISTINCT e.error_id, w.word_id, w.spelling, w.pos, w.meaning_cn
        FROM ErrorLogs e 
        JOIN Words w ON e.word_id = w.word_id 
        WHERE w.pos LIKE '%<br>%' 
           OR w.meaning_cn LIKE '%感觉，%'
           OR w.meaning_cn LIKE '%disagreement%'
           OR w.meaning_cn LIKE '%伤害，%'
           OR w.pos LIKE '%&amp;%'
    """)
    
    problematic_records = cursor.fetchall()
    print(f"   找到 {len(problematic_records)} 个有问题的错误记录")
    
    # 2. 修复这些记录对应的Words表数据
    print("2. 修复Words表中的问题数据...")
    
    # 修复harm单词
    cursor.execute("""
        UPDATE Words 
        SET pos = 'n./vt.',
            meaning_cn = '伤害，损伤'
        WHERE spelling = 'harm'
    """)
    harm_fixed = cursor.rowcount
    print(f"   修复了 {harm_fixed} 个harm单词")
    
    # 修复sense单词
    cursor.execute("""
        UPDATE Words 
        SET pos = 'n.',
            meaning_cn = '感觉，知觉；意义，道理'
        WHERE spelling = 'sense'
    """)
    sense_fixed = cursor.rowcount
    print(f"   修复了 {sense_fixed} 个sense单词")
    
    # 修复其他常见问题
    cursor.execute("""
        UPDATE Words 
        SET pos = REPLACE(pos, '&amp;', '&')
        WHERE pos LIKE '%&amp;%'
    """)
    amp_fixed = cursor.rowcount
    print(f"   修复了 {amp_fixed} 个HTML实体问题")
    
    # 修复词性中的换行问题
    cursor.execute("""
        UPDATE Words 
        SET pos = REPLACE(pos, '<br>', '/')
        WHERE pos LIKE '%<br>%'
    """)
    br_fixed = cursor.rowcount
    print(f"   修复了 {br_fixed} 个词性换行问题")
    
    # 3. 验证修复结果
    print("\n3. 验证修复结果:")
    test_words = ['harm', 'sense', 'disagree', 'feel', 'hurt']
    for word in test_words:
        cursor.execute("""
            SELECT w.spelling, w.pos, w.meaning_cn, COUNT(e.error_id) as error_count
            FROM Words w 
            LEFT JOIN ErrorLogs e ON w.word_id = e.word_id 
            WHERE w.spelling = ?
            GROUP BY w.word_id
        """, (word,))
        results = cursor.fetchall()
        for result in results:
            print(f"   {word}: pos='{result['pos']}', meaning='{result['meaning_cn']}', errors={result['error_count']}")
    
    # 提交更改
    conn.commit()
    conn.close()
    print("\n错误历史显示问题修复完成！")
    print("请刷新错误历史页面查看修复效果。")

if __name__ == "__main__":
    fix_error_history_display() 