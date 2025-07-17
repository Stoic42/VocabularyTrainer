from utils import get_database_connection, get_database_path
import sqlite3
import re
import os

def fix_anki_audio_mapping():
    """修复Anki音频映射，只保留美音，英音字段设为空"""
    print("🔧 修复Anki音频映射")
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
    
    # 更新数据库
    conn = get_database_connection()
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
    
    for match in matches:
        word = match[0].strip().lower()
        audio_file = match[1].strip()
        
        # 检查音频文件是否存在
        if audio_file not in existing_files:
            continue
        
        # 只保留美音，英音设为空
        audio_path = audio_file  # 只保留文件名，不包含路径前缀
        
        # 更新数据库中的单词
        cursor.execute("""
            UPDATE Words 
            SET audio_path_uk = NULL, audio_path_us = ?
            WHERE spelling = ? AND list_id IN (
                SELECT list_id FROM WordLists WHERE book_id = ?
            )
        """, (audio_path, word, book_id))
        
        if cursor.rowcount > 0:
            updated_count += 1
        else:
            not_found_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ 成功更新 {updated_count} 个单词")
    print(f"❌ 未找到 {not_found_count} 个单词")
    
    # 验证修复结果
    print("\n🔍 验证修复结果:")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_words,
            SUM(CASE WHEN audio_path_uk IS NULL OR audio_path_uk = '' THEN 1 ELSE 0 END) as no_uk,
            SUM(CASE WHEN audio_path_us IS NOT NULL AND audio_path_us != '' THEN 1 ELSE 0 END) as has_us
        FROM Words w
        LEFT JOIN WordLists wl ON w.list_id = wl.list_id
        WHERE wl.book_id = ?
    """, (book_id,))
    
    result = cursor.fetchone()
    total_words, no_uk, has_us = result
    
    print(f"  总单词数: {total_words}")
    print(f"  无英音: {no_uk}")
    print(f"  有美音: {has_us}")
    
    conn.close()
    
    print("\n🎉 修复完成！现在前端只会播放一次美音，不会重复播放。")

if __name__ == "__main__":
    fix_anki_audio_mapping() 