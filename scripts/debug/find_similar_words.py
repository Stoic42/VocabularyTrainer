from utils import get_database_connection, get_database_path
import sqlite3

def find_similar_words():
    """查找类似'shall'的单词（缺少音标和词性）"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    print("🔍 查找类似'shall'的单词（缺少音标和词性）")
    print("=" * 80)
    
    # 查找同时缺少音标和词性的单词
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
    """)
    
    words = cursor.fetchall()
    
    if not words:
        print("✅ 没有发现类似'shall'的单词（同时缺少音标和词性）")
        return
    
    print(f"❌ 发现 {len(words)} 个单词同时缺少音标和词性：")
    print()
    
    # 按词书分组显示
    current_book = None
    current_list = None
    
    for word in words:
        word_id, spelling, meaning_cn, pos, audio_uk, audio_us, list_name, book_name = word
        
        # 显示词书分隔
        if current_book != book_name:
            current_book = book_name
            print(f"📚 {book_name}")
            print("-" * 50)
        
        # 显示单元分隔
        if current_list != list_name:
            current_list = list_name
            print(f"  📖 {list_name}")
        
        # 显示单词信息
        meaning_short = meaning_cn[:40] + "..." if len(meaning_cn) > 40 else meaning_cn
        print(f"    • {spelling:<15} (ID: {word_id}) - {meaning_short}")
    
    print()
    print("💡 填充建议：")
    print("=" * 80)
    
    # 1. 词性提取建议
    print("1️⃣ 词性提取：")
    print("   - 从 meaning_cn 字段中提取词性信息")
    print("   - 常见词性：n., v., adj., adv., prep., conj., pron., etc.")
    print("   - 可以使用正则表达式：^([a-z]+\.)\\s")
    
    # 2. 音标获取建议
    print("\n2️⃣ 音标获取：")
    print("   - 使用 Cambridge Dictionary API")
    print("   - 使用 gTTS 生成音频")
    print("   - 从现有音频文件中提取")
    print("   - 使用第三方词典API")
    
    # 3. 批量处理建议
    print("\n3️⃣ 批量处理：")
    print("   - 创建自动化脚本")
    print("   - 优先处理高频词汇")
    print("   - 建立缓存机制")
    print("   - 定期检查更新")
    
    # 4. 具体实现
    print("\n4️⃣ 具体实现：")
    print("   - 修改导入脚本")
    print("   - 添加管理界面功能")
    print("   - 创建数据质量检查工具")
    print("   - 建立工作流程")
    
    conn.close()

if __name__ == "__main__":
    find_similar_words() 