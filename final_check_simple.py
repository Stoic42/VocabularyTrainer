import sqlite3

# 连接到数据库
conn = sqlite3.connect('vocabulary.db')
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
        WHERE book_id = ?
        ORDER BY list_id
    """, (book_id,))
    units = cursor.fetchall()
    
    # 检查是否还有包含"Word List"的单元
    word_list_units = []
    unit_units = []
    other_units = []
    
    for unit in units:
        unit_id, unit_name, word_count = unit
        
        if "Word List" in unit_name:
            word_list_units.append(unit)
        elif unit_name.startswith("Unit"):
            unit_units.append(unit)
        else:
            other_units.append(unit)
    
    print(f"\n单元类型统计:")
    print(f"总单元数: {len(units)}")
    print(f"总单词数: {sum(unit[2] for unit in units)}")
    print(f"包含'Word List'的单元数: {len(word_list_units)}")
    print(f"包含'Unit'的单元数: {len(unit_units)}")
    print(f"其他类型单元数: {len(other_units)}")
    
    # 如果有包含"Word List"的单元，显示它们
    if word_list_units:
        print("\n包含'Word List'的单元:")
        for unit in word_list_units:
            print(f"ID: {unit[0]}, 名称: {unit[1]}, 单词数: {unit[2]}")
    else:
        print(f"\n所有'Word List'单元已成功处理")
else:
    print("未找到高中英语词汇词书")

# 关闭连接
conn.close()