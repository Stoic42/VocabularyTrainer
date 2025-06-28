import sqlite3
import sys
import os
from datetime import datetime

# 设置输出编码，避免中文显示问题
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# 创建输出文件
output_dir = 'd:/Projects/VocabularyTrainer/Alan/reports'
os.makedirs(output_dir, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = os.path.join(output_dir, f'alan_error_report_{timestamp}.txt')

# 打开文件进行写入
with open(output_file, 'w', encoding='utf-8') as f:
    # 连接到数据库
    conn = sqlite3.connect('d:/Projects/VocabularyTrainer/vocabulary.db')
    # conn = sqlite3.connect('d:/Projects/LumiCamp_for_Alan/vocabulary.db')
    cursor = conn.cursor()
    
    # 按日期分组统计错词数量
    cursor.execute("""
    SELECT e.error_date, COUNT(*) as error_count
    FROM ErrorLogs e
    WHERE e.student_id = 1
    AND e.error_date BETWEEN '2025-06-25' AND '2025-06-28'
    GROUP BY e.error_date
    ORDER BY e.error_date
    """)
    
    date_stats = cursor.fetchall()
    
    f.write('\n' + '='*50 + '\n')
    f.write('Alan的错词统计(按日期)\n')
    f.write('='*50 + '\n')
    f.write('{:<12}\t{:<8}\n'.format('日期', '错误数'))
    f.write('-'*30 + '\n')
    for stat in date_stats:
        f.write('{:<12}\t{:<8}\n'.format(stat[0], stat[1]))
    
    # 查询总体错词统计
    cursor.execute("""
    SELECT COUNT(*) as total_errors, 
           COUNT(DISTINCT w.word_id) as unique_words,
           COUNT(DISTINCT w.list_id) as unique_units
    FROM ErrorLogs e 
    JOIN Words w ON e.word_id = w.word_id 
    WHERE e.student_id = 1 
    AND e.error_date BETWEEN '2025-06-25' AND '2025-06-28'
    """)
    
    total_stats = cursor.fetchone()
    
    f.write('\n' + '='*50 + '\n')
    f.write('Alan的总体错词统计(2025-06-25至2025-06-28)\n')
    f.write('='*50 + '\n')
    f.write(f'总错词数: {total_stats[0]}\n')
    f.write(f'不同单词数: {total_stats[1]}\n')
    f.write(f'涉及单元数: {total_stats[2]}\n')
    
    # 查询每个日期的错词记录（每天前5条）
    for date in ['2025-06-25', '2025-06-26', '2025-06-27']:
        cursor.execute("""
        SELECT e.error_id, e.word_id, w.spelling, w.list_id, wl.list_name, b.book_name, e.error_date, e.error_type, e.student_answer 
        FROM ErrorLogs e 
        JOIN Words w ON e.word_id = w.word_id 
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = 1 
        AND e.error_date = ? 
        ORDER BY e.error_id
        LIMIT 5
        """, (date,))
        
        rows = cursor.fetchall()
        
        f.write('\n' + '='*50 + '\n')
        f.write(f'Alan在{date}的部分错词记录(前5条)\n')
        f.write('='*50 + '\n')
        if rows:
            f.write('{:<5}\t{:<8}\t{:<12}\t{:<8}\t{:<15}\t{:<15}\t{:<12}\t{:<12}\t{:<15}\n'.format(
                'ID', '单词ID', '单词', '列表ID', '列表名称', '词书', '日期', '错误类型', '学生答案'))
            f.write('-'*120 + '\n')
            for row in rows:
                # 确保列表名称有足够的空间显示
                list_name = row[4] if row[4] else 'N/A'
                list_name_display = list_name if len(list_name) < 12 else list_name[:11] + '...'
                
                # 确保单词有足够的空间显示
                word = row[2] if len(row[2]) < 10 else row[2][:9] + '...'
                
                # 确保词书名称有足够的空间显示
                book_name = row[5] if row[5] else 'N/A'
                book_name_display = book_name if len(book_name) < 12 else book_name[:11] + '...'
                
                f.write('{:<5}\t{:<8}\t{:<12}\t{:<8}\t{:<15}\t{:<15}\t{:<12}\t{:<12}\t{:<15}\n'.format(
                    row[0], row[1], word, row[3], list_name_display, book_name_display, row[6], row[7], row[8]))
        else:
            f.write(f'没有找到{date}的错词记录\n')
    
    # 查询每个日期的错词单元分布
    for date in ['2025-06-25', '2025-06-26', '2025-06-27']:
        cursor.execute("""
        SELECT wl.list_name, b.book_name, COUNT(*) as error_count, COUNT(DISTINCT w.word_id) as unique_words
        FROM ErrorLogs e 
        JOIN Words w ON e.word_id = w.word_id 
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE e.student_id = 1 
        AND e.error_date = ? 
        GROUP BY wl.list_name
        ORDER BY error_count DESC
        """, (date,))
        
        unit_stats = cursor.fetchall()
        
        f.write('\n' + '='*50 + '\n')
        f.write(f'Alan在{date}的错词单元分布\n')
        f.write('='*50 + '\n')
        if unit_stats:
            f.write('{:<15}\t{:<15}\t{:<10}\t{:<10}\n'.format('单元名称', '词书', '错误数', '不同单词数'))
            f.write('-'*60 + '\n')
            for stat in unit_stats:
                list_name = stat[0] if stat[0] else 'Unknown'
                book_name = stat[1] if stat[1] else 'Unknown'
                book_name_display = book_name if len(book_name) < 12 else book_name[:11] + '...'
                
                f.write('{:<15}\t{:<15}\t{:<10}\t{:<10}\n'.format(
                    list_name, book_name_display, stat[2], stat[3]))
        else:
            f.write(f'没有找到{date}的错词单元分布\n')
    
    # 查询最常见的错词（出现次数最多的前10个）
    cursor.execute("""
    SELECT w.spelling, wl.list_name, COUNT(*) as error_count
    FROM ErrorLogs e 
    JOIN Words w ON e.word_id = w.word_id 
    LEFT JOIN WordLists wl ON w.list_id = wl.list_id
    WHERE e.student_id = 1 
    AND e.error_date BETWEEN '2025-06-25' AND '2025-06-28'
    GROUP BY w.word_id
    ORDER BY error_count DESC
    LIMIT 10
    """)
    
    top_errors = cursor.fetchall()
    
    f.write('\n' + '='*50 + '\n')
    f.write('Alan的最常见错词(Top 10)\n')
    f.write('='*50 + '\n')
    if top_errors:
        f.write('{:<15}\t{:<15}\t{:<10}\n'.format('单词', '单元', '错误次数'))
        f.write('-'*50 + '\n')
        for error in top_errors:
            word = error[0] if len(error[0]) < 12 else error[0][:11] + '...'
            list_name = error[1] if error[1] else 'Unknown'
            
            f.write('{:<15}\t{:<15}\t{:<10}\n'.format(word, list_name, error[2]))
    else:
        f.write('没有找到错词记录\n')
    
    conn.close()

print(f'\n报告已生成: {output_file}')