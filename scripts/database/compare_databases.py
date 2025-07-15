#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库对比和同步脚本
对比本地和服务器数据库的差异，并同步新用户数据
"""

import sqlite3
import os
import sys
from datetime import datetime

# 添加scripts目录到Python路径，确保能导入utils模块
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.dirname(current_dir)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from utils import get_database_path

def get_db_connection(db_path):
    """创建数据库连接"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def compare_tables(local_db, server_db, table_name):
    """对比两个数据库中的表"""
    print(f"\n=== 对比表: {table_name} ===")
    
    local_conn = get_db_connection(local_db)
    server_conn = get_db_connection(server_db)
    
    try:
        # 获取表结构
        local_cursor = local_conn.execute(f"PRAGMA table_info({table_name})")
        server_cursor = server_conn.execute(f"PRAGMA table_info({table_name})")
        
        local_columns = [row['name'] for row in local_cursor.fetchall()]
        server_columns = [row['name'] for row in server_cursor.fetchall()]
        
        print(f"本地表列: {local_columns}")
        print(f"服务器表列: {server_columns}")
        
        # 获取记录数
        local_count = local_conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchone()['count']
        server_count = server_conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchone()['count']
        
        print(f"本地记录数: {local_count}")
        print(f"服务器记录数: {server_count}")
        
        # 对比Words表的具体内容
        if table_name == 'Words':
            print("\n--- Words表内容对比 ---")
            
            # 检查表结构，找到正确的列名
            word_column = None
            meaning_column = None
            pos_column = None
            
            for col in local_columns:
                if 'word' in col.lower():
                    word_column = col
                if 'meaning' in col.lower():
                    meaning_column = col
                if 'pos' in col.lower():
                    pos_column = col
            
            print(f"使用的列名: word={word_column}, meaning={meaning_column}, pos={pos_column}")
            
            if word_column and meaning_column:
                # 检查一些具体的单词
                test_words = ['apple', 'book', 'cat', 'dog', 'elephant']
                for word in test_words:
                    local_word = local_conn.execute(f"SELECT * FROM Words WHERE {word_column} = ?", (word,)).fetchone()
                    server_word = server_conn.execute(f"SELECT * FROM Words WHERE {word_column} = ?", (word,)).fetchone()
                    
                    if local_word and server_word:
                        print(f"\n单词: {word}")
                        print(f"  本地释义: {local_word[meaning_column]}")
                        print(f"  服务器释义: {server_word[meaning_column]}")
                        if pos_column:
                            print(f"  本地POS: {local_word[pos_column]}")
                            print(f"  服务器POS: {server_word[pos_column]}")
                    elif local_word:
                        print(f"\n单词: {word} - 只在本地存在")
                    elif server_word:
                        print(f"\n单词: {word} - 只在服务器存在")
        
        # 对比Users表
        elif table_name == 'Users':
            print("\n--- Users表内容对比 ---")
            
            # 获取所有用户
            local_users = local_conn.execute("SELECT * FROM Users ORDER BY id").fetchall()
            server_users = server_conn.execute("SELECT * FROM Users ORDER BY id").fetchall()
            
            print(f"本地用户数: {len(local_users)}")
            print(f"服务器用户数: {len(server_users)}")
            
            # 找出新用户
            local_user_ids = {user['id'] for user in local_users}
            server_user_ids = {user['id'] for user in server_users}
            
            new_users = server_user_ids - local_user_ids
            if new_users:
                print(f"\n新用户ID: {new_users}")
                for user_id in new_users:
                    user = server_conn.execute("SELECT * FROM Users WHERE id = ?", (user_id,)).fetchone()
                    role = user['role'] if 'role' in user.keys() else 'N/A'
                    print(f"  新用户: ID={user['id']}, 用户名={user['username']}, 角色={role}")
        
        # 对比ErrorLogs表
        elif table_name == 'ErrorLogs':
            print("\n--- ErrorLogs表内容对比 ---")
            
            # 获取错误日志数量
            local_errors = local_conn.execute("SELECT COUNT(*) as count FROM ErrorLogs").fetchone()['count']
            server_errors = server_conn.execute("SELECT COUNT(*) as count FROM ErrorLogs").fetchone()['count']
            
            print(f"本地错误日志数: {local_errors}")
            print(f"服务器错误日志数: {server_errors}")
            
            # 获取新用户的错误日志
            if 'new_users' in locals():
                for user_id in new_users:
                    user_errors = server_conn.execute("SELECT COUNT(*) as count FROM ErrorLogs WHERE student_id = ?", (user_id,)).fetchone()['count']
                    print(f"  用户{user_id}的错误日志数: {user_errors}")
        
    except Exception as e:
        print(f"对比表 {table_name} 时出错: {e}")
    
    finally:
        local_conn.close()
        server_conn.close()

