# ======================================================================
# 烛梦单词训练营 - 主程序
# ======================================================================
# 重要说明：这是主程序，所有开发和修改应优先在此进行，而不是在LumiCamp_for_Alan中
# 详细开发指南请参考：DEVELOPMENT_GUIDE.md
# ======================================================================

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
# 导入Flask
from flask import Flask, request, jsonify, render_template, session, send_from_directory

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import datetime
import os
# 导入管理员路由蓝图
from admin_routes import admin_bp

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

# 注册管理员路由蓝图
app.register_blueprint(admin_bp)

# --- 日志配置 (您的优秀代码，我们保留) ---
def setup_logger(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 清除现有的处理器以避免重复
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    try:
        # 使用更安全的日志配置
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=5, delay=True)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    except (PermissionError, OSError) as e:
        # 如果无法访问日志文件，使用带时间戳的新文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            file_handler = RotatingFileHandler(f'logs/app_{timestamp}.log', maxBytes=10240, backupCount=5, delay=True)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            print(f"警告: 无法访问原始日志文件。已创建新的日志文件: app_{timestamp}.log")
        except Exception as fallback_error:
            # 如果连备用日志文件也无法创建，使用控制台日志
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s'
            ))
            console_handler.setLevel(logging.INFO)
            app.logger.addHandler(console_handler)
            print(f"警告: 无法创建任何日志文件，将使用控制台日志。错误: {fallback_error}")
    
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
    study_mode = request.args.get('study_mode', default='standard', type=str)
    
    # 获取当前登录用户ID，如果未登录则使用默认值-1（表示游客）
    student_id = session.get('user_id', -1)
    
    conn = get_db_connection()
    
    # 根据学习模式选择不同的查询策略
    if study_mode.lower() == 'error_review':
        # 错误复习模式：只获取该学生在指定列表中犯过错误的单词
        sql_query = '''
        SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.audio_path_uk, w.audio_path_us,
               w.derivatives, w.root_etymology, w.mnemonic, w.comparison, w.collocation,
               w.exam_sentence, w.exam_year_source, w.exam_options, w.exam_explanation, w.tips,
               w.list_id,
               (SELECT COUNT(*) FROM ErrorLogs WHERE word_id = w.word_id AND student_id = ?) as error_count,
               (SELECT MAX(error_date) FROM ErrorLogs WHERE word_id = w.word_id AND student_id = ?) as last_error_date,
               wl.list_name, b.book_name
        FROM Words w
        INNER JOIN ErrorLogs e ON w.word_id = e.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE w.list_id = ? AND e.student_id = ?
        GROUP BY w.word_id
        ORDER BY error_count DESC, last_error_date DESC
        '''
        params = (student_id, student_id, list_id, student_id)
    else:
        # 标准模式和默写模式：随机获取单词
        sql_query = '''SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.audio_path_uk, w.audio_path_us, 
                   w.derivatives, w.root_etymology, w.mnemonic, w.comparison, w.collocation, 
                   w.exam_sentence, w.exam_year_source, w.exam_options, w.exam_explanation, w.tips,
                   b.book_name
                   FROM Words w
                   LEFT JOIN WordLists wl ON w.list_id = wl.list_id
                   LEFT JOIN Books b ON wl.book_id = b.book_id
                   WHERE w.list_id = ? ORDER BY RANDOM()'''
        params = (list_id,)

    # 对于错词复习模式，总是获取全部错词，不应用LIMIT
    # 对于其他模式，只有当数量不是'all'时才加上LIMIT子句
    if study_mode.lower() != 'error_review' and count_str.lower() != 'all':
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

    # 添加调试日志
    if study_mode.lower() == 'error_review':
        app.logger.info(f"错词复习模式SQL: {sql_query}")
        app.logger.info(f"错词复习模式参数: {params}")
    
    words = conn.execute(sql_query, params).fetchall()
    conn.close()
    
    # 添加调试日志
    if study_mode.lower() == 'error_review':
        app.logger.info(f"错词复习模式: 列表ID={list_id}, 学生ID={student_id}, 获取到{len(words)}个错词")
        if words:
            app.logger.info(f"错词示例: {[word['spelling'] for word in words[:3]]}")
        else:
            app.logger.info(f"错词复习模式: 列表ID={list_id}, 学生ID={student_id}, 没有错词")
    
    # --- 数据处理逻辑，根据学习模式决定是否包含音频URL和详情字段 ---
    word_list = []
    for word in words:
        word_dict = dict(word)
        
        # 处理详情字段，确保它们不是None
        detail_fields = ['derivatives', 'root_etymology', 'mnemonic', 'comparison', 
                         'collocation', 'exam_sentence', 'exam_year_source', 
                         'exam_options', 'exam_explanation', 'tips']
        
        for field in detail_fields:
            if field in word_dict and word_dict[field] is None:
                word_dict[field] = ""
        
        # 处理错误复习模式特有的字段
        if study_mode.lower() == 'error_review':
            # 确保错误统计字段存在
            if 'error_count' not in word_dict:
                word_dict['error_count'] = 0
            if 'last_error_date' not in word_dict:
                word_dict['last_error_date'] = ""
            if 'list_name' not in word_dict:
                word_dict['list_name'] = ""
            if 'book_name' not in word_dict:
                word_dict['book_name'] = ""
        else:
            # 标准模式和默写模式：确保book_name字段存在
            if 'book_name' not in word_dict:
                word_dict['book_name'] = ""
        
        # 根据学习模式决定是否包含音频URL
        if study_mode.lower() != 'dictation':
            # 标准模式和错词复习模式：包含音频URL
            # 根据词书类型选择正确的媒体路径
            book_name = word_dict.get('book_name', '')
            if '高中' in book_name:
                media_prefix = "/wordlists/senior_high/media"
            else:
                media_prefix = "/wordlists/junior_high/media"
            
            if word_dict['audio_path_uk']:
                word_dict['audio_path_uk'] = f"{media_prefix}/{word_dict['audio_path_uk']}"
            else:
                # 如果没有音频文件，提供TTS URL
                word_dict['audio_path_uk'] = f"/api/tts/{word_dict['spelling']}"
                
            if word_dict['audio_path_us']:
                word_dict['audio_path_us'] = f"{media_prefix}/{word_dict['audio_path_us']}"
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
    
    # 添加调试日志
    app.logger.info(f"收到答案提交请求: 用户ID={student_id}, 答案数量={len(answers)}")
    if answers:
        app.logger.info(f"第一个答案示例: word_id={answers[0].get('word_id')}, answer={answers[0].get('answer')}")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    error_details = []
    for item in answers:
        word_id = item.get('word_id')
        student_answer = item.get('answer', '')

        correct_word = cursor.execute('SELECT spelling FROM Words WHERE word_id = ?', (word_id,)).fetchone()
        if correct_word:
            correct_spelling = correct_word['spelling']
            # 处理斜杠分隔的拼写变体
            valid_spellings = [s.strip().lower() for s in correct_spelling.split('/')]
            
            # 处理逗号分隔的拼写变体（如"wis, wit"）
            expanded_spellings = []
            for spelling in valid_spellings:
                if ',' in spelling:
                    # 对于逗号分隔的变体，将它们分开并添加到有效拼写列表中
                    comma_variants = [v.strip().lower() for v in spelling.split(',')]
                    expanded_spellings.extend(comma_variants)
                else:
                    expanded_spellings.append(spelling)
            
            valid_spellings = expanded_spellings
            
            if student_answer.strip().lower() not in valid_spellings:
                error_details.append({
                    'word_id': word_id,
                    'correct_spelling': correct_spelling,
                    'your_answer': student_answer
                })
                # 将错误记录到ErrorLogs表，使用当前用户ID
                try:
                    cursor.execute(
                        "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, datetime('now', 'localtime'))",
                        (student_id, word_id, 'spelling_mvp', student_answer)
                    )
                    app.logger.info(f"记录错误: 用户ID={student_id}, 单词ID={word_id}, 学生答案={student_answer}, 模式=错词复习, 正确拼写={correct_spelling}")
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
                                "INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, date('now', 'localtime'))",
                            (student_id, word_id, 'spelling_mvp', student_answer)
                            )
                        except sqlite3.Error as e2:
                            app.logger.error(f"创建ErrorLogs表并插入数据失败: {e2}")

    # 更新SRS进度（仅对已登录用户）
    if student_id != -1:
        try:
            for item in answers:
                word_id = item.get('word_id')
                student_answer = item.get('answer', '')
                correct_word = cursor.execute('SELECT spelling FROM Words WHERE word_id = ?', (word_id,)).fetchone()
                
                if correct_word:
                    correct_spelling = correct_word['spelling']
                    valid_spellings = [s.strip().lower() for s in correct_spelling.split('/')]
                    
                    # 处理逗号分隔的拼写变体
                    expanded_spellings = []
                    for spelling in valid_spellings:
                        if ',' in spelling:
                            comma_variants = [v.strip().lower() for v in spelling.split(',')]
                            expanded_spellings.extend(comma_variants)
                        else:
                            expanded_spellings.append(spelling)
                    
                    valid_spellings = expanded_spellings
                    
                    # 判断答案是否正确，更新SRS进度
                    is_correct = student_answer.strip().lower() in valid_spellings
                    grade = 4 if is_correct else 1  # 正确给4分，错误给1分
                    
                    # 获取当前SRS进度
                    cursor.execute("""
                        SELECT repetitions, interval FROM StudentWordProgress 
                        WHERE student_id = ? AND word_id = ?
                    """, (student_id, word_id))
                    
                    progress = cursor.fetchone()
                    
                    if not progress:
                        # 创建新进度记录
                        repetitions = 0
                        interval = 1
                    else:
                        repetitions = progress[0] or 0
                        interval = progress[1] or 1
                    
                    # 根据评分更新间隔（简化的SuperMemo算法）
                    if grade >= 3:  # 记得
                        repetitions += 1
                        if repetitions == 1:
                            interval = 1
                        elif repetitions == 2:
                            interval = 6
                        else:
                            interval = int(interval * 2.5)
                    else:  # 不记得
                        repetitions = max(0, repetitions - 1)  # 减少重复次数但不重置为0
                        interval = max(1, interval // 2)  # 减少间隔但不重置为1
                    
                    # 限制最大间隔
                    interval = min(interval, 365)
                    
                    # 计算下次复习日期
                    from datetime import datetime, timedelta
                    next_review_date = (datetime.now() + timedelta(days=interval)).strftime('%Y-%m-%d')
                    
                    # 更新或插入进度
                    cursor.execute("""
                        INSERT OR REPLACE INTO StudentWordProgress 
                        (student_id, word_id, repetitions, interval, next_review_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (student_id, word_id, repetitions, interval, next_review_date))
                    
            app.logger.info(f"SRS进度更新完成: 用户ID={student_id}, 处理单词数={len(answers)}")
        except Exception as e:
            app.logger.error(f"更新SRS进度时出错: {e}")
            # 不中断主流程，继续执行

    conn.commit()
    conn.close()
    
    # 添加提交完成日志
    app.logger.info(f"答案提交完成: 用户ID={student_id}, 错误数量={len(error_details)}")

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

# --- API路由：获取错误统计信息 ---
@app.route('/api/error-stats')
def get_error_stats():
    """获取指定列表的错误统计信息"""
    try:
        # 获取当前登录用户ID，如果未登录则使用默认值-1（表示游客）
        student_id = session.get('user_id', -1)
        # 如果用户未登录，返回错误信息
        if student_id == -1:
            return jsonify({'error': '请先登录后查看错误统计'}), 401
            
        list_id = request.args.get('list_id', type=int)
        if not list_id:
            return jsonify({'error': '请提供list_id参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先获取列表和词书信息（无论是否有错误）
        list_query = """
        SELECT wl.list_name, b.book_name
        FROM WordLists wl
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE wl.list_id = ?
        """
        
        cursor.execute(list_query, (list_id,))
        list_result = cursor.fetchone()
        
        list_name = f'List {list_id}'  # 默认值
        book_name = 'Unknown Book'     # 默认值
        
        if list_result:
            list_name = list_result[0] or f'List {list_id}'
            book_name = list_result[1] or 'Unknown Book'
        
        # 查询该列表中学生的错误统计
        error_query = """
        SELECT 
            COUNT(DISTINCT e.word_id) as error_words_count,
            COUNT(e.error_id) as total_errors
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        WHERE e.student_id = ? AND w.list_id = ?
        """
        
        cursor.execute(error_query, (student_id, list_id))
        error_result = cursor.fetchone()
        
        if error_result:
            stats = {
                'error_words_count': error_result[0],
                'total_errors': error_result[1],
                'list_name': list_name,
                'book_name': book_name
            }
        else:
            stats = {
                'error_words_count': 0,
                'total_errors': 0,
                'list_name': list_name,
                'book_name': book_name
            }
        
        conn.close()
        return jsonify(stats)
        
    except sqlite3.Error as e:
        app.logger.error(f"获取错误统计时出错: {e}")
        return jsonify({'error': '获取错误统计失败'}), 500

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
        book_id = request.args.get('book_id', default=None, type=int)  # 词书ID筛选
        list_id = request.args.get('list_id', default=None, type=int)  # 列表ID筛选
        date_from = request.args.get('date_from', default=None, type=str)  # 开始日期筛选
        date_to = request.args.get('date_to', default=None, type=str)  # 结束日期筛选
        sort_by = request.args.get('sort_by', default='date', type=str)  # 排序字段，默认按日期
        sort_order = request.args.get('sort_order', default='desc', type=str)  # 排序方向，默认降序
        
        app.logger.info(f"获取错误历史记录: student_id={student_id}, limit={limit}, book_id={book_id}, list_id={list_id}, date_from={date_from}, date_to={date_to}, sort_by={sort_by}, sort_order={sort_order}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询错误记录，并关联单词信息、词书和单元名称
        query = """
        SELECT e.error_id, e.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, 
               e.student_answer, e.error_type, e.error_date,
               (SELECT COUNT(*) FROM ErrorLogs WHERE word_id = e.word_id AND student_id = e.student_id) as error_count,
               wl.book_id, b.book_name, wl.list_name
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = ?
        """
        
        params = [student_id]
        
        # 添加词书和列表筛选条件
        if book_id is not None:
            query += " AND wl.book_id = ?"
            params.append(book_id)
        
        if list_id is not None:
            query += " AND w.list_id = ?"
            params.append(list_id)
        
        # 添加日期范围筛选条件
        if date_from is not None:
            query += " AND e.error_date >= ?"
            params.append(date_from)
        
        if date_to is not None:
            query += " AND e.error_date <= ?"
            params.append(date_to + ' 23:59:59')  # 包含当天的所有时间
        
        # 添加排序逻辑
        if sort_by == 'error_count':
            query += " ORDER BY error_count"
        else:  # 默认按日期排序
            query += " ORDER BY e.error_date"
        
        # 添加排序方向
        if sort_order.lower() == 'asc':
            query += " ASC"
        else:  # 默认降序
            query += " DESC"
        
        query += " LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        errors = cursor.fetchall()
        
        # 查询错误统计信息
        stats_query = """
        SELECT w.list_id, COUNT(*) as error_count,
               (SELECT COUNT(DISTINCT word_id) FROM ErrorLogs WHERE student_id = ? AND word_id IN 
                (SELECT word_id FROM Words WHERE list_id = w.list_id)) as unique_words_count,
               wl.book_id, b.book_name, wl.list_name
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = ?
        """
        
        stats_params = [student_id, student_id]
        
        # 添加词书和列表筛选条件
        if book_id is not None:
            stats_query += " AND wl.book_id = ?"
            stats_params.append(book_id)
        
        if list_id is not None:
            stats_query += " AND w.list_id = ?"
            stats_params.append(list_id)
        
        # 添加日期范围筛选条件
        if date_from is not None:
            stats_query += " AND e.error_date >= ?"
            stats_params.append(date_from)
        
        if date_to is not None:
            stats_query += " AND e.error_date <= ?"
            stats_params.append(date_to + ' 23:59:59')  # 包含当天的所有时间
        
        stats_query += """
        GROUP BY w.list_id
        ORDER BY w.list_id
        """
        
        cursor.execute(stats_query, stats_params)
        stats = cursor.fetchall()
        
        # 查询每个单词的错误历史
        word_history_query = """
        SELECT w.word_id, w.spelling, w.list_id, w.meaning_cn, w.pos,
               COUNT(*) as total_errors,
               GROUP_CONCAT(e.student_answer, ', ') as wrong_answers,
               GROUP_CONCAT(e.error_date, ', ') as error_dates,
               wl.book_id, b.book_name, wl.list_name
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = ?
        """
        
        word_history_params = [student_id]
        
        # 添加词书和列表筛选条件
        if book_id is not None:
            word_history_query += " AND wl.book_id = ?"
            word_history_params.append(book_id)
        
        if list_id is not None:
            word_history_query += " AND w.list_id = ?"
            word_history_params.append(list_id)
        
        # 添加日期范围筛选条件
        if date_from is not None:
            word_history_query += " AND e.error_date >= ?"
            word_history_params.append(date_from)
        
        if date_to is not None:
            word_history_query += " AND e.error_date <= ?"
            word_history_params.append(date_to + ' 23:59:59')  # 包含当天的所有时间
        
        word_history_query += """
        GROUP BY w.word_id
        """
        
        # 添加排序逻辑
        if sort_by == 'error_count' and sort_order.lower() == 'asc':
            word_history_query += " ORDER BY total_errors ASC"
        else:  # 默认按错误次数降序
            word_history_query += " ORDER BY total_errors DESC"
        
        word_history_query += " LIMIT 20"
        
        cursor.execute(word_history_query, word_history_params)
        word_history = cursor.fetchall()
        
        # 转换为JSON格式
        error_list = [dict(error) for error in errors]
        stats_list = [dict(stat) for stat in stats]
        word_history_list = [dict(item) for item in word_history]
        
        # 获取错误单词数（用于计算正确率）
        total_tested_query = "SELECT COUNT(DISTINCT word_id) FROM ErrorLogs WHERE student_id = ?"
        cursor.execute(total_tested_query, (student_id,))
        total_tested = cursor.fetchone()[0]
        
        # 计算总体正确率
        # 由于数据库只记录错误，我们采用一个更合理的计算方式
        # 方案：基于错误单词数来估算正确率
        # 假设用户测试的单词数约为错误单词数的3-5倍（这是一个合理的假设）
        
        # 获取用户错误单词涉及的所有列表的总单词数
        lists_with_errors_query = """
        SELECT DISTINCT w.list_id
        FROM ErrorLogs e
        JOIN Words w ON e.word_id = w.word_id
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = ?
        """
        
        lists_params = [student_id]
        
        # 添加筛选条件
        if book_id is not None:
            lists_with_errors_query += " AND wl.book_id = ?"
            lists_params.append(book_id)
        if list_id is not None:
            lists_with_errors_query += " AND w.list_id = ?"
            lists_params.append(list_id)
        if date_from is not None:
            lists_with_errors_query += " AND e.error_date >= ?"
            lists_params.append(date_from)
        if date_to is not None:
            lists_with_errors_query += " AND e.error_date <= ?"
            lists_params.append(date_to + ' 23:59:59')
        
        cursor.execute(lists_with_errors_query, lists_params)
        lists_with_errors = cursor.fetchall()
        
        # 计算这些列表中的总单词数
        total_words = 0
        if lists_with_errors:
            list_ids = [str(row['list_id']) for row in lists_with_errors]
            list_ids_str = ','.join(list_ids)
            
            total_words_query = f"""
            SELECT COUNT(*) as total_words
            FROM Words w
            LEFT JOIN WordLists wl ON w.list_id = wl.list_id
            LEFT JOIN Books b ON wl.book_id = b.book_id
            WHERE w.list_id IN ({list_ids_str})
            """
            
            # 添加词书筛选条件
            if book_id is not None:
                total_words_query += " AND wl.book_id = ?"
                cursor.execute(total_words_query, [book_id])
            else:
                cursor.execute(total_words_query)
            
            total_words_result = cursor.fetchone()
            total_words = total_words_result[0] if total_words_result else 0
        
        # 计算正确率
        accuracy_rate = 0
        if total_words > 0 and total_tested > 0:
            # 错误单词数就是total_tested
            # 正确率 = (总单词数 - 错误单词数) / 总单词数 * 100
            correct_words = total_words - total_tested
            accuracy_rate = round((correct_words / total_words) * 100, 2)
            # 确保正确率在0-100之间
            accuracy_rate = max(0, min(100, accuracy_rate))
        elif total_tested > 0:
            # 如果没有找到总单词数，使用一个保守的估算
            # 假设用户测试了错误单词数的4倍单词
            estimated_total = total_tested * 4
            correct_words = estimated_total - total_tested
            accuracy_rate = round((correct_words / estimated_total) * 100, 2)
            accuracy_rate = max(0, min(100, accuracy_rate))
        
        conn.close()
        
        return jsonify({
            'errors': error_list,
            'stats': stats_list,
            'word_history': word_history_list,
            'total_tested': total_tested,
            'accuracy_rate': accuracy_rate
        })
    except Exception as e:
        app.logger.error(f"获取错误历史记录时出错: {str(e)}")
        return jsonify({'error': '获取错误历史记录失败'}), 500

# --- 记录错误API ---
@app.route('/api/record-error', methods=['POST'])
def record_error():
    """记录用户的错误答案"""
    try:
        # 获取当前登录用户ID，如果未登录则使用默认值-1（表示游客）
        student_id = session.get('user_id', -1)
        # 如果用户未登录，返回错误信息
        if student_id == -1:
            return jsonify({'error': '请先登录后记录错误'}), 401
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        word_id = data.get('word_id')
        student_answer = data.get('student_answer', '')
        list_id = data.get('list_id')
        
        if not word_id:
            return jsonify({'error': '缺少单词ID'}), 400
        
        app.logger.info(f"记录错误: student_id={student_id}, word_id={word_id}, student_answer='{student_answer}', list_id={list_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查单词是否存在
        cursor.execute("SELECT spelling, meaning_cn FROM Words WHERE word_id = ?", (word_id,))
        word = cursor.fetchone()
        if not word:
            conn.close()
            return jsonify({'error': '单词不存在'}), 404
        
        # 记录错误到ErrorLogs表
        cursor.execute("""
            INSERT INTO ErrorLogs (student_id, word_id, student_answer, error_type, error_date)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (student_id, word_id, student_answer, 'spelling_error'))
        
        conn.commit()
        conn.close()
        
        app.logger.info(f"成功记录错误: student_id={student_id}, word_id={word_id}, word='{word['spelling']}'")
        
        return jsonify({
            'success': True,
            'message': '错误已记录',
            'word_id': word_id,
            'word': word['spelling']
        })
        
    except Exception as e:
        app.logger.error(f"记录错误时出错: {str(e)}")
        return jsonify({'error': '记录错误失败'}), 500
        
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

# --- 数据库初始化 ---
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查Users表是否存在role字段
    cursor.execute("PRAGMA table_info(Users)")
    columns = cursor.fetchall()
    has_role_column = any(column['name'] == 'role' for column in columns)
    
    # 如果没有role字段，添加该字段
    if not has_role_column and any(column['name'] == 'id' for column in columns):
        cursor.execute("ALTER TABLE Users ADD COLUMN role TEXT DEFAULT 'student'")
        conn.commit()
        app.logger.info("已向Users表添加role字段")
    
    # 检查是否有管理员账户
    admin = cursor.execute("SELECT * FROM Users WHERE role = 'admin'").fetchone()
    if not admin:
        # 创建默认管理员账户
        admin_username = 'admin'
        admin_password = 'admin123'  # 默认密码，应提示用户首次登录后修改
        password_hash = generate_password_hash(admin_password)
        
        # 检查是否已存在同名用户
        existing_user = cursor.execute("SELECT * FROM Users WHERE username = ?", (admin_username,)).fetchone()
        if existing_user:
            # 将已存在的用户升级为管理员
            cursor.execute("UPDATE Users SET role = 'admin' WHERE username = ?", (admin_username,))
        else:
            # 创建新的管理员账户
            cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)", 
                          (admin_username, password_hash, 'admin'))
        
        conn.commit()
        app.logger.info("已创建默认管理员账户")
    
    conn.close()

