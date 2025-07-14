from utils import get_database_connection, get_database_path
import sqlite3
import re

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
        SELECT list_id, list_name
        FROM WordLists 
        WHERE book_id = ? AND list_name LIKE 'Word List%'
        ORDER BY list_id
    """, (book_id,))
    units = cursor.fetchall()
    
    if units:
        print(f"\n找到 {len(units)} 个包含'Word List'的单元，正在重命名...")
        
        # 用于记录重命名的单元数量
        renamed_count = 0
        
        for unit_id, unit_name in units:
            # 提取数字部分
            match = re.search(r'Word List (\d+)', unit_name)
            if match:
                number = match.group(1)
                new_name = f"Unit {number}"
                
                # 更新单元名称
                cursor.execute("UPDATE WordLists SET list_name = ? WHERE list_id = ?", (new_name, unit_id))
                print(f"将 '{unit_name}' 重命名为 '{new_name}'")
                renamed_count += 1
        
        # 提交事务
        conn.commit()
        
        print(f"\n重命名完成！共重命名了 {renamed_count} 个单元")
    else:
        print("未找到包含'Word List'的单元")
else:
    print("未找到高中英语词汇词书")

# 关闭连接
conn.close()