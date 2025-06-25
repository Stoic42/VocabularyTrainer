import sqlite3
import os
import hashlib

# 连接到数据库
DATABASE_FILE = 'd:\\Projects\\VocabularyTrainer\\vocabulary.db'
WORDLISTS_BASE_DIR = 'd:\\Projects\\VocabularyTrainer\\wordlists'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 修复recen为recent
def fix_recen_typo():
    conn = get_db_connection()
    
    # 查找recen记录
    query = "SELECT word_id, spelling FROM Words WHERE spelling = 'recen'"
    row = conn.execute(query).fetchone()
    
    if row:
        word_id = row['word_id']
        print(f"找到拼写错误的单词: recen (ID: {word_id})")
        
        # 更新拼写
        update_query = "UPDATE Words SET spelling = 'recent' WHERE word_id = ?"
        conn.execute(update_query, (word_id,))
        conn.commit()
        print("已将 'recen' 更正为 'recent'")
    else:
        print("未找到 'recen' 记录")
    
    conn.close()

# 检查特定单词的音频路径
def check_specific_words():
    conn = get_db_connection()
    
    # 要检查的单词列表
    words_to_check = ['thief', 'woman', 'dare', 'horoscope']
    results = []
    
    for word in words_to_check:
        query = "SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE spelling = ?"
        row = conn.execute(query, (word,)).fetchone()
        
        if row:
            word_data = dict(row)
            print(f"单词: {word_data['spelling']}")
            print(f"  英音路径: {word_data['audio_path_uk']}")
            print(f"  美音路径: {word_data['audio_path_us']}")
            print("-" * 30)
            
            results.append(word_data)
        else:
            print(f"单词 '{word}' 在数据库中不存在")
            print("-" * 30)
    
    conn.close()
    return results

# 检查horoscope音频问题 - 使用文件名匹配
def check_horoscope_audio_issue():
    conn = get_db_connection()
    
    # 已知的horoscope音频文件名
    known_horoscope_files = [
        "cambridge-1047235c-ac6c7f0a-81859e57-59788d0a-2d1dbc06.mp3",  # thief的美音
        "cambridge-67649e25-716ae36f-9f4eca65-b4b0b8ba-4d9c6548.mp3",  # woman的美音
        "cambridge-01fd96b0-edb81282-3a804f4e-06fdcb2f-87382af2.mp3"   # dare的美音
    ]
    
    # 查找所有使用这些文件的单词
    results = []
    for filename in known_horoscope_files:
        query = "SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE audio_path_us LIKE ? OR audio_path_uk LIKE ?"
        rows = conn.execute(query, (f'%{filename}%', f'%{filename}%')).fetchall()
        
        for row in rows:
            word_data = dict(row)
            results.append({
                'word_id': word_data['word_id'],
                'spelling': word_data['spelling'],
                'audio_path_uk': word_data['audio_path_uk'],
                'audio_path_us': word_data['audio_path_us'],
                'matched_file': filename
            })
    
    conn.close()
    return results