# 应用启动时初始化数据库
with app.app_context():
    init_db()

# --- PDF导出功能 ---
@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    """导出错误历史记录为PDF"""
    try:
        app.logger.info("开始导出PDF")
        start_time = datetime.datetime.now()
        
        # 获取当前登录用户ID，如果未登录则使用默认值-1（表示游客）
        student_id = session.get('user_id', -1)
        # 如果用户未登录，返回错误信息
        if student_id == -1:
            return jsonify({'error': '请先登录后导出错误历史记录'}), 401
            
        # 获取请求数据
        data = request.get_json()
        errors = data.get('errors', [])
        selected_fields = data.get('fields', [])
        hide_word = data.get('hideWord', False)
        book_name = data.get('bookName', '')
        list_name = data.get('listName', '')
        
        app.logger.info(f"PDF导出数据: {len(errors)}条记录, {len(selected_fields)}个字段")
        
        # 如果没有错误记录，返回错误信息
        if not errors:
            return jsonify({'error': '没有可导出的数据'}), 400
            
        # 导入reportlab库
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import io
        import datetime
        
        # 注册中文字体
        try:
            # 检查是否已经注册了字体，避免重复注册
            if 'SimSun' not in pdfmetrics.getRegisteredFontNames():
                app.logger.info("注册中文字体: SimSun")
                # 尝试注册系统中的中文字体
                pdfmetrics.registerFont(TTFont('SimSun', 'C:\\Windows\\Fonts\\simsun.ttc'))
        except Exception as font_error:
            # 如果失败，使用默认字体
            app.logger.warning(f"无法加载中文字体，将使用默认字体: {str(font_error)}")
            
        app.logger.info("初始化PDF文档")
        start_pdf_time = datetime.datetime.now()
        
        # 创建PDF文档
        buffer = io.BytesIO()
        
        # 获取当前用户名
        username = session.get('username', 'User')
        
        # 生成文件名
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        if book_name and list_name:
            filename = f"{username}-{current_date}当日错词考核纸-{book_name}{list_name}.pdf"
        elif book_name:
            filename = f"{username}-{current_date}当日错词考核纸-{book_name}.pdf"
        elif list_name:
            filename = f"{username}-{current_date}当日错词考核纸-{list_name}.pdf"
        else:
            filename = f"{username}-{current_date}当日错词考核纸.pdf"
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # 创建样式
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Chinese',
            fontName='SimSun',
            fontSize=10,
            leading=12
        ))
        styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName='SimSun',
            fontSize=16,
            leading=20,
            alignment=1  # 居中对齐
        ))
        
        # 创建内容列表
        elements = []
        
        # 添加Logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'img', 'Logo', 'orange-theme-logo.svg')
        if os.path.exists(logo_path):
            img = Image(logo_path, width=2*inch, height=1*inch)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 0.5*inch))
        
        # 添加标题
        title = f"{username} - {current_date}当日错词考核纸"
        if book_name or list_name:
            subtitle = []
            if book_name:
                subtitle.append(book_name)
            if list_name:
                subtitle.append(list_name)
            title += f" - {' '.join(subtitle)}"
        elements.append(Paragraph(title, styles['ChineseTitle']))
        elements.append(Spacer(1, 0.25*inch))
        
        # 添加错误记录
        total_errors = len(errors)
        app.logger.info(f"开始处理{total_errors}条错误记录")
        
        # 批量处理，每50条记录记录一次日志
        batch_size = 50
        
        # 如果错误记录过多，可能导致内存问题，限制最大处理数量
        max_errors = 500
        if total_errors > max_errors:
            app.logger.warning(f"错误记录数量过多({total_errors})，将只处理前{max_errors}条记录")
            errors = errors[:max_errors]
            total_errors = max_errors
        
        for i, error in enumerate(errors):
            # 创建表格数据
            data = []
            
            # 添加序号和单词
            if hide_word:
                data.append([f"{i+1}.", "______"])
            else:
                data.append([f"{i+1}.", error.get('spelling', '')])
            
            # 添加选定的字段
            for field in selected_fields:
                if field != 'word':  # 单词已经作为标题显示了
                    label = ''
                    value = ''
                    
                    if field == 'meaning_cn':
                        label = '中文意思'
                        value = error.get('meaning_cn', '-')
                    elif field == 'pos':
                        label = '词性'
                        value = error.get('pos', '-')
                    elif field == 'ipa':
                        label = '音标'
                        value = error.get('ipa', '-')
                    elif field == 'meaning_en':
                        label = '英文释义'
                        value = error.get('meaning_en', '-')
                    elif field == 'example_en':
                        label = '英文例句'
                        value = error.get('example_en', '-')
                    elif field == 'example_cn':
                        label = '中文例句'
                        value = error.get('example_cn', '-')
                    elif field == 'list':
                        label = '所属列表'
                        value = error.get('list_name', '-')
                    elif field == 'wrong_answers':
                        label = '错误答案'
                        wrong_answers = error.get('wrong_answers', [])
                        if wrong_answers and isinstance(wrong_answers, list) and len(wrong_answers) > 0:
                            value = '; '.join(wrong_answers)
                        else:
                            value = '-'
                    elif field == 'error_date':
                        label = '错误日期'
                        value = error.get('error_date', '-')
                    elif field == 'error_count':
                        label = '错误次数'
                        value = str(error.get('error_count', '0'))
                    
                    data.append(['', f"{label}: {value}"])
            
            # 记录处理进度
            if (i + 1) % batch_size == 0 or i == total_errors - 1:
                app.logger.info(f"PDF生成进度: {i+1}/{total_errors} ({((i+1)/total_errors*100):.1f}%)")
            
            # 创建表格
            table = Table(data, colWidths=[0.5*inch, 4*inch])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.1*inch))
        
        # 记录表格生成完成时间
        pre_build_time = datetime.datetime.now()
        table_gen_duration = (pre_build_time - start_pdf_time).total_seconds()
        app.logger.info(f"表格数据准备完成，耗时: {table_gen_duration:.2f}秒")
        
        # 构建PDF文档
        app.logger.info("开始构建PDF文档")
        doc.build(elements)
        
        # 记录PDF构建完成时间
        post_build_time = datetime.datetime.now()
        build_duration = (post_build_time - pre_build_time).total_seconds()
        app.logger.info(f"PDF文档构建完成，耗时: {build_duration:.2f}秒")
        
        # 获取PDF内容
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # 记录PDF大小
        pdf_size = len(pdf_data) / 1024  # KB
        app.logger.info(f"PDF文件大小: {pdf_size:.2f}KB")
        
        # 计算生成PDF所需时间
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        app.logger.info(f"PDF生成完成，耗时: {duration:.2f}秒, 文件大小: {len(pdf_data)/1024:.2f}KB")
        
        # 返回PDF文件
        from flask import send_file
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        app.logger.error(f"导出PDF时出错: {e}")
        return jsonify({'error': f'导出PDF失败: {str(e)}'}), 500

