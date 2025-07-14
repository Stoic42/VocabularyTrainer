import sqlite3

# 数据库文件路径
DATABASE_FILE = 'd:\\Projects\\VocabularyTrainer\\vocabulary.db'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def check_words():
    """检查高中词书的单词示例"""
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
    
    # 获取高中词书的单词示例
    cursor.execute("""
    SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, wl.list_name
    FROM Words w
    JOIN WordLists wl ON w.list_id = wl.list_id
    WHERE wl.book_id = ?
    ORDER BY w.word_id
    LIMIT 20
    """, (book_id,))
    
    words = cursor.fetchall()
    
    print(f"高中词书(ID: {book_id})单词示例:")
    print("-" * 80)
    
    for word in words:
        print(f"ID: {word['word_id']}, 拼写: {word['spelling']}, 释义: {word['meaning_cn']}, 词性: {word['pos']}, 单元: {word['list_name']}")
    
    conn.close()

if __name__ == '__main__':
    check_words()