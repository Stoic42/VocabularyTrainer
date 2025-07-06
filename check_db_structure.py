#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database_structure():
    """检查数据库结构和ErrorLogs表内容"""
    
    # 检查当前数据库
    print("=== 当前数据库结构 ===")
    if os.path.exists('vocabulary.db'):
        conn = sqlite3.connect('vocabulary.db')
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查ErrorLogs表结构
        if any('ErrorLogs' in table for table in tables):
            cursor.execute("PRAGMA table_info(ErrorLogs)")
            columns = cursor.fetchall()
            print(f"\nErrorLogs表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # 获取ErrorLogs记录数
            cursor.execute("SELECT COUNT(*) FROM ErrorLogs")
            count = cursor.fetchone()[0]
            print(f"\nErrorLogs表记录数: {count}")
            
            # 获取最近的几条记录
            cursor.execute("SELECT * FROM ErrorLogs ORDER BY timestamp DESC LIMIT 5")
            recent_records = cursor.fetchall()
            print(f"\n最近的5条ErrorLogs记录:")
            for record in recent_records:
                print(f"  {record}")
        else:
            print("当前数据库中没有ErrorLogs表")
        
        # 检查words表的结构
        cursor.execute("PRAGMA table_info(words)")
        columns = cursor.fetchall()
        print("\nwords表的列:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 检查是否有高中词书的单词
        cursor.execute("SELECT COUNT(*) FROM words")
        total_words = cursor.fetchone()[0]
        print(f"\n总单词数: {total_words}")
        
        # 检查一些示例单词
        cursor.execute("SELECT word_id, spelling, meaning_cn FROM words LIMIT 5")
        sample_words = cursor.fetchall()
        print("\n示例单词:")
        for word in sample_words:
            print(f"  ID: {word[0]}, 单词: {word[1]}, 释义: {word[2][:50]}...")
        
        conn.close()
    else:
        print("当前目录下没有vocabulary.db文件")

if __name__ == "__main__":
    check_database_structure()