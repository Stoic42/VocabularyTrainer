from flask import Flask, jsonify, request, render_template, send_from_directory, session
import sqlite3
import random
import logging
from logging.handlers import RotatingFileHandler
import os
import hashlib
# 新增这一行，导入 werkzeug 的安全模块，用于密码加密
from werkzeug.security import generate_password_hash, check_password_hash
# 导入gTTS库，用于文本到语音转换
from gtts import gTTS

# --- 应用设置 ---
app = Flask(__name__, 
           static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'),
           static_url_path='/assets')
app.secret_key = 'your-super-secret-key-for-mvp' # MVP阶段随便写一个即可
DATABASE_FILE = 'vocabulary.db'
# 我们将所有词库资源（音频、txt）都统一放在 'wordlists' 文件夹下进行管理
WORDLISTS_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wordlists')
# TTS音频缓存目录
TTS_CACHE_DIR = os.path.join(WORDLISTS_BASE_DIR, 'tts_cache')
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

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

# TTS文本预处理函数
def preprocess_text_for_tts(text):
    """预处理文本以优化TTS效果"""
    # 处理特殊情况
    text = text.replace('a/an', 'a or an')
    text = text.replace('/', ' or ')
    # 可以添加更多替换规则
    return text

# TTS API端点
@app.route('/api/tts/<word>')
def get_tts_audio(word):
    """生成单词的TTS音频并返回"""
    try:
        # 文本预处理
        processed_word = preprocess_text_for_tts(word)
        
        # 生成文件名（使用哈希避免文件名问题）
        filename = hashlib.md5(processed_word.encode()).hexdigest() + '.mp3'
        filepath = os.path.join(TTS_CACHE_DIR, filename)
        
        # 如果文件不存在，则生成
        if not os.path.exists(filepath):
            tts = gTTS(text=processed_word, lang='en', slow=False)
            tts.save(filepath)
            app.logger.info(f"已生成TTS音频: {word} -> {filepath}")
        
        return send_from_directory(TTS_CACHE_DIR, filename)
    except Exception as e:
        app.logger.error(f"生成TTS音频失败: {word}, 错误: {str(e)}")
        return {'error': '生成TTS音频失败'}, 500

# API 1: 获取问题 (已升级)
# 在app.py中找到这个函数并替换它

@app.route('/api/questions')
def get_questions():
    # 从URL参数中获取list_id，如果没提供，默认为1
    list_id = request.args.get('list_id', default=1, type=int)
    # 新增：从URL获取单词数量, 默认为'10'
    count_str = request.args.get('count', default='10', type=str)
    # 新增：学习模式参数，默认为'standard'
    study_mode = request.args.get('mode', default='standard', type=str)
    
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
    
    # --- 数据处理逻辑，根据学习模式决定是否包含音频URL ---
    word_list = []
    for word in words:
        word_dict = dict(word)
        
        # 根据学习模式决定是否包含音频URL
        if study_mode.lower() != 'dictation':
            # 标准模式：包含音频URL
            if word_dict['audio_path_uk']:
                word_dict['audio_path_uk'] = f"/wordlists/junior_high/Media/{word_dict['audio_path_uk']}"
            else:
                # 如果没有音频文件，提供TTS URL
                word_dict['audio_path_uk'] = f"/api/tts/{word_dict['spelling']}"
                
            if word_dict['audio_path_us']:
                word_dict['audio_path_us'] = f"/wordlists/junior_high/Media/{word_dict['audio_path_us']}"
            else:
                # 如果没有音频文件，提供TTS URL
                word_dict['audio_path_us'] = f"/api/tts/{word_dict['spelling']}"
        else:
            # 默写模式：不提供音频
            word_dict['audio_path_uk'] = ""
            word_dict['audio_path_us'] = ""
            
        word_list.append(word_dict)
        
    return jsonify(word_list)

# API 2: 提交答案并批改
@app.route('/api/submit', methods=['POST'])
def submit_answers():
    data = request.get_json()
    answers = data.get('answers', [])
    
    # 获取当前登录用户ID，如果未登录则使用默认值-1（表示游客）
    student_id = session.get('user_id', -1)
    
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
                # 将错误记录到ErrorLogs表，使用当前用户ID
                try:
                    cursor.execute(
                        "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, date('now'))",
                        (student_id, word_id, 'spelling_mvp', student_answer)
                    )
                    app.logger.info(f"记录错误: 用户ID={student_id}, 单词ID={word_id}, 学生答案={student_answer}")
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
                                (student_id, word_id, 'spelling_mvp', student_answer)
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

# --- API路由：获取词书列表 ---
@app.route('/api/books')
def get_books():
    """获取所有可用的词书列表"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # 查询数据库中所有词书
        cursor.execute("SELECT book_id, book_name FROM Books ORDER BY book_id")
        books = cursor.fetchall()
        
        # 转换为列表格式
        book_list = [{'id': book[0], 'name': book[1]} for book in books]
        
        return jsonify(book_list)
    except sqlite3.Error as e:
        app.logger.error(f"获取词书列表时出错: {e}")
        return jsonify({'error': '获取词书列表失败'}), 500
    finally:
        if conn:
            conn.close()

# --- API路由：获取单词列表 ---
@app.route('/api/lists')
def get_lists():
    """获取可用的单词列表，可以按book_id筛选"""
    try:
        book_id = request.args.get('book_id', type=int)
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        if book_id:
            # 如果提供了book_id，查询特定词书下的单元
            cursor.execute(
                "SELECT list_id, list_name FROM WordLists WHERE book_id = ? ORDER BY list_id", 
                (book_id,)
            )
            lists = cursor.fetchall()
            list_ids = [{'id': list_item[0], 'name': list_item[1]} for list_item in lists]
        else:
            # 兼容旧版本，如果没有提供book_id，返回所有单元
            cursor.execute("SELECT list_id, list_name FROM WordLists ORDER BY list_id")
            lists = cursor.fetchall()
            
            if lists:
                list_ids = [{'id': list_item[0], 'name': list_item[1]} for list_item in lists]
            else:
                # 如果WordLists表为空，尝试从Words表获取list_id（兼容旧数据）
                cursor.execute("SELECT DISTINCT list_id FROM Words ORDER BY list_id")
                old_lists = cursor.fetchall()
                list_ids = [{'id': list_id[0], 'name': f'List {list_id[0]}'} for list_id in old_lists]
                
                # 确保返回32个列表选项（兼容旧逻辑）
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
        # 获取当前登录用户ID，如果未登录则使用默认值-1（表示游客）
        student_id = session.get('user_id', -1)
        # 如果用户未登录，返回错误信息
        if student_id == -1:
            return jsonify({'error': '请先登录后查看错误历史记录'}), 401
            
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

# --- 新增：用户认证API ---

@app.route('/api/register', methods=['POST'])
def register():
    """处理用户注册"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查用户名是否已存在
    user = cursor.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
    if user:
        conn.close()
        return jsonify({'error': '用户名已存在'}), 409 # 409代表冲突

    # 将密码加密后存储
    password_hash = generate_password_hash(password)

    cursor.execute('INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)', 
                   (username, password_hash, 'student')) # 默认为学生
    conn.commit()
    conn.close()

    return jsonify({'message': '用户注册成功'}), 201 # 201代表创建成功

@app.route('/api/login', methods=['POST'])
def login():
    """处理用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        # 密码正确，将用户信息存入 session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({'message': '登录成功', 'user': {'username': user['username'], 'role': user['role']}}), 200

    return jsonify({'error': '用户名或密码错误'}), 401 # 401代表未授权

# --- 启动命令 ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)