def sync_new_users(local_db, server_db):
    """同步新用户数据到本地数据库"""
    print("\n=== 同步新用户数据 ===")
    
    local_conn = get_db_connection(local_db)
    server_conn = get_db_connection(server_db)
    
    try:
        # 获取用户ID
        local_users = local_conn.execute("SELECT id FROM Users").fetchall()
        server_users = server_conn.execute("SELECT id FROM Users").fetchall()
        
        local_user_ids = {user['id'] for user in local_users}
        server_user_ids = {user['id'] for user in server_users}
        
        new_user_ids = server_user_ids - local_user_ids
        
        if not new_user_ids:
            print("没有新用户需要同步")
            return
        
        print(f"发现 {len(new_user_ids)} 个新用户需要同步")
        
        # 同步新用户
        for user_id in new_user_ids:
            user = server_conn.execute("SELECT * FROM Users WHERE id = ?", (user_id,)).fetchone()
            
            # 检查role列是否存在
            role = user['role'] if 'role' in user.keys() else 'student'
            
            # 插入用户
            local_conn.execute("""
                INSERT INTO Users (id, username, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, (user['id'], user['username'], user['password_hash'], role))
            
            print(f"同步用户: {user['username']} (ID: {user['id']})")
        
        # 同步新用户的错误日志
        for user_id in new_user_ids:
            errors = server_conn.execute("SELECT * FROM ErrorLogs WHERE student_id = ?", (user_id,)).fetchall()
            
            for error in errors:
                # 检查details列是否存在
                details = error['details'] if 'details' in error.keys() else ''
                
                local_conn.execute("""
                    INSERT INTO ErrorLogs (id, student_id, word_id, error_type, timestamp, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (error['id'], error['student_id'], error['word_id'], 
                      error['error_type'], error['timestamp'], details))
            
            print(f"同步用户 {user_id} 的 {len(errors)} 条错误日志")
        
        # 提交更改
        local_conn.commit()
        print("新用户数据同步完成！")
        
    except Exception as e:
        print(f"同步新用户数据时出错: {e}")
        local_conn.rollback()
    
    finally:
        local_conn.close()
        server_conn.close()

def main():
    """主函数"""
    # 获取数据库路径
    local_db = get_database_path()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server_db = os.path.join(project_root, "vocabulary_server.db")
    
    if not os.path.exists(local_db):
        print(f"错误: 本地数据库 {local_db} 不存在")
        return
    
    if not os.path.exists(server_db):
        print(f"错误: 服务器数据库 {server_db} 不存在")
        return
    
    print("=== 数据库对比工具 ===")
    print(f"本地数据库: {local_db}")
    print(f"服务器数据库: {server_db}")
    
    # 对比主要表
    tables_to_compare = ['Words', 'Users', 'ErrorLogs', 'Books']
    
    for table in tables_to_compare:
        compare_tables(local_db, server_db, table)
    
    # 询问是否同步新用户数据
    print("\n" + "="*50)
    response = input("是否要同步新用户数据到本地数据库？(y/n): ").strip().lower()
    
    if response in ['y', 'yes', '是']:
        sync_new_users(local_db, server_db)
    else:
        print("跳过数据同步")

if __name__ == "__main__":
    main() 