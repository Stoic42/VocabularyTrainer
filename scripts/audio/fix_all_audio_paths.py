from utils import get_database_connection, get_database_path
import sqlite3
import os
import hashlib
from gtts import gTTS
import time

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
        tts = gTTS(text=processed_word, lang='en', slow=False)
        tts.save(filepath)
    
    return filepath

# 修复所有缺少美音的单词
def fix_all_missing_us_audio(batch_size=100, max_words=None):
    conn = get_db_connection()
    query = "SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE audio_path_us IS NULL OR audio_path_us = ''"
    rows = conn.execute(query).fetchall()
    
    total = len(rows)
    print(f"找到 {total} 个缺少美音的单词")
    
    # 如果指定了最大处理数量，则限制处理的单词数
    if max_words and max_words < total:
        rows = rows[:max_words]
        print(f"将只处理前 {max_words} 个单词")
    
    fixed = 0
    errors = 0
    start_time = time.time()
    
    # 分批处理单词
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        print(f"\n处理批次 {i//batch_size + 1}/{(len(rows)-1)//batch_size + 1} ({i+1}-{min(i+batch_size, len(rows))}/{len(rows)})")
        
        for j, row in enumerate(batch):
            word_data = dict(row)
            word = word_data['spelling']
            word_id = word_data['word_id']
            
            # 显示进度
            if j % 10 == 0 or j == len(batch) - 1:
                elapsed = time.time() - start_time
                words_per_second = (i + j + 1) / elapsed if elapsed > 0 else 0
                estimated_total = total / words_per_second if words_per_second > 0 else 0
                remaining = estimated_total - elapsed if estimated_total > 0 else 0
                
                print(f"进度: {i+j+1}/{len(rows)} ({(i+j+1)/len(rows)*100:.1f}%) "
                      f"- 已用时间: {elapsed:.1f}秒 "
                      f"- 预计剩余: {remaining:.1f}秒 "
                      f"- 速度: {words_per_second:.1f}词/秒")
            
            # 生成TTS音频
            try:
                tts_path = generate_tts(word)
                # 计算相对路径
                rel_path = '/wordlists/tts_cache/' + os.path.basename(tts_path)
                
                # 更新数据库中的美音路径
                update_query = "UPDATE Words SET audio_path_us = ? WHERE word_id = ?"
                conn.execute(update_query, (rel_path, word_id))
                fixed += 1
            except Exception as e:
                print(f"处理单词 '{word}' 时出错: {str(e)}")
                errors += 1
        
        # 每批次提交一次，减少数据库操作
        conn.commit()
        print(f"批次 {i//batch_size + 1} 完成，已修复 {fixed} 个单词，失败 {errors} 个")
    
    conn.close()
    
    total_time = time.time() - start_time
    print(f"\n===== 处理完成 =====")
    print(f"总计处理: {len(rows)} 个单词")
    print(f"成功修复: {fixed} 个单词")
    print(f"处理失败: {errors} 个单词")
    print(f"总用时: {total_time:.1f}秒")
    print(f"平均速度: {fixed/total_time:.1f}词/秒")
    
    return {'total': total, 'processed': len(rows), 'fixed': fixed, 'errors': errors}

# 主函数
def main():
    print("===== 音频路径批量修复工具 =====")
    print("此工具将为所有缺少美音的单词生成TTS音频并更新数据库")
    print("-" * 50)
    
    # 询问用户是否要处理所有单词
    max_words = input("请输入要处理的最大单词数量（直接回车处理所有单词）: ")
    if max_words.strip():
        try:
            max_words = int(max_words)
        except ValueError:
            print("输入无效，将处理所有单词")
            max_words = None
    else:
        max_words = None
    
    # 询问用户批次大小
    batch_size = input("请输入每批处理的单词数量（直接回车使用默认值100）: ")
    if batch_size.strip():
        try:
            batch_size = int(batch_size)
        except ValueError:
            print("输入无效，将使用默认批次大小100")
            batch_size = 100
    else:
        batch_size = 100
    
    # 确认开始处理
    confirm = input("准备开始处理，这可能需要较长时间。是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    # 开始处理
    print("\n开始处理...")
    fix_all_missing_us_audio(batch_size=batch_size, max_words=max_words)

if __name__ == "__main__":
    main()