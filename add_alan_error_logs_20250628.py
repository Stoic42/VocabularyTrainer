import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DATABASE_FILE = 'vocabulary.db'

def get_db_connection():
    """连接到数据库"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def add_alan_error_logs():
    """添加Alan在2025-06-28的错误记录"""
    try:
        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Alan的student_id
        student_id = 3
        
        # 错误类型
        error_type = 'spelling_mvp'
        
        # 错误日期
        error_date = '2025-06-28'
        
        # 第一轮：复习【6月25日】错词时产生的新错误 (7条)
        first_round_errors = [
            {'word': 'seal', 'word_id': 17994, 'student_answer': ''},  # 未填写
            {'word': 'convenient', 'word_id': 18001, 'student_answer': 'convient'},
            {'word': 'Atlantic', 'word_id': 18055, 'student_answer': ''},  # 未填写
            {'word': 'escalator', 'word_id': 18078, 'student_answer': ''},  # 未填写
            {'word': 'nature', 'word_id': 18098, 'student_answer': 'nat'},
            {'word': 'age', 'word_id': 18070, 'student_answer': 'elder'},
            {'word': 'enemy', 'word_id': 18096, 'student_answer': 'enermy'}
        ]
        
        # 第二轮：复习【6月27日】错词时产生的新错误 (6条)
        second_round_errors = [
            {'word': 'unimportant', 'word_id': 0, 'student_answer': 'unimporant'},  # 需要查询word_id
            {'word': 'agent', 'word_id': 0, 'student_answer': 'angint'},  # 需要查询word_id
            {'word': 'gallery', 'word_id': 0, 'student_answer': 'galary'},  # 需要查询word_id
            {'word': 'pleasant', 'word_id': 0, 'student_answer': 'pleasent'},  # 需要查询word_id
            {'word': 'original', 'word_id': 0, 'student_answer': ''},  # 需要查询word_id，未填写
            {'word': 'discussion', 'word_id': 0, 'student_answer': 'discusion'}  # 需要查询word_id
        ]
        
        # 第三轮：强化考核阶段产生的新错误 (4条)
        third_round_errors = [
            {'word': 'original', 'word_id': 0, 'student_answer': ''},  # 需要查询word_id，未填写
            {'word': 'convenient', 'word_id': 18001, 'student_answer': 'convinient'},
            {'word': 'escalator', 'word_id': 18078, 'student_answer': ''},  # 未填写
            {'word': 'nature', 'word_id': 18098, 'student_answer': 'natuer'}
        ]
        
        # 查询word_id为0的单词的正确word_id
        for error_list in [second_round_errors, third_round_errors]:
            for error in error_list:
                if error['word_id'] == 0:
                    # 查询单词的word_id
                    cursor.execute(
                        "SELECT word_id FROM Words WHERE spelling = ?", 
                        (error['word'],)
                    )
                    result = cursor.fetchone()
                    if result:
                        error['word_id'] = result['word_id']
                    else:
                        print(f"警告: 未找到单词 '{error['word']}' 的ID")
        
        # 合并所有错误记录
        all_errors = first_round_errors + second_round_errors + third_round_errors
        
        # 插入错误记录
        for error in all_errors:
            if error['word_id'] > 0:  # 只插入有有效word_id的记录
                try:
                    cursor.execute(
                        "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, ?)",
                        (student_id, error['word_id'], error_type, error['student_answer'], error_date)
                    )
                    print(f"成功添加错误记录: 单词={error['word']}, ID={error['word_id']}, 学生答案={error['student_answer']}")
                except sqlite3.Error as e:
                    print(f"插入错误记录失败: {e}, 单词={error['word']}, ID={error['word_id']}")
        
        # 提交事务
        conn.commit()
        print(f"成功添加Alan在{error_date}的错误记录")
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_alan_error_logs()