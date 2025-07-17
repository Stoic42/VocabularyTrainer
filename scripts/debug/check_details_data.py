from utils import get_database_connection, get_database_path
import sqlite3

def check_details_data():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # 检查总单词数和有详细信息的单词数
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN derivatives IS NOT NULL AND derivatives != '' THEN 1 END) as has_derivatives,
            COUNT(CASE WHEN root_etymology IS NOT NULL AND root_etymology != '' THEN 1 END) as has_etymology,
            COUNT(CASE WHEN mnemonic IS NOT NULL AND mnemonic != '' THEN 1 END) as has_mnemonic,
            COUNT(CASE WHEN comparison IS NOT NULL AND comparison != '' THEN 1 END) as has_comparison,
            COUNT(CASE WHEN collocation IS NOT NULL AND collocation != '' THEN 1 END) as has_collocation,
            COUNT(CASE WHEN exam_sentence IS NOT NULL AND exam_sentence != '' THEN 1 END) as has_exam_sentence,
            COUNT(CASE WHEN tips IS NOT NULL AND tips != '' THEN 1 END) as has_tips
        FROM Words
    ''')
    
    stats = cursor.fetchone()
    print("=== 详细信息字段统计 ===")
    print(f"总单词数: {stats[0]}")
    print(f"有派生词: {stats[1]}")
    print(f"有词源: {stats[2]}")
    print(f"有联想记忆: {stats[3]}")
    print(f"有词义辨析: {stats[4]}")
    print(f"有搭配用法: {stats[5]}")
    print(f"有真题例句: {stats[6]}")
    print(f"有提示: {stats[7]}")
    
    # 检查一些示例单词
    print("\n=== 示例单词详细信息 ===")
    cursor.execute('''
        SELECT spelling, derivatives, root_etymology, mnemonic, comparison, collocation, exam_sentence, tips
        FROM Words 
        WHERE derivatives IS NOT NULL AND derivatives != ''
           OR root_etymology IS NOT NULL AND root_etymology != ''
           OR mnemonic IS NOT NULL AND mnemonic != ''
        LIMIT 5
    ''')
    
    examples = cursor.fetchall()
    if examples:
        for word in examples:
            print(f"\n单词: {word[0]}")
            if word[1]: print(f"  派生词: {word[1]}")
            if word[2]: print(f"  词源: {word[2]}")
            if word[3]: print(f"  联想记忆: {word[3]}")
            if word[4]: print(f"  词义辨析: {word[4]}")
            if word[5]: print(f"  搭配用法: {word[5]}")
            if word[6]: print(f"  真题例句: {word[6]}")
            if word[7]: print(f"  提示: {word[7]}")
    else:
        print("没有找到任何有详细信息的单词")
    
    # 检查随机几个单词的详细信息
    print("\n=== 随机单词详细信息检查 ===")
    cursor.execute('''
        SELECT spelling, derivatives, root_etymology, mnemonic, comparison, collocation, exam_sentence, tips
        FROM Words 
        ORDER BY RANDOM()
        LIMIT 3
    ''')
    
    random_words = cursor.fetchall()
    for word in random_words:
        print(f"\n单词: {word[0]}")
        print(f"  派生词: {word[1] or '无'}")
        print(f"  词源: {word[2] or '无'}")
        print(f"  联想记忆: {word[3] or '无'}")
        print(f"  词义辨析: {word[4] or '无'}")
        print(f"  搭配用法: {word[5] or '无'}")
        print(f"  真题例句: {word[6] or '无'}")
        print(f"  提示: {word[7] or '无'}")
    
    conn.close()

if __name__ == "__main__":
    check_details_data() 