import sqlite3

def fix_pity_specific():
    """专门修复pity单词的数据"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 根据原始数据，pity的正确信息应该是：
    # pity
    # ［ˈpiti］
    # n. / v. 同情，怜悯；可惜，遗憾
    # 搭 feel pity for... 为…感到可怜，怜悯…；What a pity! 真遗憾！
    
    # 正确的字段分配：
    correct_data = {
        'spelling': 'pity',
        'meaning_cn': 'n. / v. 同情，怜悯；可惜，遗憾',  # 完整释义
        'pos': 'n./v.',  # 词性
        'collocation': 'feel pity for... 为…感到可怜，怜悯…；What a pity! 真遗憾！',  # 搭配
        'ipa': '［ˈpiti］'  # 音标
    }
    
    # 先删除重复的记录，保留ID较小的那个
    cursor.execute("SELECT word_id FROM Words WHERE spelling = 'pity' ORDER BY word_id")
    pity_records = cursor.fetchall()
    
    if len(pity_records) > 1:
        # 删除ID较大的记录
        for record in pity_records[1:]:
            cursor.execute("DELETE FROM Words WHERE word_id = ?", (record[0],))
            print(f"删除重复记录: ID {record[0]}")
    
    # 更新pity单词
    cursor.execute("""
        UPDATE Words SET 
            meaning_cn = ?,
            pos = ?,
            collocation = ?,
            ipa = ?
        WHERE spelling = 'pity'
    """, (
        correct_data['meaning_cn'],
        correct_data['pos'],
        correct_data['collocation'],
        correct_data['ipa']
    ))
    
    if cursor.rowcount > 0:
        print("✓ pity单词修复成功！")
        print(f"  词义: {correct_data['meaning_cn']}")
        print(f"  词性: {correct_data['pos']}")
        print(f"  搭配: {correct_data['collocation']}")
        print(f"  音标: {correct_data['ipa']}")
    else:
        print("✗ 未找到pity单词")
    
    # 检查修复结果
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, collocation, ipa
        FROM Words 
        WHERE spelling = 'pity'
    """)
    
    result = cursor.fetchone()
    if result:
        word_id, spelling, meaning_cn, pos, collocation, ipa = result
        print(f"\n修复后的数据:")
        print(f"ID: {word_id}")
        print(f"拼写: {spelling}")
        print(f"词义: {meaning_cn}")
        print(f"词性: {pos}")
        print(f"搭配: {collocation}")
        print(f"音标: {ipa}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    fix_pity_specific() 