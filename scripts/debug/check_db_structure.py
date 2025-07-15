import sqlite3
import os

def get_db_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vocabulary.db'))

def check_db_structure():
    """检查数据库表结构"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 检查Words表结构
    print("\nWords表结构:")
    cursor.execute("PRAGMA table_info(Words)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 检查是否有list_id字段
    cursor.execute("SELECT * FROM Words WHERE spelling = 'pity' LIMIT 1")
    pity_sample = cursor.fetchone()
    if pity_sample:
        print(f"\npity单词示例数据:")
        print(f"  {pity_sample}")
    
    conn.close()

if __name__ == '__main__':
    check_db_structure() 