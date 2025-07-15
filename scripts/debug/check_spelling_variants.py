import sqlite3
import re
import os

def get_db_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vocabulary.db'))

def check_spelling_variants():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # 检查拼写变体表
    cursor.execute("SELECT * FROM SpellingVariants LIMIT 10")
    variants = cursor.fetchall()
    print("拼写变体表示例:")
    for variant in variants:
        print(f"ID: {variant[0]}, 单词ID: {variant[1]}, 变体: {variant[2]}, 主要: {variant[3]}")
    
    # 检查包含斜杠的spelling字段
    cursor.execute("SELECT word_id, spelling, meaning_cn FROM Words WHERE spelling LIKE '%/%' LIMIT 10")
    combined_words = cursor.fetchall()
    print("\n组合拼写单词示例:")
    for word in combined_words:
        print(f"ID: {word[0]}, 拼写: {word[1]}")
        print(f"词义: {word[2]}")
        print("---")
    
    # 检查organise相关的单词
    cursor.execute("SELECT word_id, spelling, meaning_cn FROM Words WHERE spelling LIKE '%organise%' OR spelling LIKE '%organize%'")
    organise_words = cursor.fetchall()
    print("\norganise相关单词:")
    for word in organise_words:
        print(f"ID: {word[0]}, 拼写: {word[1]}")
        print(f"词义: {word[2]}")
        print("---")
    
    conn.close()

if __name__ == '__main__':
    check_spelling_variants() 