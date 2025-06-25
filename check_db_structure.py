import sqlite3

# 连接到数据库
conn = sqlite3.connect('vocabulary.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("数据库中的表:")
for table in tables:
    print(f"- {table[0]}")
    
    # 获取每个表的结构
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    
    print("  列信息:")
    for column in columns:
        col_id, col_name, col_type, not_null, default_val, pk = column
        print(f"    {col_name} ({col_type}){'[PK]' if pk else ''}")
    print()

# 关闭连接
conn.close()