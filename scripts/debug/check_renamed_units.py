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
        WHERE book_id = ?
        ORDER BY list_id
    """, (book_id,))
    units = cursor.fetchall()
    
    print(f"\n单元信息:")
    print("-" * 60)
    print(f"{'ID':<5} {'单元名称':<30} {'单词数量':<10}")
    print("-" * 60)
    
    # 检查是否还有包含"Word List"的单元
    word_list_units = []
    unit_units = []
    other_units = []
    
    for unit in units:
        unit_id, unit_name, word_count = unit
        print(f"{unit_id:<5} {unit_name:<30} {word_count:<10}")
        
        if "Word List" in unit_name:
            word_list_units.append(unit)
        elif unit_name.startswith("Unit"):
            unit_units.append(unit)
        else:
            other_units.append(unit)
    
    print("-" * 60)
    print(f"总单元数: {len(units)}")
    print(f"总单词数: {sum(unit[2] for unit in units)}")
    
    print(f"\n单元类型统计:")
    print(f"包含'Word List'的单元数: {len(word_list_units)}")
    print(f"包含'Unit'的单元数: {len(unit_units)}")
    print(f"其他类型单元数: {len(other_units)}")
    
    # 检查是否有名为"Word List"的单元
    cursor.execute("SELECT COUNT(*) FROM WordLists WHERE book_id = ? AND list_name LIKE 'Word List%'", (book_id,))
    word_list_count = cursor.fetchone()[0]
    
    if word_list_count > 0:
        print(f"\n警告：仍有 {word_list_count} 个包含'Word List'的单元未被重命名！")
    else:
        print(f"\n所有'Word List'单元已成功重命名为'Unit'")
else:
    print("未找到高中英语词汇词书")

# 关闭连接
conn.close()