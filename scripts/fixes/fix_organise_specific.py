import sqlite3

def fix_organise_specific():
    """专门修复organise单词的数据"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 根据原始数据，organise的正确信息应该是：
    # 原始数据：
    # organise
    # /ˈɔːɡənaɪz/
    # （美organize）v. 组织
    # 例　I'm organising the evening party. 我正在筹备晚会。
    # 参　organisation（n. 组织）；organiser（n. 组织者，创办者）
    
    # 正确的字段分配：
    correct_data = {
        'spelling': 'organise/organize',  # 已经正确
        'meaning_cn': 'v. 组织',  # 只保留词性和释义
        'pos': 'v.',  # 词性
        'exam_sentence': 'I\'m organising the evening party. 我正在筹备晚会。',  # 例句
        'derivatives': 'organisation（n. 组织）；organiser（n. 组织者，创办者）',  # 派生词
        'ipa': '/ˈɔːɡənaɪz/'  # 音标
    }
    
    # 更新organise单词
    cursor.execute("""
        UPDATE Words SET 
            meaning_cn = ?,
            pos = ?,
            exam_sentence = ?,
            derivatives = ?,
            ipa = ?
        WHERE spelling = 'organise/organize'
    """, (
        correct_data['meaning_cn'],
        correct_data['pos'],
        correct_data['exam_sentence'],
        correct_data['derivatives'],
        correct_data['ipa']
    ))
    
    if cursor.rowcount > 0:
        print("✓ organise单词修复成功！")
        print(f"  词义: {correct_data['meaning_cn']}")
        print(f"  词性: {correct_data['pos']}")
        print(f"  例句: {correct_data['exam_sentence']}")
        print(f"  派生词: {correct_data['derivatives']}")
        print(f"  音标: {correct_data['ipa']}")
    else:
        print("✗ 未找到organise/organize单词")
    
    # 检查修复结果
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos, derivatives, exam_sentence, ipa
        FROM Words 
        WHERE spelling = 'organise/organize'
    """)
    
    result = cursor.fetchone()
    if result:
        word_id, spelling, meaning_cn, pos, derivatives, exam_sentence, ipa = result
        print(f"\n修复后的数据:")
        print(f"ID: {word_id}")
        print(f"拼写: {spelling}")
        print(f"词义: {meaning_cn}")
        print(f"词性: {pos}")
        print(f"派生词: {derivatives}")
        print(f"例句: {exam_sentence}")
        print(f"音标: {ipa}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    fix_organise_specific() 