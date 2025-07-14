from utils import get_database_connection, get_database_path
import sqlite3

# 连接到数据库
conn = get_database_connection()
cursor = conn.cursor()

# 获取高中英语词汇词书的ID
cursor.execute("SELECT book_id FROM Books WHERE book_name = '高中英语词汇'")
book_id = cursor.fetchone()

if book_id:
    book_id = book_id[0]
    print(f"找到高中英语词汇词书，ID为: {book_id}")
    
    # 查询名为"Word List"的单元
    cursor.execute("""
        SELECT list_id, list_name, 
        (SELECT COUNT(*) FROM Words WHERE list_id = WordLists.list_id) as word_count 
        FROM WordLists 
        WHERE book_id = ? AND list_name = 'Word List'
    """, (book_id,))
    unit = cursor.fetchone()
    
    if unit:
        unit_id, unit_name, word_count = unit
        print(f"\n找到名为'{unit_name}'的单元，ID为: {unit_id}，包含 {word_count} 个单词")
        
        # 查询该单元中的单词
        cursor.execute("SELECT word_id, spelling, meaning_cn FROM Words WHERE list_id = ?", (unit_id,))
        words = cursor.fetchall()
        
        print("\n该单元中的单词:")
        for word in words:
            word_id, spelling, meaning = word
            print(f"ID: {word_id}, 单词: {spelling}, 释义: {meaning}")
        
        # 删除该单元中的单词
        cursor.execute("DELETE FROM Words WHERE list_id = ?", (unit_id,))
        print(f"\n已删除单元中的 {len(words)} 个单词")
        
        # 删除该单元
        cursor.execute("DELETE FROM WordLists WHERE list_id = ?", (unit_id,))
        print(f"已删除名为'{unit_name}'的单元")
        
        # 提交事务
        conn.commit()
        print("\n删除操作已完成")
    else:
        print("未找到名为'Word List'的单元")
else:
    print("未找到高中英语词汇词书")

# 关闭连接
conn.close()