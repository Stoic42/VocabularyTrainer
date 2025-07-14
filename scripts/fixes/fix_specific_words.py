#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import get_database_connection, get_database_path
import sqlite3
import os
import hashlib
from gtts import gTTS
import re

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
        print(f"生成TTS音频: {word} -> {filepath}")
        tts = gTTS(text=processed_word, lang='en', slow=False)
        tts.save(filepath)
    else:
        print(f"TTS音频已存在: {word} -> {filepath}")
    
    return filepath

# 修复特定单词的音频路径
def fix_specific_words(words):
    conn = get_db_connection()
    results = []
    
    for word in words:
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

def fix_content_word():
    """修正content单词的数据"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    print("正在修正content单词...")
    
    # 根据词书原件，content的正确信息应该是：
    content_data = {
        'pos': 'adj. 满意的/ˈkɒntent/n. 内容；含量',
        'meaning_cn': 'adj. 满意的/ˈkɒntent/n. 内容；含量',
        'mnemonic': '词根记忆：con＋tent（伸展）→全身舒展→满意的',
        'collocation': '1．be content with...对…满意2．be content to do...乐于做…',
        'exam_sentence': 'After a good meal, we were all content. 美餐一顿之后，我们都心满意足了。//This dessert has a high fat content. 这种甜点脂肪含量很高。'
    }
    
    cursor.execute("""
        UPDATE Words SET 
            pos = ?,
            meaning_cn = ?,
            mnemonic = ?,
            collocation = ?,
            exam_sentence = ?
        WHERE spelling = 'content'
    """, (
        content_data['pos'],
        content_data['meaning_cn'],
        content_data['mnemonic'],
        content_data['collocation'],
        content_data['exam_sentence']
    ))
    
    print("content单词修正完成")
    
    conn.commit()
    conn.close()

def fix_forgivee_word():
    """修正forgivee单词的拼写错误"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    print("正在修正forgivee单词的拼写...")
    
    # 将forgivee改为forgive
    cursor.execute("UPDATE Words SET spelling = 'forgive' WHERE spelling = 'forgivee'")
    
    print("forgivee单词拼写修正完成")
    
    conn.commit()
    conn.close()

# 主函数
def main():
    print("===== 特定单词音频修复工具 =====")
    print("此工具将修复特定单词的美音路径问题")
    print("-" * 50)
    
    # 要修复的单词列表
    target_words = ['thief', 'woman', 'dare']
    
    # 修复单词
    results = fix_specific_words(target_words)
    
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

    print("\n开始修正特定单词问题...")
    
    fix_content_word()
    fix_forgivee_word()
    
    print("所有特定单词修正完成！")

if __name__ == "__main__":
    main()