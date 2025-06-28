import sqlite3

# 连接数据库
conn = sqlite3.connect('vocabulary.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 查询 Alan（用户 ID 为 3）在特定日期的错词记录
print('Alan 的错词记录:')
cursor.execute("""
    SELECT error_date, COUNT(*) as count 
    FROM ErrorLogs 
    WHERE student_id = 3 
    AND error_date IN ('2025-06-25', '2025-06-26', '2025-06-27') 
    GROUP BY error_date 
    ORDER BY error_date
""")

results = cursor.fetchall()
for row in results:
    print(f'日期: {row["error_date"]}, 错误数: {row["count"]}')

# 查询 Alan 的所有错词记录（按日期分组）
print('\nAlan 的所有错词记录（按日期分组）:')
cursor.execute("""
    SELECT error_date, COUNT(*) as count 
    FROM ErrorLogs 
    WHERE student_id = 3 
    GROUP BY error_date 
    ORDER BY error_date
""")

results = cursor.fetchall()
for row in results:
    print(f'日期: {row["error_date"]}, 错误数: {row["count"]}')

# 查询 Alan 在 6 月 26 日的具体错词
print('\nAlan 在 2025-06-26 的具体错词:')
cursor.execute("""
    SELECT e.error_id, e.error_date, w.spelling, w.meaning_cn, e.error_type, e.student_answer 
    FROM ErrorLogs e 
    JOIN Words w ON e.word_id = w.word_id 
    WHERE e.student_id = 3 AND e.error_date = '2025-06-26' 
    ORDER BY e.error_id
""")

results = cursor.fetchall()
if results:
    for row in results:
        print(f'ID: {row["error_id"]}, 单词: {row["spelling"]}, 含义: {row["meaning_cn"]}, 错误类型: {row["error_type"]}, 学生答案: {row["student_answer"]}')
else:
    print('没有找到记录')

# 关闭连接
conn.close()