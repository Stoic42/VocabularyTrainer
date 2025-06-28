import sqlite3
import os
from datetime import datetime

# 连接到数据库
conn = sqlite3.connect('vocabulary.db')
cursor = conn.cursor()

# 获取当前时间作为报告文件名的一部分
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 创建报告文件
report_file = f"d:/Projects/VocabularyTrainer/student3_error_report_{current_time}.txt"

# 查询学生信息
cursor.execute('SELECT id, username FROM Users')
students = cursor.fetchall()

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("学生ID和姓名:\n")
    for student in students:
        f.write(f"{student[0]}: {student[1]}\n")
    
    # 查询student_id=3在2025-06-27的错词数量
    cursor.execute('SELECT COUNT(*) FROM ErrorLogs WHERE student_id = 3 AND error_date = "2025-06-27"')
    error_count = cursor.fetchone()[0]
    f.write(f"\nstudent_id=3在2025-06-27的错词数量: {error_count}\n")
    
    # 如果有错词，查询详细信息
    if error_count > 0:
        f.write("\n错词详细信息:\n")
        cursor.execute("""
        SELECT e.error_id, w.spelling, w.pos, w.meaning_cn, b.book_name, l.list_name, e.student_answer, e.error_date, 1 as error_count
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        JOIN WordLists l ON w.list_id = l.list_id
        JOIN Books b ON l.book_id = b.book_id
        WHERE e.student_id = 3 AND e.error_date = "2025-06-27"
        ORDER BY e.error_id
        LIMIT 10
        """)
        errors = cursor.fetchall()
        for error in errors:
            f.write(f"ID: {error[0]}, 单词: {error[1]}, 词性: {error[2]}, 中文释义: {error[3]}\n")
            f.write(f"词书: {error[4]}, 单元: {error[5]}, 错误答案: {error[6]}, 日期: {error[7]}, 错误次数: {error[8]}\n\n")

# 关闭连接
conn.close()

print(f"报告已生成: {report_file}")