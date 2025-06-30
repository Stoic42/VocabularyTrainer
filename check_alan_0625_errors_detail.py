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
def check_alan_0625_errors_detail():
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
        
        # 查询2025-06-25的错词记录，不使用GROUP BY，获取所有记录
        query = """
        SELECT e.error_id, e.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, 
               e.student_answer, e.error_type, e.error_date,
               wl.book_id, b.book_name, wl.list_name
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = ? AND e.error_date LIKE '2025-06-25%'
        ORDER BY e.error_date
        """
        
        cursor.execute(query, (alan_id,))
        errors = cursor.fetchall()
        
        # 生成报告文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"d:/Projects/VocabularyTrainer/alan_0625_error_detail_{current_time}.txt"
        
        # 写入报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Alan (ID: {alan_id}) 在 2025-06-25 的详细错词记录\n")
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
            
            # 查询数据库中Alan在2025-06-25的错词记录数量
            cursor.execute("""
            SELECT COUNT(*) as error_count 
            FROM ErrorLogs 
            WHERE student_id = ? AND error_date LIKE '2025-06-25%'
            """, (alan_id,))
            count = cursor.fetchone()['error_count']
            f.write(f"\nAlan在2025-06-25的错词记录总数: {count}\n")
            
            # 查询Alan的所有错词记录日期及数量
            cursor.execute("""
            SELECT error_date, COUNT(*) as count 
            FROM ErrorLogs 
            WHERE student_id = ? 
            GROUP BY error_date 
            ORDER BY error_date
            """, (alan_id,))
            date_counts = cursor.fetchall()
            
            if date_counts:
                f.write("\nAlan的所有错词记录日期及数量:\n")
                for date_count in date_counts:
                    f.write(f"- {date_count['error_date']}: {date_count['count']} 条记录\n")
            else:
                f.write("\nAlan没有任何错词记录\n")
                
            # 查询错误历史API中使用的查询语句结果
            f.write("\n模拟错误历史API查询结果 (使用GROUP BY):\n")
            api_query = """
            SELECT e.error_id, e.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, 
                   e.student_answer, e.error_type, e.error_date,
                   (SELECT COUNT(*) FROM ErrorLogs WHERE word_id = e.word_id AND student_id = e.student_id) as error_count,
                   wl.book_id, b.book_name, wl.list_name
            FROM ErrorLogs e
            JOIN Words w ON e.word_id = w.word_id
            LEFT JOIN WordLists wl ON w.list_id = wl.list_id
            LEFT JOIN Books b ON wl.book_id = b.book_id
            WHERE e.student_id = ? AND e.error_date LIKE '2025-06-25%'
            GROUP BY e.word_id, e.error_date
            """
            
            cursor.execute(api_query, (alan_id,))
            api_results = cursor.fetchall()
            
            if api_results:
                f.write(f"API查询返回 {len(api_results)} 条记录\n")
                for i, result in enumerate(api_results, 1):
                    f.write(f"{i}. 单词: {result['spelling']}, 日期: {result['error_date']}\n")
            else:
                f.write("API查询未返回任何记录\n")
        
        print(f"报告已生成: {report_file}")
        
    except Exception as e:
        print(f"查询错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_alan_0625_errors_detail()