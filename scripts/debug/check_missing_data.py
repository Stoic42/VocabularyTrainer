from utils import get_database_connection, get_database_path
import sqlite3
import re

def check_missing_data():
    """检查数据库中缺少音标和词性的单词"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # 查询缺少音标或词性的单词
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.meaning_cn, w.pos, w.audio_path_uk, w.audio_path_us,
               wl.list_name, b.book_name
        FROM Words w
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        LEFT JOIN Books b ON wl.book_id = b.book_id
        WHERE (w.pos IS NULL OR w.pos = '' OR w.pos = 'N/A') 
           OR (w.audio_path_uk IS NULL OR w.audio_path_uk = '' OR w.audio_path_uk = 'N/A')
           OR (w.audio_path_us IS NULL OR w.audio_path_us = '' OR w.audio_path_us = 'N/A')
        ORDER BY b.book_name, wl.list_name, w.spelling
    """)
    
    words = cursor.fetchall()
    
    if not words:
        print("✅ 所有单词都有完整的音标和词性信息！")
        return
    
    print(f"❌ 发现 {len(words)} 个单词缺少音标或词性信息：")
    print("=" * 100)
    
    # 按词书分组统计
    book_stats = {}
    for word in words:
        word_id, spelling, meaning_cn, pos, audio_uk, audio_us, list_name, book_name = word
        if book_name not in book_stats:
            book_stats[book_name] = {'total': 0, 'missing_pos': 0, 'missing_audio': 0, 'missing_both': 0}
        
        book_stats[book_name]['total'] += 1
        
        missing_pos = not pos or pos == '' or pos == 'N/A'
        missing_audio = (not audio_uk or audio_uk == '' or audio_uk == 'N/A') and (not audio_us or audio_us == '' or audio_us == 'N/A')
        
        if missing_pos and missing_audio:
            book_stats[book_name]['missing_both'] += 1
        elif missing_pos:
            book_stats[book_name]['missing_pos'] += 1
        elif missing_audio:
            book_stats[book_name]['missing_audio'] += 1
    
    # 显示统计信息
    print("📊 统计信息：")
    print("-" * 80)
    print(f"{'词书名称':<20} {'总数量':<8} {'缺词性':<8} {'缺音标':<8} {'都缺少':<8}")
    print("-" * 80)
    
    total_missing = 0
    for book_name, stats in book_stats.items():
        print(f"{book_name:<20} {stats['total']:<8} {stats['missing_pos']:<8} {stats['missing_audio']:<8} {stats['missing_both']:<8}")
        total_missing += stats['total']
    
    print("-" * 80)
    print(f"总计: {total_missing} 个单词需要补充信息")
    
    # 显示前20个示例
    print(f"\n📝 前20个示例：")
    print("-" * 100)
    print(f"{'ID':<6} {'单词':<15} {'词性':<8} {'音标UK':<12} {'音标US':<12} {'单元':<20} {'词书':<15}")
    print("-" * 100)
    
    for i, word in enumerate(words[:20]):
        word_id, spelling, meaning_cn, pos, audio_uk, audio_us, list_name, book_name = word
        
        # 格式化显示
        pos_display = pos if pos and pos != 'N/A' else '❌'
        audio_uk_display = '✅' if audio_uk and audio_uk != 'N/A' else '❌'
        audio_us_display = '✅' if audio_us and audio_us != 'N/A' else '❌'
        
        print(f"{word_id:<6} {spelling:<15} {pos_display:<8} {audio_uk_display:<12} {audio_us_display:<12} {list_name:<20} {book_name:<15}")
    
    if len(words) > 20:
        print(f"... 还有 {len(words) - 20} 个单词")
    
    # 提供填充建议
    print(f"\n💡 填充建议：")
    print("=" * 100)
    
    # 1. 词性提取建议
    print("1️⃣ 词性提取建议：")
    print("   - 从 meaning_cn 字段中提取词性信息")
    print("   - 常见词性格式：n., v., adj., adv., prep., conj., pron., etc.")
    print("   - 可以使用正则表达式：^([a-z]+\.)\\s")
    
    # 2. 音标获取建议
    print("\n2️⃣ 音标获取建议：")
    print("   - 使用 Cambridge Dictionary API 获取音标")
    print("   - 使用 gTTS 生成音频文件")
    print("   - 从现有音频文件中提取音标信息")
    print("   - 使用第三方词典API（如 Oxford、Merriam-Webster）")
    
    # 3. 批量处理建议
    print("\n3️⃣ 批量处理建议：")
    print("   - 创建自动化脚本批量获取音标和词性")
    print("   - 优先处理高频词汇")
    print("   - 建立音标和词性的缓存机制")
    print("   - 定期检查和更新缺失信息")
    
    # 4. 具体实现建议
    print("\n4️⃣ 具体实现建议：")
    print("   - 修改导入脚本，在导入时自动提取词性")
    print("   - 添加音标获取功能到管理界面")
    print("   - 创建数据质量检查工具")
    print("   - 建立数据补充的工作流程")
    
    # 显示一些具体的词性提取示例
    print(f"\n🔍 词性提取示例：")
    print("-" * 60)
    
    # 查找一些有完整meaning_cn的单词作为示例
    cursor.execute("""
        SELECT spelling, meaning_cn 
        FROM Words 
        WHERE meaning_cn IS NOT NULL AND meaning_cn != '' 
        AND (pos IS NULL OR pos = '' OR pos = 'N/A')
        LIMIT 10
    """)
    
    examples = cursor.fetchall()
    for spelling, meaning_cn in examples:
        # 尝试提取词性
        pos_match = re.match(r'^([a-z]+\.)\s', meaning_cn.lower())
        if pos_match:
            extracted_pos = pos_match.group(1)
            remaining_meaning = meaning_cn[len(extracted_pos):].strip()
            print(f"单词: {spelling}")
            print(f"  原始: {meaning_cn}")
            print(f"  提取词性: {extracted_pos}")
            print(f"  剩余释义: {remaining_meaning}")
            print()
    
    conn.close()

if __name__ == "__main__":
    check_missing_data() 