from utils import get_database_connection, get_database_path
import sqlite3

# 数据库文件路径
DATABASE_FILE = get_database_path()

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def check_units():
    """检查高中词书的单元信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取高中词书ID
    cursor.execute("SELECT book_id FROM Books WHERE book_name = 'senior_high'")
    book_result = cursor.fetchone()
    
    if not book_result:
        print("未找到高中词书")
        conn.close()
        return
    
    book_id = book_result['book_id']
    
    # 获取高中词书的所有单元
    cursor.execute("""
    SELECT list_id, list_name, 
           (SELECT COUNT(*) FROM Words WHERE list_id = WordLists.list_id) as word_count
    FROM WordLists 
    WHERE book_id = ?
    ORDER BY list_id
    """, (book_id,))
    
    units = cursor.fetchall()
    
    print(f"高中词书(ID: {book_id})单元信息:")
    print("-" * 50)
    print(f"{'单元ID':<8} {'单元名称':<15} {'单词数量':<10}")
    print("-" * 50)
    
    for unit in units:
        print(f"{unit['list_id']:<8} {unit['list_name']:<15} {unit['word_count']:<10}")
    
    # 统计总单元数和总单词数
    total_units = len(units)
    total_words = sum(unit['word_count'] for unit in units)
    
    print("-" * 50)
    print(f"总单元数: {total_units}")
    print(f"总单词数: {total_words}")
    
    conn.close()

if __name__ == '__main__':
    check_units()