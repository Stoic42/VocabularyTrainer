import sqlite3

def restore_pity_junior_high():
    """恢复初中Unit 9的pity记录（word_id=17295）"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 根据原始数据，初中pity的正确信息应该是：
    # pity
    # ［ˈpiti］
    # n. / v. 同情，怜悯；可惜，遗憾
    # 搭 feel pity for... 为…感到可怜，怜悯…；What a pity! 真遗憾！
    
    # 正确的字段分配：
    correct_data = {
        'word_id': 17295,  # 恢复原来的word_id
        'spelling': 'pity',
        'meaning_cn': 'n. / v. 同情，怜悯；可惜，遗憾',  # 完整释义
        'pos': 'n./v.',  # 词性
        'collocation': 'feel pity for... 为…感到可怜，怜悯…；What a pity! 真遗憾！',  # 搭配
        'ipa': '［ˈpiti］',  # 音标
        'list_id': 205  # 初中Unit 9的list_id
    }
    
    # 检查word_id=17295是否已存在
    cursor.execute("SELECT word_id FROM Words WHERE word_id = ?", (17295,))
    existing = cursor.fetchone()
    
    if existing:
        print("word_id=17295已存在，更新内容...")
        cursor.execute("""
            UPDATE Words SET 
                spelling = ?,
                meaning_cn = ?,
                pos = ?,
                collocation = ?,
                ipa = ?,
                list_id = ?
            WHERE word_id = ?
        """, (
            correct_data['spelling'],
            correct_data['meaning_cn'],
            correct_data['pos'],
            correct_data['collocation'],
            correct_data['ipa'],
            correct_data['list_id'],
            correct_data['word_id']
        ))
    else:
        print("插入word_id=17295的新记录...")
        cursor.execute("""
            INSERT INTO Words (
                word_id, spelling, meaning_cn, pos, collocation, ipa, list_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            correct_data['word_id'],
            correct_data['spelling'],
            correct_data['meaning_cn'],
            correct_data['pos'],
            correct_data['collocation'],
            correct_data['ipa'],
            correct_data['list_id']
        ))
    
    if cursor.rowcount > 0:
        print("✓ 初中Unit 9的pity记录恢复成功！")
        print(f"  word_id: {correct_data['word_id']}")
        print(f"  词义: {correct_data['meaning_cn']}")
        print(f"  词性: {correct_data['pos']}")
        print(f"  搭配: {correct_data['collocation']}")
        print(f"  音标: {correct_data['ipa']}")
        print(f"  list_id: {correct_data['list_id']} (初中Unit 9)")
    else:
        print("✗ 恢复失败")
    
    # 检查恢复结果
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.collocation, w.ipa,
               w.list_id, wl.list_name, b.book_name
        FROM Words w
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE w.word_id = ?
    """, (17295,))
    
    result = cursor.fetchone()
    if result:
        word_id, spelling, meaning_cn, pos, collocation, ipa, list_id, list_name, book_name = result
        print(f"\n恢复后的数据:")
        print(f"word_id: {word_id}")
        print(f"拼写: {spelling}")
        print(f"词义: {meaning_cn}")
        print(f"词性: {pos}")
        print(f"搭配: {collocation}")
        print(f"音标: {ipa}")
        print(f"词表: {list_name} (ID: {list_id})")
        print(f"词书: {book_name}")
    
    # 检查ErrorLogs关联
    cursor.execute("""
        SELECT el.error_id, el.student_id, el.word_id, el.error_type, el.error_date,
               u.username
        FROM ErrorLogs el
        JOIN Users u ON el.student_id = u.id
        WHERE el.word_id = ?
        ORDER BY el.error_date DESC
    """, (17295,))
    
    error_logs = cursor.fetchall()
    if error_logs:
        print(f"\n✓ 找到 {len(error_logs)} 条关联的错误记录:")
        for error in error_logs:
            error_id, student_id, word_id, error_type, error_date, username = error
            print(f"  用户: {username}, 错误ID: {error_id}, 错误类型: {error_type}, 时间: {error_date}")
    else:
        print("\n⚠ 未找到关联的错误记录")
    
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
    restore_pity_junior_high() 