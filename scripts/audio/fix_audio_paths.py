from utils import get_database_connection, get_database_path
import sqlite3
import os
import hashlib
from gtts import gTTS

# 连接到数据库
DATABASE_FILE = get_database_path()
WORDLISTS_BASE_DIR = 'd:\\Projects\\VocabularyTrainer\\wordlists'
TTS_CACHE_DIR = os.path.join(WORDLISTS_BASE_DIR, 'tts_cache')
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 文本预处理函数
def preprocess_text_for_tts(text):
    """预处理文本以优化TTS效果"""
    # 处理特殊情况
    text = text.replace('a/an', 'a or an')
    text = text.replace('/', ' or ')
    # 可以添加更多替换规则
    return text

# 生成TTS音频
def generate_tts(word):
    # 文本预处理
    processed_word = preprocess_text_for_tts(word)
    
    # 生成文件名（使用哈希避免文件名问题）
    filename = hashlib.md5(processed_word.encode()).hexdigest() + '.mp3'
    filepath = os.path.join(TTS_CACHE_DIR, filename)
    
    # 如果文件不存在，则生成
    if not os.path.exists(filepath):
        print(f"生成TTS音频: {word} -> {filepath}")
        tts = gTTS(text=processed_word, lang='en', slow=False)
        tts.save(filepath)
    else:
        print(f"TTS音频已存在: {word} -> {filepath}")
    
    return filepath

# 检查并修复单词的音频路径
def check_and_fix_audio_paths(words):
    conn = get_db_connection()
    results = []
    
    for word in words:
        query = "SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE spelling = ?"
        row = conn.execute(query, (word,)).fetchone()
        
        if row:
            word_data = dict(row)
            word_id = word_data['word_id']
            
            # 检查美音路径是否存在或为空
            if not word_data['audio_path_us'] or word_data['audio_path_us'] == '':
                # 生成TTS音频
                tts_path = generate_tts(word)
                # 计算相对路径
                rel_path = '/wordlists/tts_cache/' + os.path.basename(tts_path)
                
                # 更新数据库中的美音路径
                update_query = "UPDATE Words SET audio_path_us = ? WHERE word_id = ?"
                conn.execute(update_query, (rel_path, word_id))
                conn.commit()
                
                print(f"已更新单词 '{word}' 的美音路径: {rel_path}")
                
                # 重新获取更新后的数据
                row = conn.execute("SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE word_id = ?", (word_id,)).fetchone()
                word_data = dict(row)
            
            results.append({
                'word_id': word_data['word_id'],
                'spelling': word_data['spelling'],
                'audio_path_uk': word_data['audio_path_uk'],
                'audio_path_us': word_data['audio_path_us'],
                'fixed': True
            })
        else:
            results.append({
                'spelling': word,
                'fixed': False,
                'error': 'Word not found in database'
            })
    
    conn.close()
    return results

# 查找并修复所有缺少美音的单词
def fix_all_missing_us_audio():
    conn = get_db_connection()
    query = "SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE audio_path_us IS NULL OR audio_path_us = ''"
    rows = conn.execute(query).fetchall()
    
    total = len(rows)
    fixed = 0
    
    print(f"找到 {total} 个缺少美音的单词")
    
    # 只处理前10个作为示例
    for i, row in enumerate(rows[:10]):
        word_data = dict(row)
        word = word_data['spelling']
        word_id = word_data['word_id']
        
        print(f"\n处理 {i+1}/10: {word}")
        
        # 生成TTS音频
        try:
            tts_path = generate_tts(word)
            # 计算相对路径
            rel_path = '/wordlists/tts_cache/' + os.path.basename(tts_path)
            
            # 更新数据库中的美音路径
            update_query = "UPDATE Words SET audio_path_us = ? WHERE word_id = ?"
            conn.execute(update_query, (rel_path, word_id))
            conn.commit()
            
            print(f"已更新单词 '{word}' 的美音路径: {rel_path}")
            fixed += 1
        except Exception as e:
            print(f"处理单词 '{word}' 时出错: {str(e)}")
    
    conn.close()
    return {'total': total, 'fixed': fixed}

# 主函数
def main():
    print("===== 音频路径检查与修复工具 =====")
    print("此工具将检查单词的音频路径，并为缺少美音的单词生成TTS音频")
    print("-" * 50)
    
    # 检查并修复特定单词
    target_words = ['thief', 'woman', 'dare', 'horoscope']
    print(f"\n检查并修复特定单词: {', '.join(target_words)}")
    word_results = check_and_fix_audio_paths(target_words)
    
    for result in word_results:
        if result.get('fixed', False):
            print(f"单词: {result['spelling']}")
            print(f"英音路径: {result['audio_path_uk']}")
            print(f"美音路径: {result['audio_path_us']}")
        else:
            print(f"单词: {result['spelling']} - 修复失败: {result.get('error', '未知错误')}")
        print("-" * 30)
    
    # 修复所有缺少美音的单词（示例）
    print("\n===== 修复所有缺少美音的单词（示例） =====")
    fix_result = fix_all_missing_us_audio()
    print(f"\n总计: {fix_result['total']} 个单词缺少美音")
    print(f"已修复: {fix_result['fixed']} 个单词（示例）")
    print("\n要修复所有单词，请取消代码中的限制")

if __name__ == "__main__":
    main()