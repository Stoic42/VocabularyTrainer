import sqlite3
import os
import sys

# 添加scripts目录到Python路径，确保能导入utils模块
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.dirname(current_dir)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from utils import get_database_path

db_path = get_database_path()
print(f"检查数据库文件: {db_path}")
print(f"文件是否存在: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print("数据库文件不存在！")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print(f"\n数据库中的表 (共 {len(tables)} 个):")
    for table in tables:
        print(f"  - {table[0]}")

    # 检查是否有Books表
    if any(table[0] == 'Books' for table in tables):
        print("\nBooks表存在，检查内容:")
        cursor.execute("SELECT * FROM Books LIMIT 5")
        books = cursor.fetchall()
        for book in books:
            print(f"  - {book}")
    else:
        print("\nBooks表不存在！")

    conn.close()
    
except Exception as e:
    print(f"错误: {e}") 