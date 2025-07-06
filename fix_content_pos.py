#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def fix_content_pos():
    """修正content单词的词性"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    print("正在修正content单词的词性...")
    
    # 根据词书原件，content的正确词性应该是：
    correct_pos = 'adj. 满意的；n. 内容；含量'
    correct_meaning = 'adj. 满意的；n. 内容；含量'
    
    cursor.execute("""
        UPDATE Words SET 
            pos = ?,
            meaning_cn = ?
        WHERE spelling = 'content'
    """, (correct_pos, correct_meaning))
    
    print("content单词词性修正完成")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_content_pos() 