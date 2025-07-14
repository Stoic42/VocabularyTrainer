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
    
    # 查询所有包含"Word List"的单元
    cursor.execute("""
        SELECT list_id, list_name, 
        (SELECT COUNT(*) FROM Words WHERE list_id = WordLists.list_id) as word_count 
        FROM WordLists 
        WHERE book_id = ? AND list_name LIKE '%Word List%'
        ORDER BY list_id
    """, (book_id,))
    units = cursor.fetchall()
    
    if units:
        print(f"\n找到 {len(units)} 个包含'Word List'的单元:")
        print("-" * 70)
        print(f"{'ID':<5} {'单元名称':<40} {'单词数量':<10} {'十六进制表示':<20}")
        print("-" * 70)
        
        for unit in units:
            unit_id, unit_name, word_count = unit
            # 将单元名称转换为十六进制表示，以查看是否有不可见字符
            hex_repr = ' '.join(f'{ord(c):02x}' for c in unit_name)
            print(f"{unit_id:<5} {unit_name:<40} {word_count:<10} {hex_repr}")
        
        # 查询这些单元中的部分单词
        for unit_id, unit_name, _ in units:
            print(f"\n单元 '{unit_name}' (ID: {unit_id}) 中的部分单词:")
            cursor.execute("""
                SELECT word_id, spelling, meaning_cn, pos 
                FROM Words 
                WHERE list_id = ? 
                LIMIT 5
            """, (unit_id,))
            words = cursor.fetchall()
            
            print("-" * 70)
            print(f"{'ID':<5} {'单词':<15} {'词性':<10} {'中文释义':<30}")
            print("-" * 70)
            
            for word in words:
                word_id, spelling, meaning, pos = word
                print(f"{word_id:<5} {spelling:<15} {pos:<10} {meaning:<30}")
    else:
        print("未找到包含'Word List'的单元")
else:
    print("未找到高中英语词汇词书")

# 关闭连接
conn.close()