# 生成修复脚本
def generate_fix_script(affected_words):
    if not affected_words:
        return
    
    script_content = '''import sqlite3
import os
import hashlib
from gtts import gTTS

# 连接到数据库
DATABASE_FILE = 'd:\\\\Projects\\\\VocabularyTrainer\\\\vocabulary.db'
WORDLISTS_BASE_DIR = 'd:\\\\Projects\\\\VocabularyTrainer\\\\wordlists'
TTS_CACHE_DIR = os.path.join(WORDLISTS_BASE_DIR, 'tts_cache')
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 文本预处理函数
def preprocess_text_for_tts(text):
    # 预处理文本以优化TTS效果
    if not text:
        return text
        
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

# 修复受影响的单词
def fix_affected_words():
    conn = get_db_connection()
    affected_words = [
'''
    
    # 添加受影响的单词列表
    word_list = ", ".join([f"'{word['spelling']}'" for word in affected_words])
    script_content += f"        {word_list}\n    ]\n\n"
    
    script_content += '''    results = []
    
    for word in affected_words:
        print(f"\n处理单词: {word}")
        
        # 查询单词信息
        query = "SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE spelling = ?"
        row = conn.execute(query, (word,)).fetchone()
        
        if not row:
            print(f"单词 '{word}' 在数据库中不存在")
            results.append({'spelling': word, 'status': 'not_found'})
            continue
        
        word_data = dict(row)
        word_id = word_data['word_id']
        
        # 显示当前音频路径
        print(f"当前英音路径: {word_data['audio_path_uk']}")
        print(f"当前美音路径: {word_data['audio_path_us']}")
        
        # 生成新的TTS音频
        try:
            tts_path = generate_tts(word)
            rel_path = '/wordlists/tts_cache/' + os.path.basename(tts_path)
            
            # 更新数据库中的美音路径
            update_query = "UPDATE Words SET audio_path_us = ? WHERE word_id = ?"
            conn.execute(update_query, (rel_path, word_id))
            conn.commit()
            
            print(f"已更新单词 '{word}' 的美音路径: {rel_path}")
            
            # 重新查询更新后的信息
            row = conn.execute(query, (word,)).fetchone()
            updated_data = dict(row)
            
            results.append({
                'spelling': word,
                'word_id': word_id,
                'old_audio_path_us': word_data['audio_path_us'],
                'new_audio_path_us': updated_data['audio_path_us'],
                'status': 'fixed'
            })
        except Exception as e:
            print(f"处理单词 '{word}' 时出错: {str(e)}")
            results.append({'spelling': word, 'status': 'error', 'error': str(e)})
    
    conn.close()
    return results

# 主函数
def main():
    print("===== 修复horoscope音频问题 =====")
    print("此工具将修复所有使用horoscope音频的单词")
    print("-" * 50)
    
    # 修复单词
    results = fix_affected_words()
    
    # 显示结果摘要
    print("\n===== 修复结果摘要 =====")
    for result in results:
        status = result['status']
        word = result['spelling']
        
        if status == 'fixed':
            print(f"✓ {word}: 已修复 - 旧路径: {result['old_audio_path_us']} -> 新路径: {result['new_audio_path_us']}")
        elif status == 'not_found':
            print(f"✗ {word}: 单词在数据库中不存在")
        else:
            print(f"✗ {word}: 修复失败 - {result.get('error', '未知错误')}")
    
    print("\n修复完成。请重启应用以应用更改。")

if __name__ == "__main__":
    main()
'''
    
    # 保存修复脚本
    script_path = os.path.join(os.path.dirname(DATABASE_FILE), 'fix_horoscope_affected_words.py')
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"\n已生成修复脚本: {script_path}")
    print("运行此脚本可修复所有受影响的单词")

# 主函数
def main():
    print("===== 检查horoscope音频问题 =====")
    print("此工具将检查数据库中的拼写错误和horoscope音频问题")
    print("-" * 50)
    
    # 修复recen拼写错误
    print("\n1. 修复recen拼写错误")
    fix_recen_typo()
    
    # 检查特定单词
    print("\n2. 检查特定单词的音频路径")
    specific_words = check_specific_words()
    
    # 检查horoscope音频问题
    print("\n3. 检查horoscope音频问题")
    affected_words = check_horoscope_audio_issue()
    
    if affected_words:
        print(f"\n找到 {len(affected_words)} 个使用horoscope音频的单词:")
        for i, word in enumerate(affected_words):
            print(f"{i+1}. {word['spelling']} - 匹配文件: {word['matched_file']}")
            print(f"   英音路径: {word['audio_path_uk']}")
            print(f"   美音路径: {word['audio_path_us']}")
            print("-" * 30)
        
        # 生成修复脚本
        generate_fix_script(affected_words)
    else:
        print("未找到使用horoscope音频的单词")

if __name__ == "__main__":
    main()