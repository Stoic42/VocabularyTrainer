from utils import get_database_connection, get_database_path
import sqlite3
import os

# 数据库文件路径
DATABASE_FILE = get_database_path()

def test_error_review_query():
    """测试错词复习模式的SQL查询"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # 测试参数
        list_id = 1  # 假设测试列表ID为1
        student_id = 1  # 假设测试学生ID为1
        
        print(f"测试错词复习模式: 列表ID={list_id}, 学生ID={student_id}")
        
        # 首先获取该学生在指定列表中的错词ID列表
        error_words_query = '''
        SELECT DISTINCT w.word_id, w.spelling
        FROM Words w
        INNER JOIN ErrorLogs e ON w.word_id = e.word_id
        WHERE w.list_id = ? AND e.student_id = ?
        '''
        
        cursor.execute(error_words_query, (list_id, student_id))
        error_words = cursor.fetchall()
        
        print(f"找到的错词数量: {len(error_words)}")
        if error_words:
            print("错词列表:")
            for word_id, spelling in error_words:
                print(f"  - {spelling} (ID: {word_id})")
        
        # 检查整个列表的单词数量
        total_words_query = "SELECT COUNT(*) FROM Words WHERE list_id = ?"
        cursor.execute(total_words_query, (list_id,))
        total_words = cursor.fetchone()[0]
        print(f"整个列表的单词数量: {total_words}")
        
        # 检查ErrorLogs表中的记录
        error_logs_query = "SELECT COUNT(*) FROM ErrorLogs WHERE student_id = ?"
        cursor.execute(error_logs_query, (student_id,))
        total_errors = cursor.fetchone()[0]
        print(f"该学生的总错误记录数: {total_errors}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")

if __name__ == '__main__':
    test_error_review_query() 