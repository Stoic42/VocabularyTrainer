import sqlite3
import os
from datetime import datetime

# 获取当前时间作为报告文件名的一部分
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 设置数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary.db")

# 旧ID到新ID的映射关系
id_mapping = {
    1186: 18008,  # diary
    1175: 17997,  # glue
    1163: 17985,  # cotton
    1185: 18007,  # under
    1180: 18002,  # terrible
    1183: 18005,  # careful
    1197: 18019,  # several
    1204: 18026,  # marathon
    1173: 17995,  # plastic
    1215: 18037,  # purpose
    1208: 18030,  # discovery
    1172: 17994,  # seal
    1203: 18025,  # reveal
    1217: 18039,  # association
    1213: 18035,  # clothes
    1179: 18001,  # convenient
    1233: 18055,  # Atlantic
    1222: 18044,  # author
    1256: 18078,  # escalator
    1276: 18098,  # nature
    1228: 18050,  # cabbage
    1252: 18074,  # ground
    1238: 18060,  # bill
    1225: 18047,  # globe
    1237: 18059,  # pain
    1253: 18075,  # cap
    1248: 18070,  # age
    1223: 18045,  # Jew
    1277: 18099,  # vocabulary
    1234: 18056,  # dialogue
    1272: 18094,  # project
    1278: 18100,  # list
    1261: 18083,  # weekend
    1267: 18089,  # matter
    1242: 18064,  # pear
    1239: 18061,  # positive
    1230: 18052,  # hallway
    1274: 18096,  # enemy
    1264: 18086,  # schoolbag
}

# 创建报告文件
report_file = f"fix_alan_error_logs_report_{current_time}.txt"
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), report_file)

try:
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 打开报告文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("修复Alan错词记录报告\n")
        f.write("================\n\n")
        
        # 备份ErrorLogs表
        f.write("备份ErrorLogs表...\n")
        cursor.execute("CREATE TABLE IF NOT EXISTS ErrorLogs_Backup AS SELECT * FROM ErrorLogs")
        conn.commit()
        f.write("备份完成\n\n")
        
        # 查询Alan在2025-06-25的错词记录
        f.write("查询Alan在2025-06-25的错词记录（修复前）:\n")
        cursor.execute("""
            SELECT e.error_id, e.student_id, e.word_id, e.error_type, e.student_answer, e.error_date, w.spelling
            FROM ErrorLogs e
            LEFT JOIN Words w ON e.word_id = w.word_id
            WHERE e.student_id = 3 AND e.error_date = '2025-06-25'
        """)
        error_logs = cursor.fetchall()
        
        if error_logs:
            f.write(f"找到 {len(error_logs)} 条错词记录:\n")
            for log in error_logs:
                error_id, student_id, word_id, error_type, student_answer, error_date, spelling = log
                f.write(f"错误ID: {error_id}, 单词ID: {word_id}, 错误类型: {error_type}, ")
                f.write(f"学生答案: {student_answer}, 日期: {error_date}, 单词: {spelling or '未找到'}\n")
        else:
            f.write("未找到错词记录\n")
        
        f.write("\n")
        
        # 更新ErrorLogs表中的word_id
        f.write("更新ErrorLogs表中的word_id...\n")
        updated_count = 0
        for old_id, new_id in id_mapping.items():
            cursor.execute("""
                UPDATE ErrorLogs
                SET word_id = ?
                WHERE student_id = 3 AND error_date = '2025-06-25' AND word_id = ?
            """, (new_id, old_id))
            updated_count += cursor.rowcount
        
        conn.commit()
        f.write(f"更新了 {updated_count} 条记录\n\n")
        
        # 查询Alan在2025-06-25的错词记录（修复后）
        f.write("查询Alan在2025-06-25的错词记录（修复后）:\n")
        cursor.execute("""
            SELECT e.error_id, e.student_id, e.word_id, e.error_type, e.student_answer, e.error_date, w.spelling
            FROM ErrorLogs e
            LEFT JOIN Words w ON e.word_id = w.word_id
            WHERE e.student_id = 3 AND e.error_date = '2025-06-25'
        """)
        error_logs = cursor.fetchall()
        
        if error_logs:
            f.write(f"找到 {len(error_logs)} 条错词记录:\n")
            for log in error_logs:
                error_id, student_id, word_id, error_type, student_answer, error_date, spelling = log
                f.write(f"错误ID: {error_id}, 单词ID: {word_id}, 错误类型: {error_type}, ")
                f.write(f"学生答案: {student_answer}, 日期: {error_date}, 单词: {spelling or '未找到'}\n")
        else:
            f.write("未找到错词记录\n")
        
        f.write("\n")
        
        # 检查是否还有单词ID不存在于Words表中
        f.write("检查是否还有单词ID不存在于Words表中:\n")
        cursor.execute("""
            SELECT e.error_id, e.word_id
            FROM ErrorLogs e
            LEFT JOIN Words w ON e.word_id = w.word_id
            WHERE e.student_id = 3 AND e.error_date = '2025-06-25' AND w.word_id IS NULL
        """)
        missing_words = cursor.fetchall()
        
        if missing_words:
            f.write(f"发现 {len(missing_words)} 条记录的单词ID在Words表中不存在:\n")
            for error_id, word_id in missing_words:
                f.write(f"错误ID: {error_id}, 单词ID: {word_id}\n")
        else:
            f.write("所有单词ID都存在于Words表中\n")
        
        f.write("\n")
        
        # 总结
        f.write("总结:\n")
        f.write("1. 已备份ErrorLogs表到ErrorLogs_Backup\n")
        f.write(f"2. 已更新Alan在2025-06-25的 {updated_count} 条错词记录的word_id\n")
        if not missing_words:
            f.write("3. 所有错词记录现在都可以正确关联到Words表中的单词\n")
        else:
            f.write(f"3. 仍有 {len(missing_words)} 条记录无法关联到Words表中的单词\n")
        
        f.write("\n修复完成\n")
    
    print(f"报告已生成: {report_path}")

except sqlite3.Error as e:
    print(f"数据库错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    if 'conn' in locals():
        conn.close()