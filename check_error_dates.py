import sqlite3
import os

# 数据库文件路径
DATABASE_FILE = 'vocabulary.db'

def get_db_connection():
    """连接到数据库"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def check_error_dates():
    """检查ErrorLogs表中的错误日期格式"""
    try:
        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询错误日期
        cursor.execute("SELECT error_id, student_id, error_date FROM ErrorLogs LIMIT 10")
        records = cursor.fetchall()
        
        print("错误日期示例:")
        for record in records:
            print(f"ID: {record['error_id']}, 学生ID: {record['student_id']}, 日期: {record['error_date']}")
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_error_dates()