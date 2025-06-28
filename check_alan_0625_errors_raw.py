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

# 查询Alan（student_id=3）在2025-06-25的原始错词记录
def check_alan_0625_errors_raw():
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
        
        # 查询2025-06-25的原始错词记录，不做任何JOIN
        query = """
        SELECT * FROM ErrorLogs
        WHERE student_id = ? AND error_date LIKE '2025-06-25%'
        ORDER BY error_date
        """
        
        cursor.execute(query, (alan_id,))
        errors = cursor.fetchall()
        
        # 生成报告文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"d:/Projects/VocabularyTrainer/alan_0625_error_raw_{current_time}.txt"
        
        # 写入报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Alan (ID: {alan_id}) 在 2025-06-25 的原始错词记录\n")
            f.write("=" * 80 + "\n\n")
            
            if not errors:
                f.write("未找到任何错词记录\n")
            else:
                f.write(f"共找到 {len(errors)} 条原始错词记录:\n\n")
                
                # 获取所有列名
                columns = [column[0] for column in cursor.description]
                f.write(f"列名: {', '.join(columns)}\n\n")
                
                # 统计word_id的分布
                word_id_counts = {}
                for error in errors:
                    word_id = error['word_id']
                    if word_id not in word_id_counts:
                        word_id_counts[word_id] = 0
                    word_id_counts[word_id] += 1
                
                f.write("word_id分布统计:\n")
                for word_id, count in word_id_counts.items():
                    f.write(f"word_id: {word_id}, 出现次数: {count}\n")
                f.write("\n")
                
                # 输出每条记录的详细信息
                for i, error in enumerate(errors, 1):
                    f.write(f"记录 {i}:\n")
                    for column in columns:
                        f.write(f"  {column}: {error[column]}\n")
                    f.write("\n")
            
            # 查询错误历史API中使用的查询语句结果
            f.write("\n模拟错误历史API查询结果 (使用GROUP BY):\n")
            api_query = """
            SELECT e.error_id, e.word_id, e.student_id, e.error_date,
                   (SELECT COUNT(*) FROM ErrorLogs WHERE word_id = e.word_id AND student_id = e.student_id) as error_count
            FROM ErrorLogs e
            WHERE e.student_id = ? AND e.error_date LIKE '2025-06-25%'
            GROUP BY e.word_id, e.error_date
            """
            
            cursor.execute(api_query, (alan_id,))
            api_results = cursor.fetchall()
            
            if api_results:
                f.write(f"API查询返回 {len(api_results)} 条记录\n")
                for i, result in enumerate(api_results, 1):
                    f.write(f"{i}. word_id: {result['word_id']}, 日期: {result['error_date']}, 错误次数: {result['error_count']}\n")
            else:
                f.write("API查询未返回任何记录\n")
                
            # 检查错词记录中的word_id是否存在于Words表中
            f.write("\n检查错词记录中的word_id是否存在于Words表中:\n")
            for word_id in word_id_counts.keys():
                cursor.execute("SELECT word_id, spelling FROM Words WHERE word_id = ?", (word_id,))
                word = cursor.fetchone()
                if word:
                    f.write(f"word_id: {word_id}, 单词: {word['spelling']} - 存在于Words表中\n")
                else:
                    f.write(f"word_id: {word_id} - 不存在于Words表中\n")
        
        print(f"报告已生成: {report_file}")
        
    except Exception as e:
        print(f"查询错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_alan_0625_errors_raw()