#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库中 senior_high 词表的音频映射
确保每个词都能在考核时调取到正确的发音文件
"""

import sqlite3
import os
import re
import csv
from pathlib import Path

# 配置
DATABASE_FILE = 'vocabulary.db'
SENIOR_HIGH_TXT = 'wordlists/senior_high/Senior_high.txt'
SENIOR_HIGH_CSV = 'wordlists/senior_high/senior_high_complete.csv'
MEDIA_DIR = 'wordlists/senior_high/media'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def extract_audio_mappings_from_txt(txt_file):
    """从 Senior_high.txt 提取音频映射"""
    audio_mappings = {}
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Split by tab
            parts = line.split('\t')
            if len(parts) >= 2:
                word = parts[0].strip()
                if word and word != 'Word':
                    # Extract audio file names from the line
                    audio_files = re.findall(r'cambridge-[a-f0-9-]+\.mp3', line)
                    if audio_files:
                        # 通常第一个是英音，第二个是美音（如果有的话）
                        audio_mappings[word] = {
                            'uk': audio_files[0] if len(audio_files) > 0 else None,
                            'us': audio_files[1] if len(audio_files) > 1 else None
                        }
    
    return audio_mappings

def get_available_audio_files():
    """获取 media 目录下可用的音频文件"""
    audio_files = set()
    if os.path.exists(MEDIA_DIR):
        for file in os.listdir(MEDIA_DIR):
            if file.endswith('.mp3'):
                audio_files.add(file)
    return audio_files

def get_senior_high_words_from_db():
    """从数据库获取 senior_high 词表的所有单词"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查找 senior_high 词书
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.audio_path_uk, w.audio_path_us, w.list_id
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE b.book_name = 'senior_high' OR b.book_name = '高中英语词汇'
        ORDER BY w.spelling
    """)
    
    words = cursor.fetchall()
    conn.close()
    return words

def get_words_from_csv():
    """从 CSV 获取所有单词"""
    words = []
    with open(SENIOR_HIGH_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row.get('Word', '').strip()
            if word and word not in ['Word', '前缀', '后缀', '词根']:
                words.append(word)
    return words

def update_audio_in_database():
    """更新数据库中的音频映射"""
    print("=== 更新 Senior High 词表音频映射 ===\n")
    
    # 1. 获取音频映射
    print("1. 从 Senior_high.txt 提取音频映射...")
    txt_audio_mappings = extract_audio_mappings_from_txt(SENIOR_HIGH_TXT)
    print(f"   找到 {len(txt_audio_mappings)} 个词的音频映射")
    
    # 2. 获取可用音频文件
    print("\n2. 检查 media 目录下的音频文件...")
    available_audio = get_available_audio_files()
    print(f"   找到 {len(available_audio)} 个音频文件")
    
    # 3. 获取数据库中的词
    print("\n3. 从数据库获取 senior_high 词表...")
    db_words = get_senior_high_words_from_db()
    print(f"   数据库中有 {len(db_words)} 个词")
    
    # 4. 获取 CSV 中的词
    print("\n4. 从 CSV 获取所有单词...")
    csv_words = get_words_from_csv()
    print(f"   CSV 中有 {len(csv_words)} 个词")
    
    # 5. 更新数据库
    print("\n5. 更新数据库音频字段...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updated_count = 0
    missing_audio_count = 0
    missing_words = []
    
    for db_word in db_words:
        word_id = db_word['word_id']
        spelling = db_word['spelling']
        
        # 查找对应的音频文件
        audio_uk = None
        audio_us = None
        
        if spelling in txt_audio_mappings:
            # 从 txt 文件获取音频映射
            audio_mapping = txt_audio_mappings[spelling]
            audio_uk = audio_mapping['uk']
            audio_us = audio_mapping['us']
        else:
            # 尝试在 media 目录中查找同名音频文件
            # 这里可以根据需要实现更复杂的匹配逻辑
            pass
        
        # 验证音频文件是否存在
        if audio_uk and audio_uk not in available_audio:
            print(f"   警告: 音频文件不存在 - {audio_uk}")
            audio_uk = None
        
        if audio_us and audio_us not in available_audio:
            print(f"   警告: 音频文件不存在 - {audio_us}")
            audio_us = None
        
        # 更新数据库
        cursor.execute("""
            UPDATE Words 
            SET audio_path_uk = ?, audio_path_us = ?
            WHERE word_id = ?
        """, (audio_uk, audio_us, word_id))
        
        if audio_uk or audio_us:
            updated_count += 1
        else:
            missing_audio_count += 1
            missing_words.append(spelling)
    
    # 6. 检查 CSV 中有但数据库中没有的词
    print("\n6. 检查缺失的词...")
    db_spellings = {word['spelling'] for word in db_words}
    csv_only_words = set(csv_words) - db_spellings
    
    if csv_only_words:
        print(f"   CSV 中有但数据库中没有的词: {len(csv_only_words)} 个")
        print("   前10个:", list(csv_only_words)[:10])
    
    # 提交更改
    conn.commit()
    conn.close()
    
    # 7. 生成报告
    print("\n=== 更新完成 ===")
    print(f"更新了 {updated_count} 个词的音频字段")
    print(f"缺失音频的词: {missing_audio_count} 个")
    
    if missing_words:
        print("\n缺失音频的词:")
        for word in missing_words[:20]:  # 显示前20个
            print(f"  - {word}")
        if len(missing_words) > 20:
            print(f"  ... 还有 {len(missing_words) - 20} 个")
    
    # 生成详细报告
    generate_audio_update_report(txt_audio_mappings, available_audio, db_words, 
                                csv_words, missing_words, csv_only_words)
    
    return {
        'updated_count': updated_count,
        'missing_audio_count': missing_audio_count,
        'missing_words': missing_words,
        'csv_only_words': csv_only_words
    }

def generate_audio_update_report(txt_audio_mappings, available_audio, db_words, 
                                csv_words, missing_words, csv_only_words):
    """生成详细的音频更新报告"""
    
    report_file = 'senior_high_audio_update_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== Senior High 音频更新报告 ===\n\n")
        
        f.write(f"SUMMARY:\n")
        f.write(f"- 数据库中的词数: {len(db_words)}\n")
        f.write(f"- CSV 中的词数: {len(csv_words)}\n")
        f.write(f"- 有音频映射的词数: {len(txt_audio_mappings)}\n")
        f.write(f"- 可用音频文件数: {len(available_audio)}\n")
        f.write(f"- 缺失音频的词数: {len(missing_words)}\n")
        f.write(f"- CSV 独有词数: {len(csv_only_words)}\n\n")
        
        if missing_words:
            f.write("缺失音频的词:\n")
            f.write("=" * 20 + "\n")
            for word in missing_words:
                f.write(f"- {word}\n")
            f.write("\n")
        
        if csv_only_words:
            f.write("CSV 中有但数据库中没有的词:\n")
            f.write("=" * 30 + "\n")
            for word in csv_only_words:
                f.write(f"- {word}\n")
            f.write("\n")
        
        # 样本音频映射
        f.write("样本音频映射:\n")
        f.write("=" * 20 + "\n")
        count = 0
        for word, mapping in txt_audio_mappings.items():
            if count >= 20:
                break
            f.write(f"{word}: UK={mapping['uk']}, US={mapping['us']}\n")
            count += 1
        f.write("\n")
    
    print(f"\n详细报告已保存到: {report_file}")

if __name__ == "__main__":
    update_audio_in_database() 