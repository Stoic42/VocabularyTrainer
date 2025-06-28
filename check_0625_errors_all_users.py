import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DATABASE_FILE = 'd:/Projects/VocabularyTrainer/vocabulary.db'

# 获取数据库连接
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 查询2025-06-25的所有错词记录及其所属用户
def check_0625_errors_all_users():
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有用户
        cursor.execute("SELECT id, username FROM Users")
        users = cursor.fetchall()
        
        user_dict = {user['id']: user['username'] for user in users}
        print(f"数据库中的用户: {user_dict}")
        
        # 查询2025-06-25的错词记录
        query = """
        SELECT e.error_id, e.student_id, e.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, 
               e.student_answer, e.error_type, e.error_date,
               wl.book_id, b.book_name, wl.list_name
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.error_date LIKE '2025-06-25%'
        """
        
        cursor.execute(query)
        errors = cursor.fetchall()
        
        # 生成报告文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"d:/Projects/VocabularyTrainer/all_users_0625_error_report_{current_time}.txt"
        
        # 写入报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"所有用户在 2025-06-25 的错词记录\n")
            f.write("=" * 80 + "\n\n")
            
            if not errors:
                f.write("未找到任何错词记录\n")
            else:
                # 按用户ID分组错词记录
                user_errors = {}
                for error in errors:
                    student_id = error['student_id']
                    if student_id not in user_errors:
                        user_errors[student_id] = []
                    user_errors[student_id].append(error)
                
                # 为每个用户写入错词记录
                for student_id, user_errors_list in user_errors.items():
                    username = user_dict.get(student_id, f"未知用户(ID: {student_id})")
                    f.write(f"用户: {username} (ID: {student_id})\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"共找到 {len(user_errors_list)} 条错词记录:\n\n")
                    
                    for i, error in enumerate(user_errors_list, 1):
                        f.write(f"{i}. 单词: {error['spelling']}\n")
                        f.write(f"   词性: {error['pos']}\n")
                        f.write(f"   中文释义: {error['meaning_cn']}\n")
                        f.write(f"   学生答案: {error['student_answer']}\n")
                        f.write(f"   错误类型: {error['error_type']}\n")
                        f.write(f"   错误日期: {error['error_date']}\n")
                        f.write(f"   词书: {error['book_name']}\n")
                        f.write(f"   单元: {error['list_name']}\n")
                        f.write("\n")
                    
                    f.write("\n")
            
            # 查询数据库中是否有2025-06-25的日期记录
            cursor.execute("""
            SELECT DISTINCT e.student_id, u.username, COUNT(*) as error_count 
            FROM ErrorLogs e
            JOIN Users u ON e.student_id = u.id
            WHERE e.error_date LIKE '2025-06-25%'
            GROUP BY e.student_id
            """)
            date_stats = cursor.fetchall()
            
            if date_stats:
                f.write("\n2025-06-25的错词记录统计:\n")
                for stat in date_stats:
                    f.write(f"- 用户: {stat['username']} (ID: {stat['student_id']}), 错词数量: {stat['error_count']}\n")
            else:
                f.write("\n数据库中不存在任何2025-06-25的日期记录\n")
        
        print(f"报告已生成: {report_file}")
        
    except Exception as e:
        print(f"查询错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_0625_errors_all_users()