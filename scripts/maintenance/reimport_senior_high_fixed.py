from utils import get_database_connection, get_database_path
import sqlite3
import csv
import re

# 连接到数据库
conn = get_database_connection()
cursor = conn.cursor()

# 删除旧的senior_high词书及其相关数据
cursor.execute("SELECT book_id FROM Books WHERE book_name = 'senior_high'")
old_book = cursor.fetchone()
if old_book:
    old_book_id = old_book[0]
    print(f"找到旧的senior_high词书，ID为: {old_book_id}，正在删除...")
    
    # 获取所有相关单元ID
    cursor.execute("SELECT list_id FROM WordLists WHERE book_id = ?", (old_book_id,))
    list_ids = [row[0] for row in cursor.fetchall()]
    
    # 删除单词
    for list_id in list_ids:
        cursor.execute("DELETE FROM Words WHERE list_id = ?", (list_id,))
    
    # 删除单元
    cursor.execute("DELETE FROM WordLists WHERE book_id = ?", (old_book_id,))
    
    # 删除词书
    cursor.execute("DELETE FROM Books WHERE book_id = ?", (old_book_id,))
    
    print(f"已删除旧的senior_high词书及其相关数据")

# 创建新的高中英语词汇词书
cursor.execute("INSERT INTO Books (book_name) VALUES ('高中英语词汇')")
book_id = cursor.lastrowid
print(f"已创建新的高中英语词汇词书，ID为: {book_id}")

# 读取CSV文件并导入数据
csv_file = 'wordlists/senior_high/senior_high_complete.csv'

# 用于跟踪已创建的单元
created_units = {}

# 用于统计导入的单词数量
word_count = 0

# 读取CSV文件
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 3:  # 确保行有足够的列
            unit_name = row[0].strip()  # 去除前后空格
            spelling = row[1].strip()
            pronunciation = row[2].strip() if len(row) > 2 else ""
            meaning = row[3].strip() if len(row) > 3 else ""
            example = row[4].strip() if len(row) > 4 else ""
            
            # 提取词性
            pos = ""
            if meaning and re.search(r'^[a-zA-Z]+\.', meaning):
                pos_match = re.match(r'^([a-zA-Z]+\.)', meaning)
                if pos_match:
                    pos = pos_match.group(1)
            
            # 检查单元是否已创建
            if unit_name not in created_units:
                cursor.execute("INSERT INTO WordLists (list_name, book_id) VALUES (?, ?)", (unit_name, book_id))
                unit_id = cursor.lastrowid
                created_units[unit_name] = unit_id
                print(f"创建单元: {unit_name}, ID: {unit_id}")
            else:
                unit_id = created_units[unit_name]
            
            # 插入单词
            cursor.execute("""
                INSERT INTO Words (spelling, meaning_cn, pos, list_id) 
                VALUES (?, ?, ?, ?)
            """, (spelling, meaning, pos, unit_id))
            word_count += 1

# 提交事务
conn.commit()

# 打印导入结果
print(f"\n导入完成！")
print(f"总共导入了 {word_count} 个单词")
print(f"创建了 {len(created_units)} 个单元")

# 关闭连接
conn.close()