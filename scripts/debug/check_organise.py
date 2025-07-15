import sqlite3
import os

def get_db_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vocabulary.db'))

def check_organise_word():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # 查询organise单词
    cursor.execute("SELECT word_id, spelling, meaning_cn, pos, derivatives FROM Words WHERE spelling = 'organise'")
    result = cursor.fetchall()
    
    print('organise单词数据:')
    for row in result:
        print(f'ID: {row[0]}')
        print(f'拼写: {row[1]}')
        print(f'词义: {row[2]}')
        print(f'词性: {row[3]}')
        print(f'派生词: {row[4]}')
        print('---')
    
    # 查询类似的单词，看看是否有同样的问题
    cursor.execute("SELECT word_id, spelling, meaning_cn FROM Words WHERE meaning_cn LIKE '%参%' OR meaning_cn LIKE '%organisation%' OR meaning_cn LIKE '%例%' LIMIT 15")
    similar_results = cursor.fetchall()
    
    print('\n类似的单词（可能有问题）:')
    for row in similar_results:
        print(f'ID: {row[0]}, 拼写: {row[1]}')
        print(f'词义: {row[2]}')
        print('---')
    
    # 检查高中词书中所有单词的词义格式
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn, w.pos 
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE b.book_name = '高中英语词汇'
        AND (w.meaning_cn LIKE '%例%' OR w.meaning_cn LIKE '%参%' OR w.meaning_cn LIKE '%考%')
        LIMIT 10
    """)
    problematic_words = cursor.fetchall()
    
    print('\n高中词书中有问题的单词:')
    for row in problematic_words:
        print(f'ID: {row[0]}, 拼写: {row[1]}')
        print(f'词义: {row[2]}')
        print(f'词性: {row[3]}')
        print('---')
    
    conn.close()

if __name__ == '__main__':
    check_organise_word() 