import sqlite3
import os

# 数据库文件路径
DATABASE_FILE = 'vocabulary.db'

def get_db_connection():
    """连接到数据库"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def check_alan_errors():
    """检查Alan在2025-06-28的错误记录数量"""
    try:
        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询Alan在2025-06-28的错误记录数量
        cursor.execute(
            "SELECT COUNT(*) as count FROM ErrorLogs WHERE student_id = 3 AND error_date = ?", 
            ('2025-06-28',)
        )
        result = cursor.fetchone()
        print(f"Alan在2025-06-28的错误记录数: {result['count']}")
        
        # 查询具体的错误记录
        cursor.execute(
            """SELECT e.error_id, e.word_id, w.spelling, e.student_answer, e.error_date 
               FROM ErrorLogs e 
               JOIN Words w ON e.word_id = w.word_id 
               WHERE e.student_id = 3 AND e.error_date = ? 
               ORDER BY e.error_id""", 
            ('2025-06-28',)
        )
        records = cursor.fetchall()
        
        print("\n错误记录详情:")
        for record in records:
            print(f"ID: {record['error_id']}, 单词ID: {record['word_id']}, 单词: {record['spelling']}, 学生答案: {record['student_answer']}")
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_alan_errors()