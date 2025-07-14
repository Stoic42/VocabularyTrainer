#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复多个问题：
1. 修复即时反馈功能的默认状态
2. 修复 embarrass 单词的美音映射
3. 修复 shall 单词的中文释义
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os
import re

# 配置
DATABASE_FILE = get_database_path()
SENIOR_HIGH_TXT = 'wordlists/senior_high/Senior_high.txt'
MEDIA_DIR = 'wordlists/senior_high/media'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def fix_instant_feedback_default():
    """修复即时反馈功能的默认状态"""
    print("=== 修复即时反馈功能默认状态 ===")
    
    # 读取当前的 index.html
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找即时反馈开关并添加 checked 属性
    pattern = r'(<input type="checkbox" id="instant-feedback-toggle">)'
    replacement = r'<input type="checkbox" id="instant-feedback-toggle" checked>'
    
    if pattern in content:
        new_content = re.sub(pattern, replacement, content)
        
        # 写回文件
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✓ 已修复即时反馈开关的默认状态")
    else:
        print("✗ 未找到即时反馈开关")

def fix_embarrass_audio():
    """修复 embarrass 单词的美音映射"""
    print("\n=== 修复 embarrass 单词的美音映射 ===")
    
    # 检查音频文件是否存在
    old_audio = "eus71500.mp3"
    new_audio = "cambridge-eus71500.mp3"
    
    old_path = os.path.join(MEDIA_DIR, old_audio)
    new_path = os.path.join(MEDIA_DIR, new_audio)
    
    if os.path.exists(old_path):
        if not os.path.exists(new_path):
            # 复制文件
            import shutil
            shutil.copy2(old_path, new_path)
            print(f"✓ 已复制 {old_audio} 到 {new_audio}")
        else:
            print(f"✓ {new_audio} 已存在")
    else:
        print(f"✗ 源文件 {old_audio} 不存在")
    
    # 更新数据库中的音频映射
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查找 embarrass 单词
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.audio_path_uk, w.audio_path_us
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE (b.book_name = 'senior_high' OR b.book_name = '高中英语词汇')
        AND w.spelling = 'embarrass'
    """)
    
    word = cursor.fetchone()
    if word:
        print(f"找到单词: {word['spelling']}")
        print(f"当前英音: {word['audio_path_uk']}")
        print(f"当前美音: {word['audio_path_us']}")
        
        # 更新美音
        cursor.execute("""
            UPDATE Words 
            SET audio_path_us = ?
            WHERE word_id = ?
        """, (new_audio, word['word_id']))
        
        conn.commit()
        print(f"✓ 已更新 embarrass 的美音为: {new_audio}")
    else:
        print("✗ 未找到 embarrass 单词")
    
    conn.close()

def fix_shall_meaning():
    """修复 shall 单词的中文释义"""
    print("\n=== 修复 shall 单词的中文释义 ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查找 shall 单词
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE (b.book_name = 'senior_high' OR b.book_name = '高中英语词汇')
        AND w.spelling = 'shall'
    """)
    
    word = cursor.fetchone()
    if word:
        print(f"找到单词: {word['spelling']}")
        print(f"当前释义: {word['meaning_cn']}")
        
        # 更新为正确的中文释义
        correct_meaning = "将，将要；应该，必须"
        cursor.execute("""
            UPDATE Words 
            SET meaning_cn = ?
            WHERE word_id = ?
        """, (correct_meaning, word['word_id']))
        
        conn.commit()
        print(f"✓ 已更新 shall 的释义为: {correct_meaning}")
    else:
        print("✗ 未找到 shall 单词")
    
    conn.close()

def verify_fixes():
    """验证修复结果"""
    print("\n=== 验证修复结果 ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 验证 embarrass
    cursor.execute("""
        SELECT w.spelling, w.audio_path_uk, w.audio_path_us
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE (b.book_name = 'senior_high' OR b.book_name = '高中英语词汇')
        AND w.spelling = 'embarrass'
    """)
    
    embarrass = cursor.fetchone()
    if embarrass:
        print(f"embarrass 音频映射:")
        print(f"  英音: {embarrass['audio_path_uk']}")
        print(f"  美音: {embarrass['audio_path_us']}")
        
        # 检查音频文件是否存在
        if embarrass['audio_path_us']:
            us_path = os.path.join(MEDIA_DIR, embarrass['audio_path_us'])
            if os.path.exists(us_path):
                print("  ✓ 美音文件存在")
            else:
                print("  ✗ 美音文件不存在")
    
    # 验证 shall
    cursor.execute("""
        SELECT w.spelling, w.meaning_cn
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE (b.book_name = 'senior_high' OR b.book_name = '高中英语词汇')
        AND w.spelling = 'shall'
    """)
    
    shall = cursor.fetchone()
    if shall:
        print(f"\nshall 释义: {shall['meaning_cn']}")
    
    conn.close()

def main():
    """主函数"""
    print("开始修复问题...\n")
    
    # 1. 修复即时反馈功能
    fix_instant_feedback_default()
    
    # 2. 修复 embarrass 音频
    fix_embarrass_audio()
    
    # 3. 修复 shall 释义
    fix_shall_meaning()
    
    # 4. 验证修复结果
    verify_fixes()
    
    print("\n=== 修复完成 ===")
    print("请重启应用以使即时反馈功能生效")

if __name__ == "__main__":
    main() 