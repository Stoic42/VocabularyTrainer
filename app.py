from flask import Flask, jsonify, request, render_template
import sqlite3
import random

app = Flask(__name__)
DATABASE_FILE = 'vocabulary.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # 这能让我们像字典一样访问列
    return conn

# API 1: 获取问题
@app.route('/api/questions')
def get_questions():
    conn = get_db_connection()
    # 随机抽取10个单词
    words = conn.execute('SELECT word_id, spelling, meaning_cn FROM Words ORDER BY RANDOM() LIMIT 10').fetchall()
    conn.close()
    # 将查询结果转换为字典列表
    return jsonify([dict(word) for word in words])

# API 2: 提交答案并批改
@app.route('/api/submit', methods=['POST'])
def submit_answers():
    data = request.get_json()
    answers = data.get('answers') # 期望格式: [{'word_id': 1, 'answer': 'seperate'}, ...]

    conn = get_db_connection()
    cursor = conn.cursor()

    error_count = 0
    error_details = []

    for item in answers:
        word_id = item.get('word_id')
        student_answer = item.get('answer')

        # 查询正确答案
        correct_word = cursor.execute('SELECT spelling FROM Words WHERE word_id = ?', (word_id,)).fetchone()
        correct_spelling = correct_word['spelling']

        if student_answer.strip().lower() != correct_spelling.lower():
            error_count += 1
            error_details.append({
                'word_id': word_id,
                'correct_spelling': correct_spelling,
                'your_answer': student_answer
            })
            # 将错误记录插入数据库，学生ID我们硬编码为1
            cursor.execute(
                "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, date('now'))",
                (1, word_id, 'spelling_mvp', student_answer)
            )

    conn.commit()
    conn.close()

    return jsonify({
        'message': 'Test submitted!',
        'error_count': error_count,
        'error_details': error_details
    })

# 主页面路由
@app.route('/')
def index():
    # 我们需要一个HTML文件来承载前端页面
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) # debug=True 可以在我们修改代码后自动重启服务