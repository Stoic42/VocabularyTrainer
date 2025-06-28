import sqlite3
import json
from datetime import datetime, timedelta

# 连接到数据库
conn = sqlite3.connect('d:/Projects/VocabularyTrainer/vocabulary.db')
cursor = conn.cursor()

# 模拟API请求的参数
student_id = 1  # Alan的ID
limit = 200  # 增加的limit参数
date_from = '2025-06-25'  # 从6月25日开始
date_to = '2025-06-27'  # 到6月27日结束
sort_by = 'date'  # 按日期排序
sort_order = 'desc'  # 降序排序

# 查询错误记录，并关联单词信息、词书和单元名称
query = """
SELECT e.error_id, e.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, 
       e.student_answer, e.error_type, e.error_date,
       (SELECT COUNT(*) FROM ErrorLogs WHERE word_id = e.word_id AND student_id = e.student_id) as error_count,
       wl.book_id, b.book_name, wl.list_name
FROM ErrorLogs e
JOIN Words w ON e.word_id = w.word_id
LEFT JOIN WordLists wl ON w.list_id = wl.list_id
LEFT JOIN Books b ON wl.book_id = b.book_id
WHERE e.student_id = ?
GROUP BY e.word_id, e.error_date
"""

params = [student_id]

# 添加日期范围筛选条件
if date_from is not None:
    query += " AND e.error_date >= ?"
    params.append(date_from)

if date_to is not None:
    query += " AND e.error_date <= ?"
    params.append(date_to)

# 添加排序逻辑
if sort_by == 'error_count':
    query += " ORDER BY error_count"
else:  # 默认按日期排序
    query += " ORDER BY e.error_date"

# 添加排序方向
if sort_order.lower() == 'asc':
    query += " ASC"
else:  # 默认降序
    query += " DESC"

query += " LIMIT ?"
params.append(limit)

cursor.execute(query, params)
errors = cursor.fetchall()

# 按日期分组统计错词数量
date_stats = {}
for error in errors:
    error_date = error[8]  # error_date在第9列
    if error_date not in date_stats:
        date_stats[error_date] = 0
    date_stats[error_date] += 1

# 打印统计结果
print("按日期统计错词数量:")
for date, count in sorted(date_stats.items()):
    print(f"{date}: {count}个错词")

# 打印每个日期的前5个错词
for date in sorted(date_stats.keys()):
    print(f"\n{date}的部分错词:")
    count = 0
    for error in errors:
        if error[8] == date:  # 如果是当前日期的错词
            print(f"ID: {error[0]}, 单词: {error[2]}, 错误答案: {error[6]}")
            count += 1
            if count >= 5:  # 只显示前5个
                break

conn.close()