import sqlite3
import os

def get_db_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vocabulary.db'))

def check_colour_labour():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # 检查colour/color
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, derivatives, exam_sentence, mnemonic, collocation, tips
        FROM Words 
        WHERE spelling LIKE '%colour%' OR spelling LIKE '%color%'
    """)
    colour_results = cursor.fetchall()
    print("colour/color单词详细信息:")
    for row in colour_results:
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
    
    # 检查labour/labor
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, derivatives, exam_sentence, mnemonic, collocation, tips
        FROM Words 
        WHERE spelling LIKE '%labour%' OR spelling LIKE '%labor%'
    """)
    labour_results = cursor.fetchall()
    print("labour/labor单词详细信息:")
    for row in labour_results:
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
    
    conn.close()

if __name__ == '__main__':
    check_colour_labour() 