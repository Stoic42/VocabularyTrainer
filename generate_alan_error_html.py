import sqlite3
import os
from datetime import datetime
import re

# 获取当前时间作为报告文件名的一部分
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 设置数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary.db")

# 设置HTML文件路径
alan_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Alan", "20250628")
os.makedirs(alan_dir, exist_ok=True)
html_file_path = os.path.join(alan_dir, f"alan_errors_20250625_{current_time}.html")

# 创建报告文件
report_file = f"generate_alan_error_html_report_{current_time}.txt"
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), report_file)

try:
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 打开报告文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("生成Alan错词HTML页面报告\n")
        f.write("===================\n\n")
        
        # 查询Alan在2025-06-25的错词记录
        f.write("查询Alan在2025-06-25的错词记录:\n")
        cursor.execute("""
            SELECT e.error_id, e.student_id, e.word_id, e.error_type, e.student_answer, e.error_date, w.spelling, w.meaning_cn
            FROM ErrorLogs e
            LEFT JOIN Words w ON e.word_id = w.word_id
            WHERE e.student_id = 3 AND e.error_date = '2025-06-25'
            ORDER BY e.error_id
        """)
        error_logs = cursor.fetchall()
        
        if error_logs:
            f.write(f"找到 {len(error_logs)} 条错词记录\n")
            
            # 查询学生信息
            cursor.execute("""
                SELECT id, username
                FROM Users
                WHERE id = 3
            """)
            student = cursor.fetchone()
            student_name = f"Alan (ID: {student[0]})" if student else "Alan"
            
            # 生成HTML内容
            f.write(f"生成HTML文件: {html_file_path}\n")
            
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{student_name} 的错词复习考核 (2025-06-25)</title>
    <style>
        body {{font-family: 'Arial', 'Microsoft YaHei', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;}}
        .container {{max-width: 1000px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}}
        h1 {{color: #333; text-align: center; margin-bottom: 30px;}}
        table {{width: 100%; border-collapse: collapse; margin-bottom: 20px;}}
        th, td {{padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd;}}
        th {{background-color: #f8f8f8; font-weight: bold;}}
        tr:hover {{background-color: #f1f1f1;}}
        .error {{color: #e74c3c;}}
        .correct {{color: #2ecc71;}}
        .footer {{text-align: center; margin-top: 30px; color: #777; font-size: 14px;}}
    </style>
</head>
<body>
    <div class="container">
        <h1>{student_name} 的错词复习考核 (2025-06-25)</h1>
        
        <h2>错词列表</h2>
        <table>
            <thead>
                <tr>
                    <th>序号</th>
                    <th>单词</th>
                    <th>释义</th>
                    <th>错误类型</th>
                    <th>学生答案</th>
                </tr>
            </thead>
            <tbody>
"""
            
            # 添加错词记录到HTML
            for i, log in enumerate(error_logs, 1):
                error_id, student_id, word_id, error_type, student_answer, error_date, spelling, meaning = log
                
                # 格式化错误类型
                if error_type == "spelling_mvp":
                    error_type_display = "拼写错误"
                elif error_type == "meaning_mvp":
                    error_type_display = "释义错误"
                else:
                    error_type_display = error_type
                
                html_content += f"""
                <tr>
                    <td>{i}</td>
                    <td>{spelling}</td>
                    <td>{meaning}</td>
                    <td>{error_type_display}</td>
                    <td>{student_answer}</td>
                </tr>
"""
            
            html_content += """
            </tbody>
        </table>
        
        <div class="footer">
            <p>生成时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
    </div>
</body>
</html>
"""
            
            # 写入HTML文件
            with open(html_file_path, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
            
            f.write(f"HTML文件已生成: {html_file_path}\n")
        else:
            f.write("未找到错词记录，不生成HTML文件\n")
        
        f.write("\n")
        
        # 总结
        f.write("总结:\n")
        if error_logs:
            f.write(f"1. 已查询Alan在2025-06-25的 {len(error_logs)} 条错词记录\n")
            f.write(f"2. 已生成HTML文件: {html_file_path}\n")
        else:
            f.write("1. 未找到Alan在2025-06-25的错词记录\n")
            f.write("2. 未生成HTML文件\n")
        
        f.write("\n生成完成\n")
    
    print(f"报告已生成: {report_path}")
    print(f"HTML文件已生成: {html_file_path}")

except sqlite3.Error as e:
    print(f"数据库错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    if 'conn' in locals():
        conn.close()