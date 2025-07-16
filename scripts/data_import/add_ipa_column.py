#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给数据库添加IPA字段
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os

# 配置
DATABASE_FILE = get_database_path()

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def add_ipa_column():
    """给Words表添加IPA字段"""
    print("正在给Words表添加IPA字段...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查IPA字段是否已存在
        cursor.execute("PRAGMA table_info(Words)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'ipa' in column_names:
            print("IPA字段已存在，跳过添加。")
            return
        
        # 添加IPA字段
        cursor.execute("ALTER TABLE Words ADD COLUMN ipa TEXT")
        conn.commit()
        print("IPA字段添加成功！")
        
    except Exception as e:
        print(f"添加IPA字段时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """主执行函数"""
    # 检查数据库是否存在
    if not os.path.exists(DATABASE_FILE):
        print(f"错误: 找不到数据库文件 '{DATABASE_FILE}'")
        return
    
    add_ipa_column()
    print("操作已完成。")

if __name__ == '__main__':
    main() 