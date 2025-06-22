from flask import Flask, jsonify, request, render_template, send_from_directory
import sqlite3
import random
import logging
from logging.handlers import RotatingFileHandler
import os

# --- 应用设置 ---
app = Flask(__name__, 
           static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'),
           static_url_path='/assets')
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
# 在app.py中找到这个函数并替换它

@app.route('/api/questions')
def get_questions():
    # 从URL参数中获取list_id，如果没提供，默认为1
    list_id = request.args.get('list_id', default=1, type=int)
    # 新增：从URL获取单词数量, 默认为'10'
    count_str = request.args.get('count', default='10', type=str)
    
    conn = get_db_connection()
    
    # 基础SQL查询
    sql_query = 'SELECT word_id, spelling, meaning_cn, pos, audio_path_uk, audio_path_us FROM Words WHERE list_id = ? ORDER BY RANDOM()'
    params = (list_id,)

    # 只有当数量不是'all'时，我们才加上LIMIT子句
    if count_str.lower() != 'all':
        try:
            # 确保count可以被转换为整数
            limit_count = int(count_str)
            sql_query += ' LIMIT ?'
            params += (limit_count,) # 将数量添加到参数元组中
        except ValueError:
            # 如果count不是一个有效的数字，就使用默认值10，并记录一个警告
            app.logger.warning(f"无效的count参数: '{count_str}', 将使用默认值10。")
            sql_query += ' LIMIT ?'
            params += (10,)

    words = conn.execute(sql_query, params).fetchall()
    conn.close()
    
    # --- 后续的数据处理逻辑保持不变 ---
    word_list = []
    for word in words:
        word_dict = dict(word)
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
                # 将错误记录到ErrorLogs表
                try:
                    cursor.execute(
                        "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, date('now'))",
                        (1, word_id, 'spelling_mvp', student_answer)
                    )
                    app.logger.info(f"记录错误: 单词ID={word_id}, 学生答案={student_answer}")
                except sqlite3.Error as e:
                    app.logger.error(f"记录错误到ErrorLogs表失败: {e}")
                    # 如果表不存在，尝试创建它
                    if 'no such table' in str(e).lower():
                        try:
                            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS ErrorLogs (
                                error_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                student_id INTEGER,
                                word_id INTEGER,
                                error_type TEXT,
                                student_answer TEXT,
                                error_date TEXT,
                                FOREIGN KEY (word_id) REFERENCES Words(word_id)
                            )
                            ''')
                            conn.commit()
                            app.logger.info("ErrorLogs表已创建")
                            # 重新尝试插入
                            cursor.execute(
                                "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, date('now'))",
                                (1, word_id, 'spelling_mvp', student_answer)
                            )
                        except sqlite3.Error as e2:
                            app.logger.error(f"创建ErrorLogs表并插入数据失败: {e2}")

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
        
        # 确保返回32个列表选项
        # 如果数据库中的列表数量不足32个，则补充剩余的列表选项
        existing_list_ids = {item['id'] for item in list_ids}
        for i in range(1, 33):
            if i not in existing_list_ids:
                list_ids.append({'id': i, 'name': f'List {i}'})
        
        # 按list_id排序
        list_ids.sort(key=lambda x: x['id'])
        
        return jsonify(list_ids)
    except sqlite3.Error as e:
        app.logger.error(f"获取单词列表时出错: {e}")
        return jsonify({'error': '获取单词列表失败'}), 500
    finally:
        if conn:
            conn.close()

# --- 页面路由 ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error-history')
def error_history():
    return render_template('error_history.html')

# --- 错误历史记录API ---
@app.route('/api/error-history')
def get_error_history():
    """获取用户的错误历史记录"""
    try:
        # 获取查询参数
        student_id = request.args.get('student_id', default=1, type=int)  # 默认为学生ID 1
        limit = request.args.get('limit', default=50, type=int)  # 默认最多返回50条记录
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询错误记录，并关联单词信息
        query = """
        SELECT e.error_id, e.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, 
               e.student_answer, e.error_type, e.error_date,
               (SELECT COUNT(*) FROM ErrorLogs WHERE word_id = e.word_id AND student_id = e.student_id) as error_count
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        WHERE e.student_id = ?
        ORDER BY e.error_date DESC
        LIMIT ?
        """
        
        cursor.execute(query, (student_id, limit))
        errors = cursor.fetchall()
        
        # 查询错误统计信息
        stats_query = """
        SELECT w.list_id, COUNT(*) as error_count,
               (SELECT COUNT(DISTINCT word_id) FROM ErrorLogs WHERE student_id = ? AND word_id IN 
                (SELECT word_id FROM Words WHERE list_id = w.list_id)) as unique_words_count
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        WHERE e.student_id = ?
        GROUP BY w.list_id
        ORDER BY w.list_id
        """
        
        cursor.execute(stats_query, (student_id, student_id))
        stats = cursor.fetchall()
        
        # 查询每个单词的错误历史
        word_history_query = """
        SELECT w.word_id, w.spelling, w.list_id,
               COUNT(*) as total_errors,
               GROUP_CONCAT(e.student_answer, ', ') as wrong_answers,
               GROUP_CONCAT(e.error_date, ', ') as error_dates
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        WHERE e.student_id = ?
        GROUP BY w.word_id
        ORDER BY total_errors DESC
        LIMIT 20
        """
        
        cursor.execute(word_history_query, (student_id,))
        word_history = cursor.fetchall()
        
        # 转换为JSON格式
        error_list = [dict(error) for error in errors]
        stats_list = [dict(stat) for stat in stats]
        word_history_list = [dict(item) for item in word_history]
        
        # 计算总体正确率（假设每个单词测试一次）
        total_tested_query = "SELECT COUNT(DISTINCT word_id) FROM ErrorLogs WHERE student_id = ?"
        cursor.execute(total_tested_query, (student_id,))
        total_tested = cursor.fetchone()[0]
        
        # 假设我们有一个记录总测试单词数的方法，这里简化处理
        # 实际应用中可能需要一个单独的表来记录每次测试的所有单词
        accuracy_rate = 0
        if total_tested > 0:
            # 这里的计算是简化的，实际应用中需要更准确的数据
            # 假设每个单词只测试一次，错误的单词数就是total_tested
            accuracy_rate = round((1 - total_tested / 100) * 100, 2)  # 假设总共测试了100个单词
        
        conn.close()
        
        return jsonify({
            'errors': error_list,
            'stats': stats_list,
            'word_history': word_history_list,
            'total_tested': total_tested,
            'accuracy_rate': accuracy_rate
        })
        
    except sqlite3.Error as e:
        app.logger.error(f"获取错误历史记录时出错: {e}")
        return jsonify({'error': '获取错误历史记录失败'}), 500

# --- 启动命令 ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)