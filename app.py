from flask import Flask, jsonify, request, render_template
import sqlite3
import random
import logging
from logging.handlers import RotatingFileHandler
from flask import send_from_directory
import os

# 配置日志
def setup_logger(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')

app = Flask(__name__, static_folder='assets')
app.config['AUDIO_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wordlists/junior_high/Media')
DATABASE_FILE = 'vocabulary.db'

# 初始化日志
setup_logger(app)

@app.route('/wordlists/junior_high/Media/<path:filename>')
def serve_audio(filename):
    try:
        # 检查文件是否存在
        file_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
        if not os.path.exists(file_path):
            app.logger.error(f'音频文件不存在: {file_path}')
            return {'error': '音频文件不存在'}, 404

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            app.logger.error(f'音频文件为空: {file_path}')
            return {'error': '音频文件损坏'}, 500

        response = send_from_directory(app.config['AUDIO_FOLDER'], filename)
        response.headers.update({
            'Access-Control-Allow-Origin': '*',  # 允许跨域访问
            'Access-Control-Allow-Methods': 'GET, OPTIONS',  # 允许的HTTP方法
            'Access-Control-Allow-Headers': 'Content-Type',  # 允许的请求头
            'Cache-Control': 'public, max-age=31536000',  # 启用缓存，有效期1年
            'Content-Type': 'audio/mpeg',  # 确保正确的Content-Type
            'Content-Length': str(file_size)  # 添加文件大小信息
        })
        app.logger.info(f'成功发送音频文件: {filename}, 大小: {file_size} bytes')
        return response

    except Exception as e:
        app.logger.error(f'发送音频文件时出错: {filename}, 错误: {str(e)}')
        return {'error': '服务器内部错误'}, 500

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # 这能让我们像字典一样访问列
    return conn

# API 1: 获取问题
@app.route('/api/questions')
def get_questions():
    conn = get_db_connection()
    # 随机抽取10个单词
    words = conn.execute('SELECT word_id, spelling, meaning_cn, pos, audio_path_uk, audio_path_us FROM Words ORDER BY RANDOM() LIMIT 10').fetchall()
    conn.close()
    # 将查询结果转换为字典列表，并添加音频文件的完整路径
    word_list = []
    for word in words:
        word_dict = dict(word)
        # 这是修复后的、正确的代码
        if word_dict['audio_path_uk']:
            word_dict['audio_path_uk'] = f"/wordlists/junior_high/Media/{word_dict['audio_path_uk']}"
        if word_dict['audio_path_us']:
            word_dict['audio_path_us'] = f"/wordlists/junior_high/Media/{word_dict['audio_path_us']}"
        word_list.append(word_dict)
    return jsonify(word_list)

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

        # --- 原来的逻辑 ---
        # if student_answer.strip().lower() != correct_spelling.lower():
        #     # ... 答错了 ...

        # --- 请修改为下面的新逻辑 ---
        valid_spellings = [s.strip().lower() for s in correct_spelling.split('/')]
        if student_answer.strip().lower() not in valid_spellings:
            # ... 答错了 ...
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