from utils import get_database_connection, get_database_path
import sqlite3
import re
import requests
import time
import os

def extract_pos_from_meaning(meaning_cn):
    """从中文释义中提取词性"""
    if not meaning_cn:
        return None
    
    # 常见词性模式
    pos_patterns = [
        r'^([a-z]+\.)\s',  # n. adj. v. adv. prep. conj. pron. etc.
        r'^([a-z]+)\s',    # 没有点的词性
        r'（([a-z]+)）',   # 括号中的词性
        r'\[([a-z]+)\]',   # 方括号中的词性
    ]
    
    for pattern in pos_patterns:
        match = re.match(pattern, meaning_cn.lower())
        if match:
            pos = match.group(1)
            # 验证是否为有效词性
            valid_pos = ['n', 'v', 'adj', 'adv', 'prep', 'conj', 'pron', 'int', 'num', 'art', 'aux']
            if pos in valid_pos:
                return pos + "."
    
    return None

def get_pronunciation_from_api(word):
    """从API获取音标（这里使用模拟数据，实际应该调用真实的API）"""
    # 这里应该调用真实的词典API，比如Cambridge Dictionary API
    # 为了演示，我们返回一些模拟数据
    
    # 模拟一些常见单词的音标
    mock_pronunciations = {
        'shall': {'uk': '/ʃæl/', 'us': '/ʃæl/'},
        'would': {'uk': '/wʊd/', 'us': '/wʊd/'},
        'ought': {'uk': '/ɔːt/', 'us': '/ɔːt/'},
        'behaviour': {'uk': '/bɪˈheɪvjə(r)/', 'us': '/bɪˈheɪvjər/'},
        'neighbour': {'uk': '/ˈneɪbə(r)/', 'us': '/ˈneɪbər/'},
        'humour': {'uk': '/ˈhjuːmə(r)/', 'us': '/ˈhjuːmər/'},
        'honour': {'uk': '/ˈɒnə(r)/', 'us': '/ˈɑːnər/'},
        'favour': {'uk': '/ˈfeɪvə(r)/', 'us': '/ˈfeɪvər/'},
        'labour': {'uk': '/ˈleɪbə(r)/', 'us': '/ˈleɪbər/'},
        'programme': {'uk': '/ˈprəʊɡræm/', 'us': '/ˈproʊɡræm/'},
        'centre': {'uk': '/ˈsentə(r)/', 'us': '/ˈsentər/'},
        'metre': {'uk': '/ˈmiːtə(r)/', 'us': '/ˈmiːtər/'},
        'litre': {'uk': '/ˈliːtə(r)/', 'us': '/ˈliːtər/'},
        'kilometre': {'uk': '/ˈkɪləmiːtə(r)/', 'us': '/kɪˈlɑːmɪtər/'},
        'fibre': {'uk': '/ˈfaɪbə(r)/', 'us': '/ˈfaɪbər/'},
        'tyre': {'uk': '/ˈtaɪə(r)/', 'us': '/ˈtaɪər/'},
    }
    
    word_lower = word.lower()
    if word_lower in mock_pronunciations:
        return mock_pronunciations[word_lower]
    
    # 如果没有找到，返回None
    return None

