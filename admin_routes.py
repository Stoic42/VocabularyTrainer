import sqlite3
import json
import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, session, render_template
from functools import wraps

# 创建蓝图
admin_bp = Blueprint('admin', __name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vocabulary.db')

# 管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否登录
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        # 检查用户是否是管理员
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT role FROM Users WHERE id = ?', (session['user_id'],))
            user = cursor.fetchone()
            conn.close()
            
            if not user or user[0] != 'admin':
                return jsonify({'error': '您没有管理员权限'}), 403
                
        except Exception as e:
            logger.error(f"检查管理员权限时出错: {e}")
            return jsonify({'error': '服务器错误'}), 500
            
        return f(*args, **kwargs)
    return decorated_function

# 管理员仪表盘页面路由
@admin_bp.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# 获取仪表盘数据API
@admin_bp.route('/api/admin/dashboard')
@admin_required
def get_dashboard_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 启用行工厂，使结果可以通过列名访问
        cursor = conn.cursor()
        
        # 获取总学生数（非管理员用户）
        cursor.execute('SELECT COUNT(*) FROM Users WHERE role != "admin"')
        total_students = cursor.fetchone()[0]
        
        # 获取今日活跃学生数（今天有提交测试的用户）
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(DISTINCT student_id) 
            FROM ErrorLogs 
            WHERE date(timestamp) = ?
        """, (today,))
        active_students = cursor.fetchone()[0]
        
        # 获取总测试次数（通过错误日志估算）
        cursor.execute('SELECT COUNT(DISTINCT test_id) FROM ErrorLogs')
        total_tests = cursor.fetchone()[0]
        
        # 获取平均正确率
        cursor.execute("""
            SELECT AVG(correct_rate) FROM (
                SELECT student_id, 
                       COUNT(CASE WHEN is_correct = 1 THEN 1 END) * 100.0 / COUNT(*) as correct_rate
                FROM ErrorLogs
                GROUP BY student_id
            )
        """)
        avg_accuracy_result = cursor.fetchone()
        avg_accuracy = round(avg_accuracy_result[0] if avg_accuracy_result[0] is not None else 0, 2)
        
        # 获取学生列表
        cursor.execute("""
            SELECT u.id, u.username, u.role, u.created_at as register_date,
                   (SELECT MAX(error_date) FROM ErrorLogs WHERE student_id = u.id) as last_activity,
                   (SELECT COUNT(DISTINCT test_id) FROM ErrorLogs WHERE student_id = u.id) as test_count,
                   (SELECT COUNT(CASE WHEN is_correct = 1 THEN 1 END) * 100.0 / COUNT(*) 
                    FROM ErrorLogs WHERE student_id = u.id) as accuracy
            FROM Users u
            WHERE u.role = 'student'
            ORDER BY last_activity IS NULL, last_activity DESC
        """)
        students = [dict(row) for row in cursor.fetchall()]
        
        # 处理日期格式和空值
        for student in students:
            if student['register_date']:
                student['register_date'] = datetime.fromisoformat(student['register_date']).strftime('%Y-%m-%d')
            if student['last_activity']:
                student['last_activity'] = datetime.fromisoformat(student['last_activity']).strftime('%Y-%m-%d %H:%M')
            if student['accuracy'] is not None:
                student['accuracy'] = round(student['accuracy'], 2)
            else:
                student['accuracy'] = 0
        
        # 获取单词错误统计
        cursor.execute("""
            SELECT 
                w.spelling, 
                w.list_id,
                COUNT(*) as error_count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ErrorLogs) as error_rate,
                GROUP_CONCAT(DISTINCT e.user_answer, ', ') as common_errors
            FROM ErrorLogs e
            JOIN Words w ON e.word_id = w.id
            WHERE e.is_correct = 0
            GROUP BY w.id
            ORDER BY error_count DESC
            LIMIT 20
        """)
        word_stats = [dict(row) for row in cursor.fetchall()]
        
        # 处理错误率和常见错误
        for word in word_stats:
            word['error_rate'] = round(word['error_rate'], 2)
            # 限制常见错误的数量
            if word['common_errors']:
                errors = word['common_errors'].split(', ')
                word['common_errors'] = ', '.join(errors[:3])  # 只显示前3个常见错误
        
        # 获取正确率趋势（最近30天）
        accuracy_trend = []
        for i in range(30, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN is_correct = 1 THEN 1 END) * 100.0 / COUNT(*) as accuracy
                FROM ErrorLogs
                WHERE date(timestamp) = ?
            """, (date,))
            result = cursor.fetchone()
            accuracy = round(result[0], 2) if result[0] is not None else 0
            accuracy_trend.append({
                'date': date,
                'accuracy': accuracy
            })
        
        # 获取活动趋势（最近30天）
        activity_trend = []
        for i in range(30, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(DISTINCT test_id) as test_count
                FROM ErrorLogs
                WHERE date(timestamp) = ?
            """, (date,))
            result = cursor.fetchone()
            test_count = result[0] if result[0] is not None else 0
            activity_trend.append({
                'date': date,
                'test_count': test_count
            })
        
        conn.close()
        
        # 返回仪表盘数据
        return jsonify({
            'total_students': total_students,
            'active_students': active_students,
            'total_tests': total_tests,
            'avg_accuracy': avg_accuracy,
            'students': students,
            'word_stats': word_stats,
            'accuracy_trend': accuracy_trend,
            'activity_trend': activity_trend
        })
        
    except Exception as e:
        logger.error(f"获取仪表盘数据时出错: {e}")
        return jsonify({'error': f'获取仪表盘数据失败: {str(e)}'}), 500

# 获取单个学生详情API
@admin_bp.route('/api/admin/student/<int:student_id>')
@admin_required
def get_student_details(student_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取学生基本信息
        cursor.execute('SELECT id, username, role, created_at FROM Users WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': '学生不存在'}), 404
        
        student_data = dict(student)
        
        # 获取学生测试统计
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT test_id) as test_count,
                COUNT(CASE WHEN is_correct = 1 THEN 1 END) * 100.0 / COUNT(*) as accuracy,
                MAX(timestamp) as last_activity
            FROM ErrorLogs
            WHERE student_id = ?
        """, (student_id,))
        stats = cursor.fetchone()
        
        if stats:
            student_data.update(dict(stats))
            if student_data['accuracy'] is not None:
                student_data['accuracy'] = round(student_data['accuracy'], 2)
            else:
                student_data['accuracy'] = 0
        
        # 获取学生最近的错误记录
        cursor.execute("""
            SELECT 
                e.id, e.timestamp, e.test_id, e.is_correct,
                w.spelling, w.meaning, e.user_answer
            FROM ErrorLogs e
            JOIN Words w ON e.word_id = w.id
            WHERE e.student_id = ?
            ORDER BY e.timestamp DESC
            LIMIT 20
        """, (student_id,))
        recent_errors = [dict(row) for row in cursor.fetchall()]
        
        # 获取学生的单词列表统计
        cursor.execute("""
            SELECT 
                w.list_id,
                COUNT(*) as total,
                COUNT(CASE WHEN e.is_correct = 1 THEN 1 END) as correct,
                COUNT(CASE WHEN e.is_correct = 1 THEN 1 END) * 100.0 / COUNT(*) as accuracy
            FROM ErrorLogs e
            JOIN Words w ON e.word_id = w.id
            WHERE e.student_id = ?
            GROUP BY w.list_id
            ORDER BY w.list_id
        """, (student_id,))
        list_stats = [dict(row) for row in cursor.fetchall()]
        
        # 处理列表统计的准确率
        for stat in list_stats:
            if stat['accuracy'] is not None:
                stat['accuracy'] = round(stat['accuracy'], 2)
            else:
                stat['accuracy'] = 0
        
        # 获取学生的学习趋势（最近14天）
        trend_data = []
        for i in range(14, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT 
                    COUNT(*) as attempts,
                    COUNT(CASE WHEN is_correct = 1 THEN 1 END) as correct,
                    COUNT(CASE WHEN is_correct = 1 THEN 1 END) * 100.0 / COUNT(*) as accuracy
                FROM ErrorLogs
                WHERE student_id = ? AND date(timestamp) = ?
            """, (student_id, date))
            result = cursor.fetchone()
            
            if result:
                data = dict(result)
                data['date'] = date
                if data['accuracy'] is not None:
                    data['accuracy'] = round(data['accuracy'], 2)
                else:
                    data['accuracy'] = 0
                trend_data.append(data)
            else:
                trend_data.append({
                    'date': date,
                    'attempts': 0,
                    'correct': 0,
                    'accuracy': 0
                })
        
        conn.close()
        
        # 返回学生详情数据
        return jsonify({
            'student': student_data,
            'recent_errors': recent_errors,
            'list_stats': list_stats,
            'trend_data': trend_data
        })
        
    except Exception as e:
        logger.error(f"获取学生详情时出错: {e}")
        return jsonify({'error': f'获取学生详情失败: {str(e)}'}), 500