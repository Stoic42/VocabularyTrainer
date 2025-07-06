#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

OUTPUT_FILE = 'none_meaning_words.txt'

def export_none_meaning_words():
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 查找meaning_cn为None或空的单词
    cursor.execute("SELECT word_id, spelling, pos FROM Words WHERE meaning_cn IS NULL OR TRIM(meaning_cn) = ''")
    rows = cursor.fetchall()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('word_id\tspelling\tpos\n')
        for row in rows:
            word_id, spelling, pos = row
            f.write(f'{word_id}\t{spelling}\t{pos or ""}\n')
    
    print(f"导出完成，共 {len(rows)} 个单词释义为空，已保存到 {OUTPUT_FILE}")
    conn.close()

if __name__ == "__main__":
    export_none_meaning_words() 