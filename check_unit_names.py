import sqlite3

# 连接到数据库
conn = sqlite3.connect('vocabulary.db')
cursor = conn.cursor()

# 获取senior_high词书的ID
cursor.execute("SELECT book_id FROM Books WHERE book_name = 'senior_high'")
book_id = cursor.fetchone()

if book_id:
    book_id = book_id[0]
    print(f"找到senior_high词书，ID为: {book_id}")
    
    # 查询所有单元信息
    cursor.execute("""
        SELECT list_id, list_name, 
        (SELECT COUNT(*) FROM Words WHERE list_id = WordLists.list_id) as word_count 
        FROM WordLists 
        WHERE book_id = ?
    """, (book_id,))
    units = cursor.fetchall()
    
    print(f"\n单元信息:")
    print("-" * 50)
    print(f"{'ID':<5} {'单元名称':<30} {'单词数量':<10}")
    print("-" * 50)
    
    for unit in units:
        unit_id, unit_name, word_count = unit
        print(f"{unit_id:<5} {unit_name:<30} {word_count:<10}")
    
    print("-" * 50)
    print(f"总单元数: {len(units)}")
    
    # 特别检查是否有名为"unit"的单元
    cursor.execute("SELECT list_id, list_name FROM WordLists WHERE book_id = ? AND list_name = 'unit'", (book_id,))
    unit_unit = cursor.fetchone()
    if unit_unit:
        print(f"\n发现名为'unit'的单元，ID为: {unit_unit[0]}")
        
        # 查询该单元下的单词示例
        cursor.execute("""
            SELECT word_id, spelling, meaning_cn, pos 
            FROM Words 
            WHERE list_id = ? 
            LIMIT 10
        """, (unit_unit[0],))
        words = cursor.fetchall()
        
        print(f"\n'unit'单元下的单词示例:")
        print("-" * 70)
        print(f"{'ID':<5} {'单词':<15} {'词性':<10} {'中文释义':<30}")
        print("-" * 70)
        
        for word in words:
            word_id, spelling, chinese, pos = word
            print(f"{word_id:<5} {spelling:<15} {pos:<10} {chinese:<30}")
    else:
        print(f"\n未发现名为'unit'的单元")
else:
    print("未找到senior_high词书")

# 关闭连接
conn.close()