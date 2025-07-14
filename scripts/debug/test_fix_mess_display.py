import os
import sys
from utils import get_database_connection, get_database_path
import sqlite3
import datetime

# 定义数据库路径
db_path = 'd:/Projects/VocabularyTrainer/vocabulary.db'

# 检查数据库是否存在
if not os.path.exists(db_path):
    print(f'错误: 数据库文件 {db_path} 不存在')
    sys.exit(1)

# 连接数据库
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 检查是否存在单词"mess"
print('检查单词"mess"是否存在...')
cursor.execute("SELECT * FROM Words WHERE spelling = 'mess'")
mess_word = cursor.fetchone()

if not mess_word:
    print('单词"mess"不存在于数据库中，将添加测试数据')
    
    # 获取一个有效的list_id
    cursor.execute("SELECT list_id FROM WordLists LIMIT 1")
    list_result = cursor.fetchone()
    
    if not list_result:
        print('错误: 没有找到有效的词汇列表')
        conn.close()
        sys.exit(1)
    
    list_id = list_result['list_id']
    
    # 添加单词"mess"
    cursor.execute("""
    INSERT INTO Words (spelling, meaning_cn, pos, list_id) 
    VALUES (?, ?, ?, ?)
    """, ('mess', '混乱；杂乱；脏乱', 'n.', list_id))
    
    conn.commit()
    print(f'已添加单词"mess"到数据库，list_id: {list_id}')
    
    # 获取新添加的word_id
    cursor.execute("SELECT word_id FROM Words WHERE spelling = 'mess'")
    mess_word = cursor.fetchone()

word_id = mess_word['word_id']
print(f'找到单词"mess"，word_id: {word_id}')

# 检查是否有学生账号
cursor.execute("SELECT * FROM Users WHERE role = 'student' LIMIT 1")
student = cursor.fetchone()

if not student:
    print('没有找到学生账号，将创建测试学生账号')
    
    # 创建测试学生账号
    cursor.execute("""
    INSERT INTO Users (username, password, role) 
    VALUES (?, ?, ?)
    """, ('test_student', 'pbkdf2:sha256:150000$nTkjUihm$a4a85766d5deddbd3e37f326e3b1ec2f9f84a0a0f3d5c09f8e35462b47d25059', 'student'))
    
    conn.commit()
    print('已创建测试学生账号: test_student')
    
    # 获取新创建的学生ID
    cursor.execute("SELECT id FROM Users WHERE username = 'test_student'")
    student = cursor.fetchone()

student_id = student['id']
print(f'找到学生账号，student_id: {student_id}')

# 检查是否存在ErrorLogs表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ErrorLogs'")
if not cursor.fetchone():
    print('ErrorLogs表不存在，将创建表')
    
    cursor.execute("""
    CREATE TABLE ErrorLogs (
        error_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        word_id INTEGER,
        student_answer TEXT,
        error_type TEXT,
        error_date TEXT,
        FOREIGN KEY (student_id) REFERENCES Users(id),
        FOREIGN KEY (word_id) REFERENCES Words(word_id)
    )
    """)
    
    conn.commit()
    print('已创建ErrorLogs表')

# 检查是否已存在"mess"的错误记录
cursor.execute("""
    SELECT * FROM ErrorLogs 
    WHERE student_id = ? AND word_id = ? AND student_answer = 'mass'
""", (student_id, word_id))

existing_error = cursor.fetchone()

if not existing_error:
    print('添加测试错误记录: "mess"拼写为"mass"')
    
    # 添加错误记录
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
    INSERT INTO ErrorLogs (student_id, word_id, student_answer, error_type, error_date)
    VALUES (?, ?, ?, ?, ?)
    """, (student_id, word_id, 'mass', 'spelling', current_date))
    
    # 再添加一条不同日期的错误记录
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
    INSERT INTO ErrorLogs (student_id, word_id, student_answer, error_type, error_date)
    VALUES (?, ?, ?, ?, ?)
    """, (student_id, word_id, 'mass', 'spelling', yesterday))
    
    conn.commit()
    print('已添加测试错误记录')
else:
    print('已存在"mess"的错误记录')

# 验证错误记录
cursor.execute("""
    SELECT e.student_answer, e.error_date, w.spelling, w.meaning_cn, w.pos
    FROM ErrorLogs e
    JOIN Words w ON e.word_id = w.word_id
    WHERE e.student_id = ? AND w.spelling = 'mess'
    ORDER BY e.error_date DESC
""", (student_id,))

errors = cursor.fetchall()
print(f'\n找到 {len(errors)} 条"mess"的错误记录:')

for i, error in enumerate(errors, 1):
    print(f"记录 {i}:")
    print(f"  单词拼写: {error['spelling']}")
    print(f"  中文意思: {error['meaning_cn']}")
    print(f"  词性: {error['pos']}")
    print(f"  学生答案: {error['student_answer']}")
    print(f"  错误日期: {error['error_date']}")
    print()

# 关闭数据库连接
conn.close()

print('\n测试数据准备完成，请访问错误历史页面检查显示效果')
print('访问地址: http://localhost:5000/error-history')
print('登录账号: test_student')
print('登录密码: password')