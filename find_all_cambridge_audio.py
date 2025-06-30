import sqlite3
import os
import re

# 连接到数据库
DATABASE_FILE = 'vocabulary.db'
WORDLISTS_BASE_DIR = 'd:\\Projects\\VocabularyTrainer\\wordlists'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 查找所有使用cambridge音频的单词
def find_all_cambridge_audio():
    conn = get_db_connection()
    
    # 查找所有使用cambridge音频的单词
    query = "SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE audio_path_uk LIKE '%cambridge%' OR audio_path_us LIKE '%cambridge%'"
    rows = conn.execute(query).fetchall()
    
    # 提取文件名和哈希值
    cambridge_files = {}
    for row in rows:
        word_data = dict(row)
        word_id = word_data['word_id']
        spelling = word_data['spelling']
        
        # 检查英音路径
        uk_path = word_data['audio_path_uk']
        if uk_path and 'cambridge' in uk_path:
            file_name = os.path.basename(uk_path)
            if file_name not in cambridge_files:
                cambridge_files[file_name] = []
            cambridge_files[file_name].append({
                'word_id': word_id,
                'spelling': spelling,
                'audio_type': 'uk',
                'path': uk_path
            })
        
        # 检查美音路径
        us_path = word_data['audio_path_us']
        if us_path and 'cambridge' in us_path:
            file_name = os.path.basename(us_path)
            if file_name not in cambridge_files:
                cambridge_files[file_name] = []
            cambridge_files[file_name].append({
                'word_id': word_id,
                'spelling': spelling,
                'audio_type': 'us',
                'path': us_path
            })
    
    conn.close()
    return cambridge_files

# 查找重复使用的cambridge音频文件
def find_duplicate_cambridge_audio(cambridge_files):
    duplicates = {}
    for file_name, words in cambridge_files.items():
        if len(words) > 1:
            duplicates[file_name] = words
    return duplicates

# 提取cambridge文件名中的哈希值
def extract_hash_from_filename(filename):
    # 匹配cambridge-HASH1-HASH2-HASH3-HASH4-HASH5.mp3格式
    match = re.match(r'cambridge-([0-9a-f]+)-([0-9a-f]+)-([0-9a-f]+)-([0-9a-f]+)-([0-9a-f]+)\.mp3', filename)
    if match:
        return '-'.join(match.groups())
    return None

# 按哈希值分组cambridge文件
def group_by_hash(cambridge_files):
    hash_groups = {}
    for file_name, words in cambridge_files.items():
        hash_value = extract_hash_from_filename(file_name)
        if hash_value:
            if hash_value not in hash_groups:
                hash_groups[hash_value] = []
            for word in words:
                word['file_name'] = file_name
                hash_groups[hash_value].append(word)
    return hash_groups

# 主函数
def main():
    print("===== 查找所有Cambridge音频文件 =====")
    print("此工具将查找数据库中所有使用Cambridge音频的单词")
    print("-" * 50)
    
    # 查找所有cambridge音频
    cambridge_files = find_all_cambridge_audio()
    print(f"\n找到 {len(cambridge_files)} 个不同的Cambridge音频文件")
    
    # 查找重复使用的cambridge音频
    duplicates = find_duplicate_cambridge_audio(cambridge_files)
    print(f"找到 {len(duplicates)} 个被多个单词共用的Cambridge音频文件")
    
    # 按哈希值分组
    hash_groups = group_by_hash(cambridge_files)
    print(f"按哈希值分组后有 {len(hash_groups)} 个不同的哈希值")
    
    # 显示被多个单词共用的音频文件
    if duplicates:
        print("\n===== 被多个单词共用的Cambridge音频文件 =====")
        for file_name, words in duplicates.items():
            print(f"\n文件: {file_name}")
            print(f"哈希值: {extract_hash_from_filename(file_name)}")
            print(f"被 {len(words)} 个单词共用:")
            for word in words:
                print(f"  - {word['spelling']} ({word['audio_type']}音): {word['path']}")
            print("-" * 30)
    
    # 检查是否有单词仍在使用已知的horoscope音频
    known_horoscope_hashes = [
        "1047235c-ac6c7f0a-81859e57-59788d0a-2d1dbc06",  # thief的美音
        "67649e25-716ae36f-9f4eca65-b4b0b8ba-4d9c6548",  # woman的美音
        "01fd96b0-edb81282-3a804f4e-06fdcb2f-87382af2"   # dare的美音
    ]
    
    print("\n===== 检查是否有单词仍在使用horoscope音频 =====")
    horoscope_affected = False
    for hash_value in known_horoscope_hashes:
        if hash_value in hash_groups:
            horoscope_affected = True
            words = hash_groups[hash_value]
            print(f"\n发现 {len(words)} 个单词使用horoscope音频哈希值: {hash_value}")
            for word in words:
                print(f"  - {word['spelling']} ({word['audio_type']}音): {word['path']}")
            print("-" * 30)
    
    if not horoscope_affected:
        print("未发现单词使用horoscope音频")
    
    # 生成修复脚本
    if horoscope_affected:
        print("\n需要生成修复脚本来修复这些单词")
        # 这里可以添加生成修复脚本的代码
    else:
        print("\n所有horoscope音频问题已修复，无需生成修复脚本")

if __name__ == "__main__":
    main()