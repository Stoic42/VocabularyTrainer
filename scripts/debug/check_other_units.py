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
    
    # 查询所有单元
    cursor.execute("""
        SELECT list_id, list_name, 
        (SELECT COUNT(*) FROM Words WHERE list_id = WordLists.list_id) as word_count 
        FROM WordLists 
        WHERE book_id = ? AND list_name NOT LIKE 'Unit%'
        ORDER BY list_id
    """, (book_id,))
    units = cursor.fetchall()
    
    print(f"\n非'Unit'开头的单元:")
    print("-" * 60)
    print(f"{'ID':<5} {'单元名称':<30} {'单词数量':<10}")
    print("-" * 60)
    
    for unit in units:
        unit_id, unit_name, word_count = unit
        print(f"{unit_id:<5} {unit_name:<30} {word_count:<10}")
    
    print("-" * 60)
    print(f"总计: {len(units)} 个单元")
else:
    print("未找到高中英语词汇词书")

# 关闭连接
conn.close()