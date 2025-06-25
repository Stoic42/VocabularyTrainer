import sqlite3

# 连接到数据库
conn = sqlite3.connect('vocabulary.db')
cursor = conn.cursor()

# 查询所有词书
cursor.execute("SELECT book_id, book_name FROM Books ORDER BY book_id")
books = cursor.fetchall()

print("数据库中的词书:")
for book_id, book_name in books:
    # 查询单元数量
    cursor.execute("SELECT COUNT(*) FROM WordLists WHERE book_id = ?", (book_id,))
    list_count = cursor.fetchone()[0]
    
    # 查询单词数量
    cursor.execute("""
        SELECT COUNT(*) FROM Words 
        WHERE list_id IN (SELECT list_id FROM WordLists WHERE book_id = ?)
    """, (book_id,))
    word_count = cursor.fetchone()[0]
    
    print(f"ID: {book_id}, 名称: {book_name}, 单元数: {list_count}, 单词数: {word_count}")

print(f"总词书数: {len(books)}")

# 关闭连接
conn.close()