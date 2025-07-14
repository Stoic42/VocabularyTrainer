import os
import sys

# 添加scripts目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.dirname(current_dir)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from utils import get_database_connection, get_database_path
import sqlite3

# 数据库文件路径
DATABASE_FILE = get_database_path()

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def check_database():
    """检查数据库中的高中词汇数据"""
    if not os.path.exists(DATABASE_FILE):
        print(f"错误: 找不到数据库文件 '{DATABASE_FILE}'")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查词书
    print("=== 词书信息 ===")
    cursor.execute("SELECT book_id, book_name FROM Books")
    books = cursor.fetchall()
    for book in books:
        print(f"ID: {book['book_id']}, 名称: {book['book_name']}")
    
    # 检查高中词书的单元
    print("\n=== 高中词书单元信息 ===")
    cursor.execute("""
    SELECT wl.list_id, wl.list_name, b.book_name, COUNT(w.word_id) as word_count
    FROM WordLists wl
    JOIN Books b ON wl.book_id = b.book_id
    LEFT JOIN Words w ON wl.list_id = w.list_id
    WHERE b.book_name LIKE '%高中%'
    GROUP BY wl.list_id
    ORDER BY wl.list_id
    """)
    lists = cursor.fetchall()
    if lists:
        for list_info in lists:
            print(f"单元ID: {list_info['list_id']}, 名称: {list_info['list_name']}, "
                  f"词书: {list_info['book_name']}, 单词数: {list_info['word_count']}")
    else:
        print("未找到高中词书的单元信息")
    
    # 检查高中词书的单词数量
    print("\n=== 高中词书单词统计 ===")
    cursor.execute("""
    SELECT COUNT(w.word_id) as total_words
    FROM Words w
    JOIN WordLists wl ON w.list_id = wl.list_id
    JOIN Books b ON wl.book_id = b.book_id
    WHERE b.book_name LIKE '%高中%'
    """)
    result = cursor.fetchone()
    if result:
        print(f"高中词书总单词数: {result['total_words']}")
    else:
        print("未找到高中词书的单词")
    
    # 检查部分高中词汇单词示例
    print("\n=== 高中词书单词示例 ===")
    cursor.execute("""
    SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, wl.list_name
    FROM Words w
    JOIN WordLists wl ON w.list_id = wl.list_id
    JOIN Books b ON wl.book_id = b.book_id
    WHERE b.book_name LIKE '%高中%'
    LIMIT 10
    """)
    words = cursor.fetchall()
    if words:
        for word in words:
            print(f"ID: {word['word_id']}, 拼写: {word['spelling']}, "
                  f"释义: {word['meaning_cn']}, 词性: {word['pos']}, 单元: {word['list_name']}")
    else:
        print("未找到高中词书的单词示例")
    
    conn.close()

if __name__ == '__main__':
    check_database()