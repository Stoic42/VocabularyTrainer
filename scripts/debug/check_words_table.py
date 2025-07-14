#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import get_database_connection, get_database_path
import sqlite3

def check_words_table():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # 检查Words表的结构
    cursor.execute("PRAGMA table_info(Words)")
    columns = cursor.fetchall()
    print("Words表的列:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 检查一些示例单词
    cursor.execute("SELECT word_id, spelling, meaning_cn FROM Words LIMIT 3")
    sample_words = cursor.fetchall()
    print("\n示例单词:")
    for word in sample_words:
        print(f"  ID: {word[0]}, 单词: {word[1]}")
        print(f"    释义: {word[2]}")
        print()
    
    # 检查高中词书的单词
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn, b.name as book_name
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.id
        JOIN Books b ON wl.book_id = b.id
        WHERE b.name LIKE '%高中%' OR b.name LIKE '%senior%'
        LIMIT 5
    """)
    senior_words = cursor.fetchall()
    print("高中词书示例单词:")
    for word in senior_words:
        print(f"  ID: {word[0]}, 单词: {word[1]}, 词书: {word[3]}")
        print(f"    释义: {word[2]}")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_words_table() 