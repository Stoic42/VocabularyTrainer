import sqlite3
import os

# 连接到数据库
DATABASE_FILE = 'vocabulary.db'
TTS_CACHE_DIR = 'd:\\Projects\\VocabularyTrainer\\wordlists\\tts_cache'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 查询特定单词的音频路径
def check_word_audio_paths(words):
    conn = get_db_connection()
    results = []
    
    for word in words:
        query = "SELECT spelling, audio_path_uk, audio_path_us FROM Words WHERE spelling = ?"
        row = conn.execute(query, (word,)).fetchone()
        
        if row:
            word_data = dict(row)
            # 检查TTS缓存中是否有这个单词的音频
            import hashlib
            word_hash = hashlib.md5(word.encode()).hexdigest() + '.mp3'
            tts_path = os.path.join(TTS_CACHE_DIR, word_hash)
            tts_exists = os.path.exists(tts_path)
            
            results.append({
                'spelling': word_data['spelling'],
                'audio_path_uk': word_data['audio_path_uk'],
                'audio_path_us': word_data['audio_path_us'],
                'tts_path': tts_path,
                'tts_exists': tts_exists
            })
        else:
            results.append({
                'spelling': word,
                'audio_path_uk': None,
                'audio_path_us': None,
                'tts_path': None,
                'tts_exists': False,
                'error': 'Word not found in database'
            })
    
    conn.close()
    return results

# 查询所有单词中缺少美音的情况
def find_missing_us_audio():
    conn = get_db_connection()
    query = "SELECT spelling, audio_path_uk, audio_path_us FROM Words WHERE audio_path_us IS NULL OR audio_path_us = ''"
    rows = conn.execute(query).fetchall()
    
    results = [dict(row) for row in rows]
    conn.close()
    return results

# 检查TTS缓存目录
def check_tts_cache():
    if not os.path.exists(TTS_CACHE_DIR):
        print(f"TTS缓存目录不存在: {TTS_CACHE_DIR}")
        return []
    
    files = os.listdir(TTS_CACHE_DIR)
    mp3_files = [f for f in files if f.endswith('.mp3')]
    return mp3_files

# 主函数
def main():
    # 检查TTS缓存目录
    print("===== TTS缓存目录检查 =====")
    tts_files = check_tts_cache()
    print(f"TTS缓存目录: {TTS_CACHE_DIR}")
    print(f"缓存中的MP3文件数量: {len(tts_files)}")
    print(f"前10个文件: {tts_files[:10]}")
    print("-" * 50)
    
    # 检查特定单词
    target_words = ['thief', 'woman', 'dare', 'horoscope']
    word_results = check_word_audio_paths(target_words)
    
    print("\n===== 特定单词音频路径检查 =====")
    for result in word_results:
        print(f"单词: {result['spelling']}")
        print(f"英音路径: {result['audio_path_uk']}")
        print(f"美音路径: {result['audio_path_us']}")
        print(f"TTS缓存路径: {result['tts_path']}")
        print(f"TTS文件存在: {result['tts_exists']}")
        if 'error' in result:
            print(f"错误: {result['error']}")
        print("-" * 50)
    
    # 查找缺少美音的单词
    print("\n===== 缺少美音的单词 =====")
    missing_us = find_missing_us_audio()
    print(f"总计: {len(missing_us)} 个单词缺少美音")
    
    # 只打印前10个作为示例
    for i, word in enumerate(missing_us[:10]):
        print(f"{i+1}. {word['spelling']} - 英音: {'有' if word['audio_path_uk'] else '无'}")

if __name__ == "__main__":
    main()