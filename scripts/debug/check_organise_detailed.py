import sqlite3
import os

def get_db_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vocabulary.db'))

def check_organise_detailed():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # 检查organise/organize单词的详细信息
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, derivatives, exam_sentence, mnemonic, collocation, tips
        FROM Words 
        WHERE spelling LIKE '%organise%' OR spelling LIKE '%organize%'
    """)
    
    results = cursor.fetchall()
    print("organise/organize单词详细信息:")
    for row in results:
        word_id, spelling, meaning_cn, pos, derivatives, exam_sentence, mnemonic, collocation, tips = row
        print(f"ID: {word_id}")
        print(f"拼写: {spelling}")
        print(f"词义: {meaning_cn}")
        print(f"词性: {pos}")
        print(f"派生词: {derivatives}")
        print(f"例句: {exam_sentence}")
        print(f"记忆: {mnemonic}")
        print(f"搭配: {collocation}")
        print(f"提示: {tips}")
        print("---")
    
    # 检查拼写变体表
    cursor.execute("""
        SELECT sv.*, w.spelling as word_spelling
        FROM SpellingVariants sv
        JOIN Words w ON sv.word_id = w.word_id
        WHERE sv.spelling_variant IN ('organise', 'organize')
    """)
    
    variants = cursor.fetchall()
    print("拼写变体表记录:")
    for variant in variants:
        print(f"变体ID: {variant[0]}, 单词ID: {variant[1]}, 变体: {variant[2]}, 主要: {variant[3]}, 单词拼写: {variant[4]}")
    
    conn.close()

if __name__ == '__main__':
    check_organise_detailed() 