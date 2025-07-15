#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查服务器数据库的ErrorLogs表结构，特别是details字段
"""

import sqlite3

def check_server_errorlogs():
    """检查服务器数据库的ErrorLogs表"""
    
    server_db = "vocabulary_server.db"
    
    try:
        conn = sqlite3.connect(server_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=== 服务器数据库ErrorLogs表结构 ===")
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(ErrorLogs)")
        columns = cursor.fetchall()
        
        print("ErrorLogs表列:")
        for col in columns:
            print(f"  {col['name']} ({col['type']})")
        
        # 检查是否有details字段
        has_details = any(col['name'] == 'details' for col in columns)
        print(f"\n是否有details字段: {has_details}")
        
        if has_details:
            # 查看details字段的内容示例
            print("\n=== details字段内容示例 ===")
            cursor.execute("SELECT error_id, student_id, word_id, error_type, details FROM ErrorLogs WHERE details IS NOT NULL AND details != '' LIMIT 10")
            records = cursor.fetchall()
            
            if records:
                for record in records:
                    print(f"错误ID: {record['error_id']}")
                    print(f"  学生ID: {record['student_id']}")
                    print(f"  单词ID: {record['word_id']}")
                    print(f"  错误类型: {record['error_type']}")
                    print(f"  details内容: {record['details']}")
                    print("  ---")
            else:
                print("没有找到非空的details内容")
        
        # 查看错误类型分布
        print("\n=== 错误类型分布 ===")
        cursor.execute("SELECT error_type, COUNT(*) as count FROM ErrorLogs GROUP BY error_type")
        error_types = cursor.fetchall()
        
        for error_type in error_types:
            print(f"  {error_type['error_type']}: {error_type['count']} 条")
        
        # 查看最近的几条记录
        print("\n=== 最近的5条ErrorLogs记录 ===")
        cursor.execute("SELECT * FROM ErrorLogs ORDER BY error_date DESC LIMIT 5")
        recent_records = cursor.fetchall()
        
        for record in recent_records:
            print(f"错误ID: {record['error_id']}")
            print(f"  学生ID: {record['student_id']}")
            print(f"  单词ID: {record['word_id']}")
            print(f"  错误类型: {record['error_type']}")
            print(f"  学生答案: {record['student_answer']}")
            print(f"  错误日期: {record['error_date']}")
            if has_details:
                print(f"  details: {record.get('details', 'N/A')}")
            print("  ---")
        
        conn.close()
        
    except Exception as e:
        print(f"检查服务器数据库时出错: {e}")

if __name__ == "__main__":
    check_server_errorlogs() 