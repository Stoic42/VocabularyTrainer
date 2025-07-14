from utils import get_database_connection, get_database_path
import sqlite3
import os

# 数据库文件路径
DATABASE_FILE = get_database_path()

def create_error_logs_table():
    """创建ErrorLogs表"""
    try:
        # 连接到数据库
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ErrorLogs'")
        if cursor.fetchone() is None:
            # 创建ErrorLogs表
            cursor.execute('''
            CREATE TABLE ErrorLogs (
                error_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                word_id INTEGER,
                error_type TEXT,
                student_answer TEXT,
                error_date TEXT,
                FOREIGN KEY (word_id) REFERENCES Words(word_id)
            )
            ''')
            print("ErrorLogs表创建成功！")
        else:
            print("ErrorLogs表已存在，无需创建。")
        
        # 提交事务并关闭连接
        conn.commit()
        
        # 显示所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"- {table[0]}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"创建ErrorLogs表时出错: {e}")

if __name__ == '__main__':
    create_error_logs_table()