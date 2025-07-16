#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库中的音频映射是否正确
确保每个词都能在考核时调取到正确的发音文件
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os
import csv

# 配置
DATABASE_FILE = get_database_path()
MEDIA_DIR = 'wordlists/senior_high/media'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_available_audio_files():
    """获取 media 目录下可用的音频文件"""
    audio_files = set()
    if os.path.exists(MEDIA_DIR):
        for file in os.listdir(MEDIA_DIR):
            if file.endswith('.mp3'):
                audio_files.add(file)
    return audio_files

def verify_audio_mapping():
    """验证数据库中的音频映射"""
    print("=== 验证 Senior High 音频映射 ===\n")
    
    # 1. 获取可用音频文件
    print("1. 检查 media 目录下的音频文件...")
    available_audio = get_available_audio_files()
    print(f"   找到 {len(available_audio)} 个音频文件")
    
    # 2. 获取数据库中的词
    print("\n2. 从数据库获取 senior_high 词表...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.audio_path_uk, w.audio_path_us, w.list_id
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE b.book_name = 'senior_high' OR b.book_name = '高中英语词汇'
        ORDER BY w.spelling
    """)
    
    db_words = cursor.fetchall()
    conn.close()
    print(f"   数据库中有 {len(db_words)} 个词")
    
    # 3. 验证音频映射
    print("\n3. 验证音频映射...")
    
    valid_audio_count = 0
    missing_audio_count = 0
    invalid_audio_count = 0
    missing_words = []
    invalid_words = []
    
    for word in db_words:
        spelling = word['spelling']
        audio_uk = word['audio_path_uk']
        audio_us = word['audio_path_us']
        
        has_valid_audio = False
        
        # 检查英音
        if audio_uk:
            if audio_uk in available_audio:
                has_valid_audio = True
            else:
                invalid_words.append(f"{spelling} (UK: {audio_uk})")
                invalid_audio_count += 1
        
        # 检查美音
        if audio_us:
            if audio_us in available_audio:
                has_valid_audio = True
            else:
                invalid_words.append(f"{spelling} (US: {audio_us})")
                invalid_audio_count += 1
        
        if has_valid_audio:
            valid_audio_count += 1
        else:
            missing_audio_count += 1
            missing_words.append(spelling)
    
    # 4. 生成报告
    print("\n=== 验证结果 ===")
    print(f"总词数: {len(db_words)}")
    print(f"有有效音频的词: {valid_audio_count}")
    print(f"缺失音频的词: {missing_audio_count}")
    print(f"音频文件不存在的词: {invalid_audio_count}")
    
    # 计算覆盖率
    coverage = (valid_audio_count / len(db_words)) * 100 if db_words else 0
    print(f"音频覆盖率: {coverage:.2f}%")
    
    if missing_words:
        print(f"\n缺失音频的词 (前20个):")
        for word in missing_words[:20]:
            print(f"  - {word}")
        if len(missing_words) > 20:
            print(f"  ... 还有 {len(missing_words) - 20} 个")
    
    if invalid_words:
        print(f"\n音频文件不存在的词 (前10个):")
        for word in invalid_words[:10]:
            print(f"  - {word}")
        if len(invalid_words) > 10:
            print(f"  ... 还有 {len(invalid_words) - 10} 个")
    
    # 生成详细报告
    generate_verification_report(db_words, available_audio, valid_audio_count, 
                               missing_audio_count, invalid_audio_count, 
                               missing_words, invalid_words, coverage)
    
    return {
        'total_words': len(db_words),
        'valid_audio_count': valid_audio_count,
        'missing_audio_count': missing_audio_count,
        'invalid_audio_count': invalid_audio_count,
        'coverage': coverage,
        'missing_words': missing_words,
        'invalid_words': invalid_words
    }

def generate_verification_report(db_words, available_audio, valid_audio_count, 
                               missing_audio_count, invalid_audio_count, 
                               missing_words, invalid_words, coverage):
    """生成详细的验证报告"""
    
    report_file = 'senior_high_audio_verification_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== Senior High 音频映射验证报告 ===\n\n")
        
        f.write(f"SUMMARY:\n")
        f.write(f"- 总词数: {len(db_words)}\n")
        f.write(f"- 有有效音频的词: {valid_audio_count}\n")
        f.write(f"- 缺失音频的词: {missing_audio_count}\n")
        f.write(f"- 音频文件不存在的词: {invalid_audio_count}\n")
        f.write(f"- 音频覆盖率: {coverage:.2f}%\n")
        f.write(f"- 可用音频文件数: {len(available_audio)}\n\n")
        
        if missing_words:
            f.write("缺失音频的词:\n")
            f.write("=" * 20 + "\n")
            for word in missing_words:
                f.write(f"- {word}\n")
            f.write("\n")
        
        if invalid_words:
            f.write("音频文件不存在的词:\n")
            f.write("=" * 25 + "\n")
            for word in invalid_words:
                f.write(f"- {word}\n")
            f.write("\n")
        
        # 样本有效音频映射
        f.write("样本有效音频映射:\n")
        f.write("=" * 25 + "\n")
        count = 0
        for word in db_words:
            if count >= 20:
                break
            if word['audio_path_uk'] or word['audio_path_us']:
                f.write(f"{word['spelling']}: UK={word['audio_path_uk']}, US={word['audio_path_us']}\n")
                count += 1
        f.write("\n")
    
    print(f"\n详细验证报告已保存到: {report_file}")

def test_audio_playback():
    """测试音频播放功能（模拟）"""
    print("\n=== 音频播放测试 ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取一些有音频的词进行测试
    cursor.execute("""
        SELECT w.spelling, w.audio_path_uk, w.audio_path_us
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE (b.book_name = 'senior_high' OR b.book_name = '高中英语词汇')
        AND (w.audio_path_uk IS NOT NULL OR w.audio_path_us IS NOT NULL)
        LIMIT 5
    """)
    
    test_words = cursor.fetchall()
    conn.close()
    
    print("测试音频播放路径:")
    for word in test_words:
        spelling = word['spelling']
        audio_uk = word['audio_path_uk']
        audio_us = word['audio_path_us']
        
        print(f"\n单词: {spelling}")
        if audio_uk:
            uk_path = os.path.join(MEDIA_DIR, audio_uk)
            if os.path.exists(uk_path):
                print(f"  英音: ✓ {audio_uk}")
            else:
                print(f"  英音: ✗ {audio_uk} (文件不存在)")
        
        if audio_us:
            us_path = os.path.join(MEDIA_DIR, audio_us)
            if os.path.exists(us_path):
                print(f"  美音: ✓ {audio_us}")
            else:
                print(f"  美音: ✗ {audio_us} (文件不存在)")

if __name__ == "__main__":
    verify_audio_mapping()
    test_audio_playback() 