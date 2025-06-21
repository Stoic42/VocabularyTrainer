from flask import Flask, jsonify, request, render_template, send_from_directory
import sqlite3
import random
import logging
from logging.handlers import RotatingFileHandler
import os

# --- 应用设置 ---
app = Flask(__name__)
# 将静态文件目录设置为项目根目录下的 'assets' 文件夹
app.static_folder = 'assets' 
DATABASE_FILE = 'vocabulary.db'
# 我们将所有词库资源（音频、txt）都统一放在 'wordlists' 文件夹下进行管理
WORDLISTS_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wordlists')

# --- 日志配置 (您的优秀代码，我们保留) ---
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

setup_logger(app)

# --- 数据库连接 ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- 核心API路由 ---

# 媒体文件服务路由 (您的优秀代码，我们保留)
@app.route('/wordlists/<path:subpath>')
def serve_wordlist_files(subpath):
    try:
        return send_from_directory(WORDLISTS_BASE_DIR, subpath)
    except Exception as e:
        app.logger.error(f'发送媒体文件时出错: {subpath}, 错误: {str(e)}')
        return {'error': '服务器内部错误'}, 500

# API 1: 获取问题 (已升级)
@app.route('/api/questions')
def get_questions():
    # 从URL参数中获取list_id，如果前端没提供，就默认为1
    list_id_str = request.args.get('list_id', default='1', type=str)
    
    conn = get_db_connection()
    # 在SQL查询中加入 WHERE 子句，根据list_id筛选
    words = conn.execute(
        'SELECT word_id, spelling, meaning_cn, pos, audio_path_uk, audio_path_us FROM Words WHERE list_id = ? ORDER BY RANDOM() LIMIT 10',
        (list_id_str,)
    ).fetchall()
    conn.close()
    
    word_list = []
    for word in words:
        word_dict = dict(word)
        # --- 修复了URL路径问题 ---
        # 生成正确的、从网站根目录开始的URL
        if word_dict['audio_path_uk']:
            word_dict['audio_path_uk'] = f"/wordlists/junior_high/Media/{word_dict['audio_path_uk']}"
        if word_dict['audio_path_us']:
            word_dict['audio_path_us'] = f"/wordlists/junior_high/Media/{word_dict['audio_path_us']}"
        word_list.append(word_dict)
        
    return jsonify(word_list)

# API 2: 提交答案并批改 (您的优秀代码，我们保留)
@app.route('/api/submit', methods=['POST'])
def submit_answers():
    # ... 您的 submit_answers 函数逻辑非常完美，无需改动 ...
    data = request.get_json()
    answers = data.get('answers', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()

    error_details = []
    for item in answers:
        word_id = item.get('word_id')
        student_answer = item.get('answer', '')

        correct_word = cursor.execute('SELECT spelling FROM Words WHERE word_id = ?', (word_id,)).fetchone()
        if correct_word:
            correct_spelling = correct_word['spelling']
            valid_spellings = [s.strip().lower() for s in correct_spelling.split('/')]
            if student_answer.strip().lower() not in valid_spellings:
                error_details.append({
                    'word_id': word_id,
                    'correct_spelling': correct_spelling,
                    'your_answer': student_answer
                })
                cursor.execute(
                    "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, date('now'))",
                    (1, word_id, 'spelling_mvp', student_answer)
                )

    conn.commit()
    conn.close()

    return jsonify({
        'message': 'Test submitted!',
        'error_count': len(error_details),
        'error_details': error_details
    })

# --- API路由：获取单词列表 ---
@app.route('/api/lists')
def get_lists():
    """获取所有可用的单词列表"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # 查询数据库中所有不同的 list_id
        cursor.execute("SELECT DISTINCT list_id FROM Words ORDER BY list_id")
        lists = cursor.fetchall()
        
        # 转换为列表格式
        list_ids = [{'id': list_id[0], 'name': f'List {list_id[0]}'} for list_id in lists]
        
        return jsonify(list_ids)
    except sqlite3.Error as e:
        app.logger.error(f"获取单词列表时出错: {e}")
        return jsonify({'error': '获取单词列表失败'}), 500
    finally:
        if conn:
            conn.close()

# --- 主页面路由 ---
@app.route('/')
def index():
    return render_template('index.html')

# --- 启动命令 ---
if __name__ == '__main__':
    app.run(debug=True)