# --- 提供JS修复脚本 ---
@app.route('/fix_mess_display_new.js')
def get_fix_mess_display_new_js():
    return send_from_directory('.', 'fix_mess_display_new.js')

# --- SRS (Spaced Repetition System) API Endpoints ---

@app.route('/api/srs/progress', methods=['GET'])
def get_srs_progress():
    """获取用户的SRS学习进度"""
    try:
        student_id = session.get('user_id', -1)
        if student_id == -1:
            return jsonify({'error': '请先登录'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取用户的学习进度统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_words,
                SUM(CASE WHEN repetitions > 0 THEN 1 ELSE 0 END) as learned_words,
                SUM(CASE WHEN next_review_date <= date('now') THEN 1 ELSE 0 END) as due_words,
                AVG(interval) as avg_interval
            FROM StudentWordProgress 
            WHERE student_id = ?
        """, (student_id,))
        
        stats = cursor.fetchone()
        
        # 获取最近学习的单词（最近7天）
        cursor.execute("""
            SELECT w.spelling, w.meaning_cn, p.repetitions, p.interval, p.next_review_date,
                   wl.list_name, b.book_name
            FROM StudentWordProgress p
            JOIN Words w ON p.word_id = w.word_id
            LEFT JOIN WordLists wl ON w.list_id = wl.list_id
            LEFT JOIN Books b ON wl.book_id = b.book_id
            WHERE p.student_id = ? 
            AND p.repetitions > 0
            ORDER BY p.next_review_date DESC
            LIMIT 20
        """, (student_id,))
        
        recent_words = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'stats': {
                'total_words': stats[0] or 0,
                'learned_words': stats[1] or 0,
                'due_words': stats[2] or 0,
                'avg_interval': round(stats[3] or 0, 1)
            },
            'recent_words': recent_words
        })
        
    except Exception as e:
        app.logger.error(f"获取SRS进度时出错: {e}")
        return jsonify({'error': '获取学习进度失败'}), 500

@app.route('/api/srs/due-words', methods=['GET'])
def get_due_words():
    """获取需要复习的单词"""
    try:
        student_id = session.get('user_id', -1)
        if student_id == -1:
            return jsonify({'error': '请先登录'}), 401
        
        # 获取参数
        limit = request.args.get('limit', default=10, type=int)
        list_id = request.args.get('list_id', type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        where_clause = "p.student_id = ? AND p.next_review_date <= date('now')"
        params = [student_id]
        
        if list_id:
            where_clause += " AND w.list_id = ?"
            params.append(list_id)
        
        # 获取需要复习的单词
        cursor.execute(f"""
            SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.audio_path_uk, w.audio_path_us,
                   w.derivatives, w.root_etymology, w.mnemonic, w.comparison, w.collocation,
                   w.exam_sentence, w.exam_year_source, w.exam_options, w.exam_explanation, w.tips,
                   p.repetitions, p.interval, p.next_review_date,
                   wl.list_name, b.book_name
            FROM StudentWordProgress p
            JOIN Words w ON p.word_id = w.word_id
            LEFT JOIN WordLists wl ON w.list_id = wl.list_id
            LEFT JOIN Books b ON wl.book_id = b.book_id
            WHERE {where_clause}
            ORDER BY p.next_review_date ASC, p.repetitions ASC
            LIMIT ?
        """, params + [limit])
        
        due_words = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'due_words': due_words})
        
    except Exception as e:
        app.logger.error(f"获取待复习单词时出错: {e}")
        return jsonify({'error': '获取待复习单词失败'}), 500

@app.route('/api/srs/update-progress', methods=['POST'])
def update_srs_progress():
    """更新单词的SRS进度"""
    try:
        student_id = session.get('user_id', -1)
        if student_id == -1:
            return jsonify({'error': '请先登录'}), 401
        
        data = request.get_json()
        word_id = data.get('word_id')
        grade = data.get('grade', 3)  # 0-5的评分
        
        if not word_id:
            return jsonify({'error': '缺少单词ID'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取当前进度
        cursor.execute("""
            SELECT repetitions, interval FROM StudentWordProgress 
            WHERE student_id = ? AND word_id = ?
        """, (student_id, word_id))
        
        progress = cursor.fetchone()
        
        if not progress:
            # 创建新进度记录
            repetitions = 0
            interval = 1
        else:
            repetitions = progress[0] or 0
            interval = progress[1] or 1
        
        # 根据评分更新间隔（简化的SuperMemo算法）
        if grade >= 3:  # 记得
            repetitions += 1
            if repetitions == 1:
                interval = 1
            elif repetitions == 2:
                interval = 6
            else:
                interval = int(interval * 2.5)
        else:  # 不记得
            repetitions = 0
            interval = 1
        
        # 限制最大间隔
        interval = min(interval, 365)
        
        # 计算下次复习日期
        from datetime import datetime, timedelta
        next_review_date = (datetime.now() + timedelta(days=interval)).strftime('%Y-%m-%d')
        
        # 更新或插入进度
        cursor.execute("""
            INSERT OR REPLACE INTO StudentWordProgress 
            (student_id, word_id, repetitions, interval, next_review_date)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, word_id, repetitions, interval, next_review_date))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': '进度更新成功',
            'new_interval': interval,
            'new_repetitions': repetitions,
            'next_review_date': next_review_date
        })
        
    except Exception as e:
        app.logger.error(f"更新SRS进度时出错: {e}")
        return jsonify({'error': '更新进度失败'}), 500

