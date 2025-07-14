import sqlite3
import re
import os

def map_anki_audio_correct():
    """正确映射Anki音频，英音和美音分别映射到对应字段"""
    print("🔧 正确映射Anki音频（英音+美音）")
    print("=" * 60)
    
    # 解析Anki文件
    anki_file = "wordlists/senior_high/高中 乱序 绿宝书.txt"
    media_dir = "wordlists/senior_high/media"
    
    with open(anki_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配单词和音频文件
    pattern = r'^([a-zA-Z\-\']+)\t.*?\t\[sound:([^\]]+\.mp3)\]\t([^\t]+)'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    print(f"📊 找到 {len(matches)} 个单词-音频映射")
    
    # 检查音频文件是否存在
    existing_files = set()
    for match in matches:
        audio_file = match[1].strip()
        audio_path = os.path.join(media_dir, audio_file)
        if os.path.exists(audio_path):
            existing_files.add(audio_file)
    
    print(f"✅ 存在的音频文件: {len(existing_files)}")
    
    # 分类音频文件
    uk_files = [f for f in existing_files if f.startswith('cambridge-') and not f.startswith('cambridgeee-')]
    us_files = [f for f in existing_files if f.startswith('cambridgeee-')]
    
    print(f"🇬🇧 英音文件: {len(uk_files)} 个")
    print(f"🇺🇸 美音文件: {len(us_files)} 个")
    
    # 创建单词到音频文件的映射
    word_audio_mapping = {}
    
    for match in matches:
        word = match[0].strip().lower()
        audio_file = match[1].strip()
        
        if audio_file not in existing_files:
            continue
        
        if word not in word_audio_mapping:
            word_audio_mapping[word] = {'uk': None, 'us': None}
        
        # 根据文件名判断是英音还是美音
        if audio_file.startswith('cambridge-') and not audio_file.startswith('cambridgeee-'):
            word_audio_mapping[word]['uk'] = audio_file
        elif audio_file.startswith('cambridgeee-'):
            word_audio_mapping[word]['us'] = audio_file
    
    # 统计映射情况
    uk_only = sum(1 for data in word_audio_mapping.values() if data['uk'] and not data['us'])
    us_only = sum(1 for data in word_audio_mapping.values() if data['us'] and not data['uk'])
    both = sum(1 for data in word_audio_mapping.values() if data['uk'] and data['us'])
    
    print(f"\n📊 映射统计:")
    print(f"  只有英音: {uk_only} 个单词")
    print(f"  只有美音: {us_only} 个单词")
    print(f"  英音+美音: {both} 个单词")
    
    # 更新数据库
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 获取高中英语词汇的book_id
    cursor.execute("SELECT book_id FROM Books WHERE book_name = '高中英语词汇'")
    result = cursor.fetchone()
    if not result:
        print("❌ 未找到'高中英语词汇'书籍")
        return
    
    book_id = result[0]
    print(f"📚 高中英语词汇 book_id: {book_id}")
    
    updated_count = 0
    not_found_count = 0
    
    for word, audio_data in word_audio_mapping.items():
        uk_audio = audio_data['uk']
        us_audio = audio_data['us']
        
        # 更新数据库中的单词
        cursor.execute("""
            UPDATE Words 
            SET audio_path_uk = ?, audio_path_us = ?
            WHERE spelling = ? AND list_id IN (
                SELECT list_id FROM WordLists WHERE book_id = ?
            )
        """, (uk_audio, us_audio, word, book_id))
        
        if cursor.rowcount > 0:
            updated_count += 1
        else:
            not_found_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 成功更新 {updated_count} 个单词")
    print(f"❌ 未找到 {not_found_count} 个单词")
    
    # 验证修复结果
    print("\n🔍 验证修复结果:")
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_words,
            SUM(CASE WHEN audio_path_uk IS NOT NULL AND audio_path_uk != '' THEN 1 ELSE 0 END) as has_uk,
            SUM(CASE WHEN audio_path_us IS NOT NULL AND audio_path_us != '' THEN 1 ELSE 0 END) as has_us,
            SUM(CASE WHEN audio_path_uk IS NOT NULL AND audio_path_uk != '' AND audio_path_us IS NOT NULL AND audio_path_us != '' THEN 1 ELSE 0 END) as has_both
        FROM Words w
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        WHERE wl.book_id = ?
    """, (book_id,))
    
    result = cursor.fetchone()
    total_words, has_uk, has_us, has_both = result
    
    print(f"  总单词数: {total_words}")
    print(f"  有英音: {has_uk}")
    print(f"  有美音: {has_us}")
    print(f"  英音+美音: {has_both}")
    
    conn.close()
    
    print("\n🎉 映射完成！现在前端会先播放英音，再播放美音。")

if __name__ == "__main__":
    map_anki_audio_correct() 