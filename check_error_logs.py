import sqlite3
import os

# 数据库文件路径
DATABASE_FILE = 'vocabulary.db'

# 检查数据库文件是否存在
if not os.path.exists(DATABASE_FILE):
    print(f"错误：数据库文件 {DATABASE_FILE} 不存在")
    exit(1)

# 连接数据库
conn = sqlite3.connect(DATABASE_FILE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 检查 ErrorLogs 表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ErrorLogs';")
if not cursor.fetchone():
    print("错误：ErrorLogs 表不存在")
    # 列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库中的表：")
    for table in tables:
        print(f"- {table['name']}")
    conn.close()
    exit(1)

# 查询错误日期统计
print("\n错误日期统计：")
cursor.execute("SELECT error_date, COUNT(*) as count FROM ErrorLogs GROUP BY error_date ORDER BY error_date DESC;")
date_stats = cursor.fetchall()
if date_stats:
    for stat in date_stats:
        print(f"日期: {stat['error_date']}, 错误数: {stat['count']}")
else:
    print("没有找到错误记录")

# 查询 Alan 的错误记录（假设 Alan 的用户 ID 是 1）
print("\n查询 Alan 的错误记录：")
cursor.execute("""
    SELECT e.student_id, e.error_date, COUNT(*) as count 
    FROM ErrorLogs e 
    GROUP BY e.student_id, e.error_date 
    ORDER BY e.error_date DESC;
""")
user_stats = cursor.fetchall()
if user_stats:
    for stat in user_stats:
        print(f"用户ID: {stat['student_id']}, 日期: {stat['error_date']}, 错误数: {stat['count']}")
else:
    print("没有找到用户错误记录")

# 查询所有表
print("\n数据库中的所有表：")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
if tables:
    for table in tables:
        print(f"- {table['name']}")
        # 显示表结构
        cursor.execute(f"PRAGMA table_info({table['name']})")
        columns = cursor.fetchall()
        print("  列结构:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
else:
    print("没有找到表")

# 关闭连接
conn.close()