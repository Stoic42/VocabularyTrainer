#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import get_database_connection, get_database_path
import sqlite3

def check_specific_words():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # 检查content单词
    cursor.execute("SELECT word_id, spelling, pos, meaning_cn, mnemonic, collocation, tips, comparison, derivatives, exam_sentence FROM Words WHERE spelling = 'content'")
    content_word = cursor.fetchone()
    
    print("=== content 单词状态 ===")
    if content_word:
        word_id, spelling, pos, meaning_cn, mnemonic, collocation, tips, comparison, derivatives, exam_sentence = content_word
        print(f"word_id: {word_id}")
        print(f"spelling: {spelling}")
        print(f"pos: {pos}")
        print(f"meaning_cn: {meaning_cn}")
        print(f"mnemonic: {mnemonic}")
        print(f"collocation: {collocation}")
        print(f"tips: {tips}")
        print(f"comparison: {comparison}")
        print(f"derivatives: {derivatives}")
        print(f"exam_sentence: {exam_sentence}")
    else:
        print("未找到content单词")
    
    print("\n=== forgivee 单词状态 ===")
    cursor.execute("SELECT word_id, spelling, pos, meaning_cn FROM Words WHERE spelling = 'forgivee'")
    forgivee_word = cursor.fetchone()
    
    if forgivee_word:
        word_id, spelling, pos, meaning_cn = forgivee_word
        print(f"word_id: {word_id}")
        print(f"spelling: {spelling}")
        print(f"pos: {pos}")
        print(f"meaning_cn: {meaning_cn}")
    else:
        print("未找到forgivee单词")
    
    # 检查是否有forgive单词
    print("\n=== forgive 单词状态 ===")
    cursor.execute("SELECT word_id, spelling, pos, meaning_cn FROM Words WHERE spelling = 'forgive'")
    forgive_word = cursor.fetchone()
    
    if forgive_word:
        word_id, spelling, pos, meaning_cn = forgive_word
        print(f"word_id: {word_id}")
        print(f"spelling: {spelling}")
        print(f"pos: {pos}")
        print(f"meaning_cn: {meaning_cn}")
    else:
        print("未找到forgive单词")
    
    conn.close()

if __name__ == "__main__":
    check_specific_words() 