@app.route('/api/srs/mastery-stats', methods=['GET'])
def get_mastery_stats():
    """获取掌握度统计"""
    try:
        student_id = session.get('user_id', -1)
        if student_id == -1:
            return jsonify({'error': '请先登录'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取掌握度分布
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN repetitions = 0 THEN '未学习'
                    WHEN repetitions = 1 THEN '初学'
                    WHEN repetitions <= 3 THEN '熟悉'
                    WHEN repetitions <= 10 THEN '掌握'
                    ELSE '精通'
                END as mastery_level,
                COUNT(*) as count
            FROM StudentWordProgress 
            WHERE student_id = ?
            GROUP BY mastery_level
            ORDER BY 
                CASE mastery_level
                    WHEN '未学习' THEN 1
                    WHEN '初学' THEN 2
                    WHEN '熟悉' THEN 3
                    WHEN '掌握' THEN 4
                    WHEN '精通' THEN 5
                END
        """, (student_id,))
        
        mastery_distribution = [dict(row) for row in cursor.fetchall()]
        
        # 获取最近7天的学习统计
        cursor.execute("""
            SELECT 
                date(created_at) as study_date,
                COUNT(*) as words_studied
            FROM (
                SELECT 
                    CASE 
                        WHEN next_review_date IS NOT NULL THEN next_review_date
                        ELSE date('now')
                    END as created_at
                FROM StudentWordProgress 
                WHERE student_id = ? AND repetitions > 0
            )
            WHERE created_at >= date('now', '-7 days')
            GROUP BY date(created_at)
            ORDER BY study_date
        """, (student_id,))
        
        weekly_stats = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'mastery_distribution': mastery_distribution,
            'weekly_stats': weekly_stats
        })
        
    except Exception as e:
        app.logger.error(f"获取掌握度统计时出错: {e}")
        return jsonify({'error': '获取掌握度统计失败'}), 500

# --- 启动命令 ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