def fix_missing_data():
    """修复数据库中缺少音标和词性的单词"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    print("🔧 开始修复数据库中缺少音标和词性的单词")
    print("=" * 80)
    
    # 查找需要修复的单词
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.audio_path_uk, w.audio_path_us
        FROM Words w
        WHERE (w.pos IS NULL OR w.pos = '' OR w.pos = 'N/A') 
           OR (w.audio_path_uk IS NULL OR w.audio_path_uk = '' OR w.audio_path_uk = 'N/A')
           OR (w.audio_path_us IS NULL OR w.audio_path_us = '' OR w.audio_path_us = 'N/A')
        ORDER BY w.spelling
    """)
    
    words = cursor.fetchall()
    
    if not words:
        print("✅ 没有发现需要修复的单词")
        return
    
    print(f"📝 发现 {len(words)} 个单词需要修复")
    print()
    
    # 统计修复结果
    fixed_pos = 0
    fixed_pronunciation = 0
    total_processed = 0
    
    for word in words:
        word_id, spelling, meaning_cn, pos, audio_uk, audio_us = word
        
        print(f"处理单词: {spelling} (ID: {word_id})")
        
        # 1. 修复词性
        if not pos or pos == '' or pos == 'N/A':
            extracted_pos = extract_pos_from_meaning(meaning_cn)
            if extracted_pos:
                cursor.execute("UPDATE Words SET pos = ? WHERE word_id = ?", (extracted_pos, word_id))
                print(f"  ✅ 修复词性: {extracted_pos}")
                fixed_pos += 1
            else:
                print(f"  ❌ 无法提取词性")
        
        # 2. 修复音标
        missing_uk = not audio_uk or audio_uk == '' or audio_uk == 'N/A'
        missing_us = not audio_us or audio_us == '' or audio_us == 'N/A'
        
        if missing_uk or missing_us:
            pronunciation = get_pronunciation_from_api(spelling)
            if pronunciation:
                updates = []
                params = []
                
                if missing_uk and pronunciation.get('uk'):
                    updates.append("audio_path_uk = ?")
                    params.append(pronunciation['uk'])
                
                if missing_us and pronunciation.get('us'):
                    updates.append("audio_path_us = ?")
                    params.append(pronunciation['us'])
                
                if updates:
                    params.append(word_id)
                    sql = f"UPDATE Words SET {', '.join(updates)} WHERE word_id = ?"
                    cursor.execute(sql, params)
                    print(f"  ✅ 修复音标: UK={pronunciation.get('uk', 'N/A')}, US={pronunciation.get('us', 'N/A')}")
                    fixed_pronunciation += 1
            else:
                print(f"  ❌ 无法获取音标")
        
        total_processed += 1
        
        # 每处理10个单词提交一次事务
        if total_processed % 10 == 0:
            conn.commit()
            print(f"  📊 已处理 {total_processed}/{len(words)} 个单词")
    
    # 最终提交
    conn.commit()
    
    print()
    print("📊 修复完成统计：")
    print(f"  总处理单词数: {total_processed}")
    print(f"  修复词性数: {fixed_pos}")
    print(f"  修复音标数: {fixed_pronunciation}")
    
    # 验证修复结果
    print()
    print("🔍 验证修复结果：")
    
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN pos IS NULL OR pos = '' OR pos = 'N/A' THEN 1 ELSE 0 END) as missing_pos,
               SUM(CASE WHEN audio_path_uk IS NULL OR audio_path_uk = '' OR audio_path_uk = 'N/A' THEN 1 ELSE 0 END) as missing_uk,
               SUM(CASE WHEN audio_path_us IS NULL OR audio_path_us = '' OR audio_path_us = 'N/A' THEN 1 ELSE 0 END) as missing_us
        FROM Words
    """)
    
    stats = cursor.fetchone()
    total_words = stats[0]
    missing_pos_count = stats[1]
    missing_uk_count = stats[2]
    missing_us_count = stats[3]
    
    print(f"  总单词数: {total_words}")
    print(f"  仍缺少词性的单词数: {missing_pos_count}")
    print(f"  仍缺少英式音标的单词数: {missing_uk_count}")
    print(f"  仍缺少美式音标的单词数: {missing_us_count}")
    
    print(f"  词性完整率: {((total_words - missing_pos_count) / total_words * 100):.1f}%")
    print(f"  英式音标完整率: {((total_words - missing_uk_count) / total_words * 100):.1f}%")
    print(f"  美式音标完整率: {((total_words - missing_us_count) / total_words * 100):.1f}%")
    
    conn.close()

if __name__ == "__main__":
    fix_missing_data() 