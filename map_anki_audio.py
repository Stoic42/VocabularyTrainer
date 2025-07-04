import sqlite3
import re
import os
from pathlib import Path

def parse_anki_file(file_path):
    """解析Anki导出的文件，提取单词和音频文件的映射关系"""
    print("🔍 开始解析Anki文件...")
    
    word_audio_mapping = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配单词和音频文件
    # 格式: word\t释义\t[sound:audio_file.mp3]\t音标\t...
    pattern = r'^([a-zA-Z\-\']+)\t.*?\t\[sound:([^\]]+\.mp3)\]\t([^\t]+)'
    
    matches = re.findall(pattern, content, re.MULTILINE)
    
    print(f"📊 找到 {len(matches)} 个单词-音频映射")
    
    for match in matches:
        word = match[0].strip().lower()
        audio_file = match[1].strip()
        pronunciation = match[2].strip()
        
        # 清理音标（移除可能的HTML标签等）
        pronunciation = re.sub(r'<[^>]+>', '', pronunciation)
        pronunciation = re.sub(r'strong\s+', '', pronunciation)
        pronunciation = pronunciation.strip()
        
        word_audio_mapping[word] = {
            'audio_file': audio_file,
            'pronunciation': pronunciation
        }
    
    return word_audio_mapping

def check_audio_files_exist(mapping, media_dir):
    """检查音频文件是否存在于media目录中"""
    print("🔍 检查音频文件是否存在...")
    
    existing_files = set()
    missing_files = set()
    
    for word, data in mapping.items():
        audio_file = data['audio_file']
        audio_path = os.path.join(media_dir, audio_file)
        
        if os.path.exists(audio_path):
            existing_files.add(audio_file)
        else:
            missing_files.add(audio_file)
    
    print(f"✅ 存在的音频文件: {len(existing_files)}")
    print(f"❌ 缺失的音频文件: {len(missing_files)}")
    
    if missing_files:
        print("缺失的音频文件:")
        for file in list(missing_files)[:10]:  # 只显示前10个
            print(f"  - {file}")
        if len(missing_files) > 10:
            print(f"  ... 还有 {len(missing_files) - 10} 个文件")
    
    return existing_files, missing_files

def update_database(mapping, existing_files):
    """更新数据库中的音频路径和音标"""
    print("🔄 开始更新数据库...")
    
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
    
    for word, data in mapping.items():
        audio_file = data['audio_file']
        pronunciation = data['pronunciation']
        
        # 检查音频文件是否存在
        if audio_file not in existing_files:
            continue
        
        # 构建音频文件路径
        audio_path = f"wordlists/senior_high/media/{audio_file}"
        
        # 更新数据库中的单词
        cursor.execute("""
            UPDATE Words 
            SET audio_path_uk = ?, audio_path_us = ?
            WHERE spelling = ? AND list_id IN (
                SELECT list_id FROM WordLists WHERE book_id = ?
            )
        """, (audio_path, audio_path, word, book_id))
        
        if cursor.rowcount > 0:
            updated_count += 1
        else:
            not_found_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ 成功更新 {updated_count} 个单词")
    print(f"❌ 未找到 {not_found_count} 个单词")
    
    # 输出未匹配的单词和音频名
    if not_found_count > 0:
        with open('unmatched_audio.txt', 'w', encoding='utf-8') as f:
            f.write('未匹配到数据库的单词及音频文件：\n')
            for word, data in mapping.items():
                audio_file = data['audio_file']
                if audio_file in existing_files:
                    # 检查是否未更新
                    # 这里假设未更新的单词就是未找到的
                    cursor = sqlite3.connect('vocabulary.db').cursor()
                    cursor.execute("""
                        SELECT word_id FROM Words WHERE spelling = ? AND list_id IN (
                            SELECT list_id FROM WordLists WHERE book_id = ?
                        ) AND (audio_path_uk IS NULL OR audio_path_uk = '' OR audio_path_uk NOT LIKE ?)
                    """, (word, book_id, f"%{audio_file}"))
                    if cursor.fetchone():
                        f.write(f"{word}\t{audio_file}\n")
    
    return updated_count, not_found_count

def generate_report(mapping, existing_files, missing_files, updated_count, not_found_count):
    """生成映射报告"""
    print("\n" + "="*60)
    print("📋 映射报告")
    print("="*60)
    
    print(f"📊 总映射数量: {len(mapping)}")
    print(f"✅ 音频文件存在: {len(existing_files)}")
    print(f"❌ 音频文件缺失: {len(missing_files)}")
    print(f"🔄 数据库更新成功: {updated_count}")
    print(f"❌ 数据库未找到: {not_found_count}")
    
    # 计算覆盖率
    coverage = len(existing_files) / len(mapping) * 100 if mapping else 0
    db_coverage = updated_count / len(mapping) * 100 if mapping else 0
    
    print(f"📈 音频文件覆盖率: {coverage:.1f}%")
    print(f"📈 数据库更新覆盖率: {db_coverage:.1f}%")
    
    # 显示一些示例映射
    print("\n📝 示例映射:")
    count = 0
    for word, data in list(mapping.items())[:5]:
        status = "✅" if data['audio_file'] in existing_files else "❌"
        print(f"  {status} {word} -> {data['audio_file']} ({data['pronunciation']})")
        count += 1
        if count >= 5:
            break

def main():
    """主函数"""
    print("🎯 开始Anki音频映射处理")
    print("="*60)
    
    # 文件路径
    anki_file = "wordlists/senior_high/高中 乱序 绿宝书.txt"
    media_dir = "wordlists/senior_high/media"
    
    # 检查文件是否存在
    if not os.path.exists(anki_file):
        print(f"❌ Anki文件不存在: {anki_file}")
        return
    
    if not os.path.exists(media_dir):
        print(f"❌ 媒体目录不存在: {media_dir}")
        return
    
    # 1. 解析Anki文件
    mapping = parse_anki_file(anki_file)
    
    if not mapping:
        print("❌ 未能从Anki文件中提取到任何映射关系")
        return
    
    # 2. 检查音频文件
    existing_files, missing_files = check_audio_files_exist(mapping, media_dir)
    
    # 3. 更新数据库
    updated_count, not_found_count = update_database(mapping, existing_files)
    
    # 4. 生成报告
    generate_report(mapping, existing_files, missing_files, updated_count, not_found_count)
    
    print("\n🎉 处理完成！")

if __name__ == "__main__":
    main() 