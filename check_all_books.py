import sqlite3

# 连接到数据库
conn = sqlite3.connect('vocabulary.db')
cursor = conn.cursor()

# 查询所有词书
cursor.execute("""
    SELECT book_id, book_name, 
    (SELECT COUNT(*) FROM WordLists WHERE book_id = Books.book_id) as list_count,
    (SELECT COUNT(*) FROM Words WHERE list_id IN (SELECT list_id FROM WordLists WHERE book_id = Books.book_id)) as word_count
    FROM Books
    ORDER BY book_id
""")
books = cursor.fetchall()

print("数据库中的词书:")
print("-" * 70)
print(f"{'ID':<5} {'词书名称':<20} {'单元数量':<10} {'单词数量':<10}")
print("-" * 70)

for book in books:
    book_id, book_name, list_count, word_count = book
    print(f"{book_id:<5} {book_name:<20} {list_count:<10} {word_count:<10}")

print("-" * 70)
print(f"总词书数: {len(books)}")
print(f"总单词数: {sum(book[3] for book in books)}")

# 关闭连接
conn.close()