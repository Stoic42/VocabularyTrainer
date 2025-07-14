from utils import get_database_connection, get_database_path
import sqlite3
import os

# 数据库文件路径
DATABASE_FILE = get_database_path()

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def check_books():
    """检查数据库中的词书信息"""
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
        
        # 查询该词书下的单词数量
        cursor.execute("""
        SELECT COUNT(w.word_id) as word_count
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        WHERE wl.book_id = ?
        """, (book['book_id'],))
        word_count = cursor.fetchone()['word_count']
        print(f"  单词数量: {word_count}")
        
        # 查询该词书下的单元数量
        cursor.execute("""
        SELECT COUNT(list_id) as list_count
        FROM WordLists
        WHERE book_id = ?
        """, (book['book_id'],))
        list_count = cursor.fetchone()['list_count']
        print(f"  单元数量: {list_count}")
        print()
    
    conn.close()

if __name__ == '__main__':
    check_books()