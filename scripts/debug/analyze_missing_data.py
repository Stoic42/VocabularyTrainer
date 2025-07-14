from utils import get_database_connection, get_database_path
import sqlite3
import re

def analyze_missing_data():
    """详细分析数据库中缺少音标和词性的单词"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    print("🔍 详细分析数据库中缺少音标和词性的单词")
    print("=" * 80)
    
    # 1. 查找类似"shall"的单词（缺少音标和词性）
    print("1️⃣ 查找类似'shall'的单词（缺少音标和词性）：")
    print("-" * 60)
    
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.audio_path_uk, w.audio_path_us,
               wl.list_name, b.book_name
        FROM Words w
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE (w.pos IS NULL OR w.pos = '' OR w.pos = 'N/A') 
           AND (w.audio_path_uk IS NULL OR w.audio_path_uk = '' OR w.audio_path_uk = 'N/A')
           AND (w.audio_path_us IS NULL OR w.audio_path_us = '' OR w.audio_path_us = 'N/A')
        ORDER BY b.book_name, wl.list_name, w.spelling
        LIMIT 50
    """)
    
    missing_both = cursor.fetchall()
    
    if missing_both:
        print(f"发现 {len(missing_both)} 个单词同时缺少音标和词性：")
        print(f"{'ID':<6} {'单词':<15} {'单元':<20} {'词书':<15} {'释义':<30}")
        print("-" * 80)
        
        for word in missing_both[:20]:  # 只显示前20个
            word_id, spelling, meaning_cn, pos, audio_uk, audio_us, list_name, book_name = word
            meaning_short = meaning_cn[:25] + "..." if len(meaning_cn) > 25 else meaning_cn
            print(f"{word_id:<6} {spelling:<15} {list_name:<20} {book_name:<15} {meaning_short:<30}")
        
        if len(missing_both) > 20:
            print(f"... 还有 {len(missing_both) - 20} 个单词")
    else:
        print("✅ 没有发现同时缺少音标和词性的单词")
    
    # 2. 分析词性缺失的情况
    print(f"\n2️⃣ 词性缺失分析：")
    print("-" * 60)
    
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN pos IS NULL OR pos = '' OR pos = 'N/A' THEN 1 ELSE 0 END) as missing_pos
        FROM Words
    """)
    
    pos_stats = cursor.fetchone()
    total_words = pos_stats[0]
    missing_pos_count = pos_stats[1]
    
    print(f"总单词数: {total_words}")
    print(f"缺少词性的单词数: {missing_pos_count}")
    print(f"词性完整率: {((total_words - missing_pos_count) / total_words * 100):.1f}%")
    
    # 3. 分析音标缺失的情况
    print(f"\n3️⃣ 音标缺失分析：")
    print("-" * 60)
    
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN audio_path_uk IS NULL OR audio_path_uk = '' OR audio_path_uk = 'N/A' THEN 1 ELSE 0 END) as missing_uk,
               SUM(CASE WHEN audio_path_us IS NULL OR audio_path_us = '' OR audio_path_us = 'N/A' THEN 1 ELSE 0 END) as missing_us
        FROM Words
    """)
    
    audio_stats = cursor.fetchone()
    missing_uk_count = audio_stats[1]
    missing_us_count = audio_stats[2]
    
    print(f"缺少英式音标的单词数: {missing_uk_count}")
    print(f"缺少美式音标的单词数: {missing_us_count}")
    print(f"英式音标完整率: {((total_words - missing_uk_count) / total_words * 100):.1f}%")
    print(f"美式音标完整率: {((total_words - missing_us_count) / total_words * 100):.1f}%")
    
    # 4. 按词书分析
    print(f"\n4️⃣ 按词书分析：")
    print("-" * 60)
    
    cursor.execute("""
        SELECT b.book_name,
               COUNT(*) as total_words,
               SUM(CASE WHEN w.pos IS NULL OR w.pos = '' OR w.pos = 'N/A' THEN 1 ELSE 0 END) as missing_pos,
               SUM(CASE WHEN w.audio_path_uk IS NULL OR w.audio_path_uk = '' OR w.audio_path_uk = 'N/A' THEN 1 ELSE 0 END) as missing_uk,
               SUM(CASE WHEN w.audio_path_us IS NULL OR w.audio_path_us = '' OR w.audio_path_us = 'N/A' THEN 1 ELSE 0 END) as missing_us
        FROM Words w
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        GROUP BY b.book_name
        ORDER BY total_words DESC
    """)
    
    book_stats = cursor.fetchall()
    
    print(f"{'词书名称':<15} {'总单词数':<10} {'缺词性':<8} {'缺英音':<8} {'缺美音':<8}")
    print("-" * 60)
    
    for book in book_stats:
        book_name, total, missing_pos, missing_uk, missing_us = book
        print(f"{book_name:<15} {total:<10} {missing_pos:<8} {missing_uk:<8} {missing_us:<8}")
    
    # 5. 提供具体的填充建议
    print(f"\n5️⃣ 具体填充建议：")
    print("-" * 60)
    
    # 查找一些有完整meaning_cn的单词作为示例
    cursor.execute("""
        SELECT spelling, meaning_cn, pos
        FROM Words 
        WHERE meaning_cn IS NOT NULL AND meaning_cn != '' 
        AND (pos IS NULL OR pos = '' OR pos = 'N/A')
        LIMIT 10
    """)
    
    examples = cursor.fetchall()
    
    if examples:
        print("词性提取示例：")
        for spelling, meaning_cn, pos in examples:
            # 尝试提取词性
            pos_match = re.match(r'^([a-z]+\.)\s', meaning_cn.lower())
            if pos_match:
                extracted_pos = pos_match.group(1)
                remaining_meaning = meaning_cn[len(extracted_pos):].strip()
                print(f"单词: {spelling}")
                print(f"  原始释义: {meaning_cn}")
                print(f"  提取词性: {extracted_pos}")
                print(f"  剩余释义: {remaining_meaning}")
                print()
    
    # 6. 创建修复脚本的建议
    print("6️⃣ 修复脚本建议：")
    print("-" * 60)
    print("建议创建以下脚本：")
    print("1. extract_pos_from_meaning.py - 从meaning_cn提取词性")
    print("2. fetch_pronunciation.py - 获取音标信息")
    print("3. batch_update_database.py - 批量更新数据库")
    print("4. data_quality_check.py - 数据质量检查")
    
    # 7. 优先级建议
    print(f"\n7️⃣ 处理优先级建议：")
    print("-" * 60)
    print("高优先级：")
    print("  - 高中英语词汇中缺少词性的35个单词")
    print("  - 初中英语词汇中缺少词性的1个单词")
    print("  - 高频词汇的音标补充")
    
    print("\n中优先级：")
    print("  - 高中英语词汇中缺少音标的2505个单词")
    print("  - 初中英语词汇中缺少音标的41个单词")
    
    print("\n低优先级：")
    print("  - 同时缺少音标和词性的609个单词")
    print("  - 数据格式标准化")
    
    conn.close()

if __name__ == "__main__":
    analyze_missing_data() 