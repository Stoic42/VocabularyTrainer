import sqlite3

def fix_pity_meaning_display():
    """修复pity单词的meaning_cn字段，将词性信息分离"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 修复初中Unit 9的pity记录（word_id=17295）
    cursor.execute("""
        UPDATE Words SET 
            meaning_cn = '同情，怜悯；可惜，遗憾',
            pos = 'n./v.'
        WHERE word_id = 17295
    """)
    
    if cursor.rowcount > 0:
        print("✓ 初中Unit 9的pity记录修复成功！")
        print("  词义: 同情，怜悯；可惜，遗憾")
        print("  词性: n./v.")
    else:
        print("✗ 修复失败")
    
    # 检查修复结果
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, list_id
        FROM Words 
        WHERE word_id = 17295
    """)
    
    result = cursor.fetchone()
    if result:
        word_id, spelling, meaning_cn, pos, list_id = result
        print(f"\n修复后的数据:")
        print(f"word_id: {word_id}")
        print(f"拼写: {spelling}")
        print(f"词义: {meaning_cn}")
        print(f"词性: {pos}")
        print(f"list_id: {list_id}")
    
    # 检查所有pity记录
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.list_id, wl.list_name, b.book_name
        FROM Words w
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE w.spelling = 'pity'
        ORDER BY w.word_id
    """)
    
    all_pity = cursor.fetchall()
    print(f"\n=== 所有pity记录 ({len(all_pity)}条) ===")
    for pity in all_pity:
        word_id, spelling, meaning_cn, pos, list_id, list_name, book_name = pity
        print(f"word_id: {word_id}, 词表: {list_name}, 词书: {book_name}")
        print(f"  词义: {meaning_cn}")
        print(f"  词性: {pos}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    fix_pity_meaning_display() 