#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复单词显示问题：
1. 修复词性换行问题（去掉<br>标签）
2. 修复词义截取问题
3. 修复格式混乱问题
4. 处理重复记录
"""

from utils import get_database_connection, get_database_path
import sqlite3
import re

DATABASE_FILE = get_database_path()

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def fix_word_display_issues():
    """修复单词显示问题"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("开始修复单词显示问题...")
    
    # 1. 修复词性换行问题 - 去掉<br>标签
    print("1. 修复词性换行问题...")
    cursor.execute("""
        UPDATE Words 
        SET pos = REPLACE(pos, '<br>', '/')
        WHERE pos LIKE '%<br>%'
    """)
    br_fixed = cursor.rowcount
    print(f"   修复了 {br_fixed} 个词性换行问题")
    
    # 2. 修复feel单词的词义问题 - 处理所有feel记录
    print("2. 修复feel单词的词义问题...")
    cursor.execute("""
        UPDATE Words 
        SET meaning_cn = '感觉；触摸；认为',
            pos = 'vt./vi./link.v.'
        WHERE spelling = 'feel'
    """)
    feel_fixed = cursor.rowcount
    print(f"   修复了 {feel_fixed} 个feel单词的词义问题")
    
    # 3. 修复disagree单词的词义问题
    print("3. 修复disagree单词的词义问题...")
    cursor.execute("""
        UPDATE Words 
        SET meaning_cn = '不同意，有分歧',
            pos = 'vi.'
        WHERE spelling = 'disagree'
    """)
    disagree_fixed = cursor.rowcount
    print(f"   修复了 {disagree_fixed} 个disagree单词的词义问题")
    
    # 4. 修复hurt单词的词义问题
    print("4. 修复hurt单词的词义问题...")
    cursor.execute("""
        UPDATE Words 
        SET meaning_cn = '伤害，损伤；疼痛',
            pos = 'v.'
        WHERE spelling = 'hurt'
    """)
    hurt_fixed = cursor.rowcount
    print(f"   修复了 {hurt_fixed} 个hurt单词的词义问题")
    
    # 5. 清理其他格式问题
    print("5. 清理其他格式问题...")
    cursor.execute("""
        UPDATE Words 
        SET meaning_cn = TRIM(meaning_cn),
            pos = TRIM(pos)
        WHERE meaning_cn LIKE '% %' OR pos LIKE '% %'
    """)
    trim_fixed = cursor.rowcount
    print(f"   清理了 {trim_fixed} 个格式问题")
    
    # 6. 修复词性中的多余空格
    cursor.execute("""
        UPDATE Words 
        SET pos = REPLACE(pos, ' / ', '/')
        WHERE pos LIKE '% / %'
    """)
    space_fixed = cursor.rowcount
    print(f"   修复了 {space_fixed} 个词性空格问题")
    
    # 7. 删除重复记录（保留第一个）
    print("7. 处理重复记录...")
    cursor.execute("""
        DELETE FROM Words 
        WHERE word_id NOT IN (
            SELECT MIN(word_id) 
            FROM Words 
            GROUP BY spelling, list_id
        )
    """)
    duplicate_fixed = cursor.rowcount
    print(f"   删除了 {duplicate_fixed} 个重复记录")
    
    # 提交更改
    conn.commit()
    
    # 验证修复结果
    print("\n验证修复结果:")
    test_words = ['feel', 'disagree', 'hurt']
    for word in test_words:
        cursor.execute("SELECT spelling, pos, meaning_cn FROM Words WHERE spelling = ?", (word,))
        results = cursor.fetchall()
        for result in results:
            print(f"   {word}: pos='{result['pos']}', meaning='{result['meaning_cn']}'")
    
    conn.close()
    print("\n单词显示问题修复完成！")

if __name__ == "__main__":
    fix_word_display_issues() 