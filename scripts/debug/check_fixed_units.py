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
    
    # 查询所有单元信息，按ID排序
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
    print(f"{'ID':<5} {'单元名称':<30} {'单词数量':<10} {'单元名称的十六进制表示':<20}")
    print("-" * 60)
    
    for unit in units:
        unit_id, unit_name, word_count = unit
        # 将单元名称转换为十六进制表示，以查看是否有不可见字符
        hex_repr = ' '.join(f'{ord(c):02x}' for c in unit_name)
        print(f"{unit_id:<5} {unit_name:<30} {word_count:<10} {hex_repr}")
    
    print("-" * 60)
    print(f"总单元数: {len(units)}")
    print(f"总单词数: {sum(unit[2] for unit in units)}")
    
    # 检查是否有名为"Unit"的单元（不区分大小写）
    cursor.execute("SELECT list_id, list_name FROM WordLists WHERE book_id = ? AND LOWER(list_name) LIKE '%unit%'", (book_id,))
    unit_units = cursor.fetchall()
    if unit_units:
        print(f"\n发现包含'unit'的单元:")
        for unit in unit_units:
            # 将单元名称转换为十六进制表示，以查看是否有不可见字符
            hex_repr = ' '.join(f'{ord(c):02x}' for c in unit[1])
            print(f"ID: {unit[0]}, 名称: '{unit[1]}', 十六进制表示: {hex_repr}")
    else:
        print(f"\n未发现包含'unit'的单元")
else:
    print("未找到高中英语词汇词书")

# 关闭连接
conn.close()