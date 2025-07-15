import sqlite3

def fix_colour_labour_specific():
    """专门修复colour/color和labour/labor单词的数据"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 修复colour/color单词
    # 原始数据：colour /ˈkʌlə/n. 颜色　vt. 给…着色，涂色
    colour_data = {
        'spelling': 'colour/color',  # 已经正确
        'meaning_cn': 'n. 颜色　vt. 给…着色，涂色',  # 完整释义
        'pos': 'n./vt.',  # 词性
        'ipa': '/ˈkʌlə/'  # 音标
    }
    
    cursor.execute("""
        UPDATE Words SET 
            meaning_cn = ?,
            pos = ?,
            ipa = ?
        WHERE spelling = 'colour/color'
    """, (
        colour_data['meaning_cn'],
        colour_data['pos'],
        colour_data['ipa']
    ))
    
    if cursor.rowcount > 0:
        print("✓ colour/color单词修复成功！")
        print(f"  词义: {colour_data['meaning_cn']}")
        print(f"  词性: {colour_data['pos']}")
        print(f"  音标: {colour_data['ipa']}")
    else:
        print("✗ 未找到colour/color单词")
    
    # 修复labour/labor单词
    # 原始数据：
    # labour
    # /ˈleɪbə/
    # （美labor）n. 劳动，劳力
    # 记　联想记忆：旧时的港口（harbour）有很多劳力（labour）
    # 例　Building a house requires a lot of labour. 盖一栋房子需要大量的劳力。
    
    labour_data = {
        'spelling': 'labour/labor',  # 已经正确
        'meaning_cn': 'n. 劳动，劳力',  # 只保留词性和释义
        'pos': 'n.',  # 词性
        'exam_sentence': 'Building a house requires a lot of labour. 盖一栋房子需要大量的劳力。',  # 例句
        'mnemonic': '联想记忆：旧时的港口（harbour）有很多劳力（labour）',  # 记忆方法
        'ipa': '/ˈleɪbə/'  # 音标
    }
    
    cursor.execute("""
        UPDATE Words SET 
            meaning_cn = ?,
            pos = ?,
            exam_sentence = ?,
            mnemonic = ?,
            ipa = ?
        WHERE spelling = 'labour/labor'
    """, (
        labour_data['meaning_cn'],
        labour_data['pos'],
        labour_data['exam_sentence'],
        labour_data['mnemonic'],
        labour_data['ipa']
    ))
    
    if cursor.rowcount > 0:
        print("✓ labour/labor单词修复成功！")
        print(f"  词义: {labour_data['meaning_cn']}")
        print(f"  词性: {labour_data['pos']}")
        print(f"  例句: {labour_data['exam_sentence']}")
        print(f"  记忆: {labour_data['mnemonic']}")
        print(f"  音标: {labour_data['ipa']}")
    else:
        print("✗ 未找到labour/labor单词")
    
    # 检查修复结果
    print("\n=== 修复后的数据 ===")
    
    # 检查colour/color
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, ipa
        FROM Words 
        WHERE spelling = 'colour/color'
    """)
    colour_result = cursor.fetchone()
    if colour_result:
        word_id, spelling, meaning_cn, pos, ipa = colour_result
        print(f"colour/color:")
        print(f"  ID: {word_id}")
        print(f"  拼写: {spelling}")
        print(f"  词义: {meaning_cn}")
        print(f"  词性: {pos}")
        print(f"  音标: {ipa}")
    
    # 检查labour/labor
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, exam_sentence, mnemonic, ipa
        FROM Words 
        WHERE spelling = 'labour/labor'
    """)
    labour_result = cursor.fetchone()
    if labour_result:
        word_id, spelling, meaning_cn, pos, exam_sentence, mnemonic, ipa = labour_result
        print(f"\nlabour/labor:")
        print(f"  ID: {word_id}")
        print(f"  拼写: {spelling}")
        print(f"  词义: {meaning_cn}")
        print(f"  词性: {pos}")
        print(f"  例句: {exam_sentence}")
        print(f"  记忆: {mnemonic}")
        print(f"  音标: {ipa}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    fix_colour_labour_specific() 