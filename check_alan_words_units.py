import sqlite3
import os
import sys
from datetime import datetime

# 获取当前时间作为报告文件名的一部分
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 设置数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary.db")

# 从HTML文件中提取的错词列表
alan_error_words = [
    "diary", "glue", "cotton", "under", "terrible", "careful", "several", "marathon", 
    "plastic", "purpose", "discovery", "seal", "reveal", "association", "clothes", 
    "convenient", "Atlantic", "author", "escalator", "nature", "cabbage", "ground", 
    "bill", "globe", "pain", "cap", "age", "Jew", "vocabulary", "dialogue", 
    "project", "list", "weekend", "matter", "pear", "positive", "hallway", "enemy", "schoolbag"
]

# 创建报告文件
report_file = f"alan_words_units_report_{current_time}.txt"
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), report_file)

try:
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 打开报告文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Alan的错词单元匹配报告\n")
        f.write("======================\n\n")
        
        # 查询初中单词书的ID
        cursor.execute("SELECT book_id, book_name FROM Books WHERE book_name LIKE '%初中%'")
        junior_books = cursor.fetchall()
        
        if not junior_books:
            f.write("未找到初中单词书\n")
        else:
            f.write("找到以下初中单词书:\n")
            for book_id, book_name in junior_books:
                f.write(f"ID: {book_id}, 名称: {book_name}\n")
            
            f.write("\n")
            
            # 查询Unit 21和Unit 22的ID
            unit_ids = []
            for book_id, _ in junior_books:
                cursor.execute("SELECT list_id, list_name FROM WordLists WHERE book_id = ? AND (list_name LIKE '%Unit 21%' OR list_name LIKE '%Unit 22%')", (book_id,))
                units = cursor.fetchall()
                for unit_id, unit_name in units:
                    unit_ids.append((unit_id, unit_name, book_id))
            
            if not unit_ids:
                f.write("未找到Unit 21或Unit 22\n")
            else:
                f.write("找到以下Unit 21和Unit 22:\n")
                for unit_id, unit_name, book_id in unit_ids:
                    f.write(f"ID: {unit_id}, 名称: {unit_name}, 所属书ID: {book_id}\n")
                
                f.write("\n")
                
                # 查询这些单元中的单词
                f.write("Unit 21和Unit 22中的单词:\n")
                unit_words = {}
                for unit_id, unit_name, book_id in unit_ids:
                    cursor.execute("SELECT word_id, spelling, meaning_cn FROM Words WHERE list_id = ?", (unit_id,))
                    words = cursor.fetchall()
                    unit_words[unit_name] = words
                    f.write(f"\n{unit_name} 包含 {len(words)} 个单词:\n")
                    for word_id, word, meaning in words:
                        f.write(f"ID: {word_id}, 单词: {word}, 释义: {meaning}\n")
                
                f.write("\n")
                
                # 检查Alan的错词是否在这些单元中
                f.write("Alan错词与Unit 21/22匹配情况:\n")
                found_count = 0
                not_found_count = 0
                found_words = []
                not_found_words = []
                
                for error_word in alan_error_words:
                    found = False
                    for unit_name, words in unit_words.items():
                        for word_id, word, meaning in words:
                            if error_word.lower() == word.lower():
                                found = True
                                found_words.append((error_word, word_id, unit_name))
                                break
                        if found:
                            break
                    
                    if not found:
                        not_found_words.append(error_word)
                
                f.write(f"\n在Unit 21/22中找到的错词 ({len(found_words)}/{len(alan_error_words)}):\n")
                for word, word_id, unit_name in found_words:
                    f.write(f"单词: {word}, ID: {word_id}, 单元: {unit_name}\n")
                
                f.write(f"\n未在Unit 21/22中找到的错词 ({len(not_found_words)}/{len(alan_error_words)}):\n")
                for word in not_found_words:
                    f.write(f"单词: {word}\n")
                
                # 在整个数据库中查找未匹配的单词
                f.write("\n在整个数据库中查找未匹配的单词:\n")
                for word in not_found_words:
                    cursor.execute("SELECT word_id, spelling, meaning_cn, WordLists.list_name, Books.book_name FROM Words "
                                "JOIN WordLists ON Words.list_id = WordLists.list_id "
                                "JOIN Books ON WordLists.book_id = Books.book_id "
                                "WHERE spelling LIKE ?", (word,))
                    results = cursor.fetchall()
                    if results:
                        f.write(f"单词 '{word}' 在数据库中找到 {len(results)} 条记录:\n")
                        for word_id, db_word, meaning, list_name, book_name in results:
                            f.write(f"  ID: {word_id}, 单词: {db_word}, 释义: {meaning}, 单元: {list_name}, 书: {book_name}\n")
                    else:
                        f.write(f"单词 '{word}' 在数据库中未找到\n")
                
                # 检查ErrorLogs表中Alan在2025-06-25的错词记录
                f.write("\nErrorLogs表中Alan在2025-06-25的错词记录:\n")
                cursor.execute("""
                    SELECT e.error_id, e.student_id, e.word_id, e.error_type, e.student_answer, e.error_date, w.spelling
                    FROM ErrorLogs e
                    LEFT JOIN Words w ON e.word_id = w.word_id
                    WHERE e.student_id = 3 AND e.error_date = '2025-06-25'
                """)
                error_logs = cursor.fetchall()
                
                if error_logs:
                    f.write(f"找到 {len(error_logs)} 条错词记录:\n")
                    for log in error_logs:
                        error_id, student_id, word_id, error_type, student_answer, error_date, word = log
                        f.write(f"错误ID: {error_id}, 单词ID: {word_id}, 错误类型: {error_type}, ")
                        f.write(f"学生答案: {student_answer}, 日期: {error_date}, 单词: {word or '未找到'}\n")
                else:
                    f.write("未找到错词记录\n")
                
                # 检查是否有单词ID不存在于Words表中
                f.write("\n检查ErrorLogs中的单词ID是否存在于Words表中:\n")
                cursor.execute("""
                    SELECT e.error_id, e.word_id
                    FROM ErrorLogs e
                    LEFT JOIN Words w ON e.word_id = w.word_id
                    WHERE e.student_id = 3 AND e.error_date = '2025-06-25' AND w.word_id IS NULL
                """)
                missing_words = cursor.fetchall()
                
                if missing_words:
                    f.write(f"发现 {len(missing_words)} 条记录的单词ID在Words表中不存在:\n")
                    for error_id, word_id in missing_words:
                        f.write(f"错误ID: {error_id}, 单词ID: {word_id}\n")
                else:
                    f.write("所有单词ID都存在于Words表中\n")
        
        f.write("\n报告生成完成\n")
    
    print(f"报告已生成: {report_path}")

except sqlite3.Error as e:
    print(f"数据库错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    if 'conn' in locals():
        conn.close()