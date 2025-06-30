import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DATABASE_FILE = 'vocabulary.db'

# 获取数据库连接
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 查询Alan（student_id=3）在2025-06-25的错词记录
def check_alan_0625_errors():
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先确认Alan的用户ID
        cursor.execute("SELECT id, username FROM Users WHERE username = 'Alan'")
        user = cursor.fetchone()
        
        if not user:
            print("未找到用户Alan")
            return
            
        alan_id = user['id']
        print(f"找到用户Alan，ID为: {alan_id}")
        
        # 查询2025-06-25的错词记录
        query = """
        SELECT e.error_id, e.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, 
               e.student_answer, e.error_type, e.error_date,
               wl.book_id, b.book_name, wl.list_name
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = ? AND e.error_date LIKE '2025-06-25%'
        """
        
        cursor.execute(query, (alan_id,))
        errors = cursor.fetchall()
        
        # 生成报告文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"d:/Projects/VocabularyTrainer/alan_0625_error_report_{current_time}.txt"
        
        # 写入报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Alan (ID: {alan_id}) 在 2025-06-25 的错词记录\n")
            f.write("=" * 80 + "\n\n")
            
            if not errors:
                f.write("未找到任何错词记录\n")
            else:
                f.write(f"共找到 {len(errors)} 条错词记录:\n\n")
                
                for i, error in enumerate(errors, 1):
                    f.write(f"{i}. 单词: {error['spelling']}\n")
                    f.write(f"   词性: {error['pos']}\n")
                    f.write(f"   中文释义: {error['meaning_cn']}\n")
                    f.write(f"   学生答案: {error['student_answer']}\n")
                    f.write(f"   错误类型: {error['error_type']}\n")
                    f.write(f"   错误日期: {error['error_date']}\n")
                    f.write(f"   词书: {error['book_name']}\n")
                    f.write(f"   单元: {error['list_name']}\n")
                    f.write("\n")
            
            # 查询数据库中是否有2025-06-25的日期记录
            cursor.execute("SELECT DISTINCT error_date FROM ErrorLogs WHERE error_date LIKE '2025-06-25%'")
            dates = cursor.fetchall()
            
            if dates:
                f.write("\n数据库中存在以下2025-06-25的日期记录:\n")
                for date in dates:
                    f.write(f"- {date['error_date']}\n")
            else:
                f.write("\n数据库中不存在任何2025-06-25的日期记录\n")
                
            # 查询Alan的所有错词记录日期
            cursor.execute("SELECT DISTINCT error_date FROM ErrorLogs WHERE student_id = ? ORDER BY error_date", (alan_id,))
            alan_dates = cursor.fetchall()
            
            if alan_dates:
                f.write("\nAlan的所有错词记录日期:\n")
                for date in alan_dates:
                    f.write(f"- {date['error_date']}\n")
            else:
                f.write("\nAlan没有任何错词记录\n")
        
        print(f"报告已生成: {report_file}")
        
    except Exception as e:
        print(f"查询错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_alan_0625_errors()