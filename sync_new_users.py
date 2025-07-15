#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步新用户数据到本地数据库
"""

import sqlite3
import os

def sync_new_users():
    """同步新用户数据到本地数据库"""
    
    local_db = "vocabulary.db"
    server_db = "vocabulary_server.db"
    
    if not os.path.exists(local_db):
        print(f"错误: 本地数据库 {local_db} 不存在")
        return
    
    if not os.path.exists(server_db):
        print(f"错误: 服务器数据库 {server_db} 不存在")
        return
    
    local_conn = sqlite3.connect(local_db)
    server_conn = sqlite3.connect(server_db)
    
    try:
        # 获取用户ID
        local_users = local_conn.execute("SELECT id FROM Users").fetchall()
        server_users = server_conn.execute("SELECT id FROM Users").fetchall()
        
        local_user_ids = {user[0] for user in local_users}
        server_user_ids = {user[0] for user in server_users}
        
        new_user_ids = server_user_ids - local_user_ids
        
        if not new_user_ids:
            print("没有新用户需要同步")
            return
        
        print(f"发现 {len(new_user_ids)} 个新用户需要同步")
        
        # 同步新用户
        for user_id in new_user_ids:
            user = server_conn.execute("SELECT * FROM Users WHERE id = ?", (user_id,)).fetchone()
            
            # 插入用户
            local_conn.execute("""
                INSERT INTO Users (id, username, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, (user[0], user[1], user[2], user[3] if len(user) > 3 else 'student'))
            
            print(f"同步用户: {user[1]} (ID: {user[0]})")
        
        # 同步新用户的错误日志
        for user_id in new_user_ids:
            errors = server_conn.execute("SELECT * FROM ErrorLogs WHERE student_id = ?", (user_id,)).fetchall()
            
            for error in errors:
                # 检查是否已存在相同的错误记录
                existing = local_conn.execute("""
                    SELECT error_id FROM ErrorLogs 
                    WHERE student_id = ? AND word_id = ? AND error_type = ? AND student_answer = ? AND error_date = ?
                """, (error[1], error[2], error[3], error[4], error[5])).fetchone()
                
                if not existing:
                    local_conn.execute("""
                        INSERT INTO ErrorLogs (error_id, student_id, word_id, error_type, student_answer, error_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (error[0], error[1], error[2], error[3], error[4], error[5]))
            
            print(f"同步用户 {user_id} 的 {len(errors)} 条错误日志")
        
        # 提交更改
        local_conn.commit()
        print("新用户数据同步完成！")
        
        # 验证同步结果
        print("\n=== 同步验证 ===")
        local_count = local_conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        server_count = server_conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        print(f"本地用户数: {local_count}")
        print(f"服务器用户数: {server_count}")
        
        local_errors = local_conn.execute("SELECT COUNT(*) FROM ErrorLogs").fetchone()[0]
        server_errors = server_conn.execute("SELECT COUNT(*) FROM ErrorLogs").fetchone()[0]
        print(f"本地错误日志数: {local_errors}")
        print(f"服务器错误日志数: {server_errors}")
        
    except Exception as e:
        print(f"同步新用户数据时出错: {e}")
        local_conn.rollback()
    
    finally:
        local_conn.close()
        server_conn.close()

if __name__ == "__main__":
    sync_new_users() 