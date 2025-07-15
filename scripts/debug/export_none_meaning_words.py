#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys

# 添加scripts目录到Python路径，确保能导入utils模块
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.dirname(current_dir)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from utils import get_database_path

def export_none_meaning_words():
    # 获取数据库路径
    db_path = get_database_path()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, 'none_meaning_words.txt')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查找meaning_cn为None或空的单词
    cursor.execute("SELECT word_id, spelling, pos FROM Words WHERE meaning_cn IS NULL OR TRIM(meaning_cn) = ''")
    rows = cursor.fetchall()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('word_id\tspelling\tpos\n')
        for row in rows:
            word_id, spelling, pos = row
            f.write(f'{word_id}\t{spelling}\t{pos or ""}\n')
    
    print(f"导出完成，共 {len(rows)} 个单词释义为空，已保存到 {output_file}")
    conn.close()

if __name__ == "__main__":
    export_none_meaning_words() 