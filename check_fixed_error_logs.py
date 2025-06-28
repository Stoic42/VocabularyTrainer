import sqlite3
import os
from datetime import datetime
import re

# 获取当前时间作为报告文件名的一部分
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 设置数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary.db")

# 设置HTML文件路径
html_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Alan", "20250628", "index25.html")

# 创建报告文件
report_file = f"check_fixed_error_logs_report_{current_time}.txt"
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), report_file)

try:
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 打开报告文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("检查修复后的错词记录报告\n")
        f.write("===================\n\n")
        
        # 查询Alan在2025-06-25的错词记录
        f.write("查询Alan在2025-06-25的错词记录:\n")
        cursor.execute("""
            SELECT e.error_id, e.student_id, e.word_id, e.error_type, e.student_answer, e.error_date, w.spelling, w.meaning_cn
            FROM ErrorLogs e
            LEFT JOIN Words w ON e.word_id = w.word_id
            WHERE e.student_id = 3 AND e.error_date = '2025-06-25'
            ORDER BY e.error_id
        """)
        error_logs = cursor.fetchall()
        
        if error_logs:
            f.write(f"找到 {len(error_logs)} 条错词记录:\n")
            for log in error_logs:
                error_id, student_id, word_id, error_type, student_answer, error_date, spelling, meaning = log
                f.write(f"错误ID: {error_id}, 单词ID: {word_id}, 单词: {spelling}, 释义: {meaning}, ")
                f.write(f"错误类型: {error_type}, 学生答案: {student_answer}, 日期: {error_date}\n")
        else:
            f.write("未找到错词记录\n")
        
        f.write("\n")
        
        # 检查HTML文件是否存在
        if os.path.exists(html_file_path):
            f.write(f"检查HTML文件: {html_file_path}\n")
            
            # 读取HTML文件内容
            with open(html_file_path, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
            
            # 检查HTML文件中是否包含错词记录
            f.write("检查HTML文件中的错词记录:\n")
            
            # 提取HTML中的错词记录
            word_pattern = r'<tr>\s*<td>(\d+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]*)</td>\s*</tr>'
            html_words = re.findall(word_pattern, html_content)
            
            if html_words:
                f.write(f"在HTML文件中找到 {len(html_words)} 条错词记录:\n")
                for i, (index, word, meaning, error_type, student_answer) in enumerate(html_words, 1):
                    f.write(f"{i}. 序号: {index}, 单词: {word}, 释义: {meaning}, 错误类型: {error_type}, 学生答案: {student_answer}\n")
                
                # 比较数据库和HTML中的错词记录
                f.write("\n比较数据库和HTML中的错词记录:\n")
                db_words = [(str(i+1), log[6], log[7], log[3], log[4]) for i, log in enumerate(error_logs)]
                
                # 检查数据库中的单词是否都在HTML中
                missing_in_html = []
                for i, (index, word, meaning, error_type, student_answer) in enumerate(db_words):
                    found = False
                    for html_index, html_word, html_meaning, html_error_type, html_student_answer in html_words:
                        if word == html_word:
                            found = True
                            break
                    if not found:
                        missing_in_html.append((index, word, meaning, error_type, student_answer))
                
                if missing_in_html:
                    f.write(f"数据库中有 {len(missing_in_html)} 条记录在HTML中未找到:\n")
                    for index, word, meaning, error_type, student_answer in missing_in_html:
                        f.write(f"序号: {index}, 单词: {word}, 释义: {meaning}, 错误类型: {error_type}, 学生答案: {student_answer}\n")
                else:
                    f.write("数据库中的所有单词都在HTML中找到\n")
                
                # 检查HTML中的单词是否都在数据库中
                missing_in_db = []
                for html_index, html_word, html_meaning, html_error_type, html_student_answer in html_words:
                    found = False
                    for index, word, meaning, error_type, student_answer in db_words:
                        if html_word == word:
                            found = True
                            break
                    if not found:
                        missing_in_db.append((html_index, html_word, html_meaning, html_error_type, html_student_answer))
                
                if missing_in_db:
                    f.write(f"HTML中有 {len(missing_in_db)} 条记录在数据库中未找到:\n")
                    for html_index, html_word, html_meaning, html_error_type, html_student_answer in missing_in_db:
                        f.write(f"序号: {html_index}, 单词: {html_word}, 释义: {html_meaning}, 错误类型: {html_error_type}, 学生答案: {html_student_answer}\n")
                else:
                    f.write("HTML中的所有单词都在数据库中找到\n")
            else:
                f.write("在HTML文件中未找到错词记录\n")
        else:
            f.write(f"HTML文件不存在: {html_file_path}\n")
        
        f.write("\n")
        
        # 总结
        f.write("总结:\n")
        f.write("1. 已查询Alan在2025-06-25的错词记录\n")
        if os.path.exists(html_file_path):
            if html_words:
                f.write(f"2. 在HTML文件中找到 {len(html_words)} 条错词记录\n")
                if not missing_in_html and not missing_in_db:
                    f.write("3. 数据库和HTML中的错词记录完全匹配\n")
                else:
                    if missing_in_html:
                        f.write(f"3. 数据库中有 {len(missing_in_html)} 条记录在HTML中未找到\n")
                    if missing_in_db:
                        f.write(f"4. HTML中有 {len(missing_in_db)} 条记录在数据库中未找到\n")
            else:
                f.write("2. 在HTML文件中未找到错词记录\n")
        else:
            f.write(f"2. HTML文件不存在: {html_file_path}\n")
        
        f.write("\n检查完成\n")
    
    print(f"报告已生成: {report_path}")

except sqlite3.Error as e:
    print(f"数据库错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    if 'conn' in locals():
        conn.close()