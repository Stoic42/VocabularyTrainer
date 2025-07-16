from utils import get_database_connection, get_database_path
import sqlite3
import os

# --- 配置区 ---
DATABASE_FILE = get_database_path()
# 音频数据源 (包含[sound:xxx]标签)
TXT_FILE_PATH = 'wordlists/junior_high/初中 乱序 绿宝书.txt'
# 音频文件目录
MEDIA_DIR = 'wordlists/junior_high/media'
# ----------------

def load_audio_paths_from_txt(txt_path):
    """
    扫描TXT文件，建立一个 "单词 -> 音频路径" 的映射字典。
    """
    print(f"正在从 '{txt_path}' 加载音频路径...")
    audio_map = {}
    try:
        with open(txt_path, mode='r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) < 12:
                    continue # 跳过格式不正确的行
                
                spelling = parts[1].strip().lower() # 使用小写单词作为key，更稳定
                uk_ref = parts[10].strip()
                us_ref = parts[11].strip()

                audio_uk = ""
                audio_us = ""

                if uk_ref.startswith('[sound:') and uk_ref.endswith(']'):
                    audio_uk = uk_ref[7:-1]
                if us_ref.startswith('[sound:') and us_ref.endswith(']'):
                    audio_us = us_ref[7:-1]
                
                if audio_uk or audio_us:
                    audio_map[spelling] = {'uk': audio_uk, 'us': audio_us}
    except FileNotFoundError:
        print(f"错误: 找不到音频来源文件 '{txt_path}'")
        return None
    
    print(f"音频路径加载完成！共找到 {len(audio_map)} 个单词的音频。")
    return audio_map

def update_audio_paths(conn, audio_map):
    """
    更新数据库中的音频路径
    """
    if not audio_map:
        print("没有音频映射数据，无法更新。")
        return
    
    cursor = conn.cursor()
    updated_count = 0
    not_found_count = 0
    not_found_words = []
    
    # 获取数据库中所有单词
    cursor.execute("SELECT word_id, spelling FROM Words WHERE list_id IN (SELECT list_id FROM WordLists WHERE book_id = (SELECT book_id FROM Books WHERE book_name = '初中英语词汇'))")
    words = cursor.fetchall()
    
    print(f"开始更新 {len(words)} 个单词的音频路径...")
    
    for word_id, spelling in words:
        spelling_key = spelling.lower()
        
        # 从映射中查找音频路径
        audio_data = audio_map.get(spelling_key)
        
        if audio_data:
            # 更新数据库中的音频路径
            cursor.execute(
                "UPDATE Words SET audio_path_uk = ?, audio_path_us = ? WHERE word_id = ?",
                (audio_data['uk'], audio_data['us'], word_id)
            )
            updated_count += 1
        else:
            not_found_count += 1
            not_found_words.append(spelling)
    
    conn.commit()
    
    print(f"音频路径更新完成！")
    print(f"成功更新: {updated_count} 个单词")
    print(f"未找到映射: {not_found_count} 个单词")
    
    if not_found_words:
        print("\n未找到映射的单词示例 (最多显示10个):")
        for word in not_found_words[:10]:
            print(f"  - {word}")
        if len(not_found_words) > 10:
            print(f"  ... 以及其他 {len(not_found_words) - 10} 个单词")

def verify_audio_files(conn):
    """
    验证数据库中的音频路径是否对应到实际存在的文件
    """
    print("\n开始验证音频文件是否存在...")
    
    cursor = conn.cursor()
    cursor.execute("SELECT word_id, spelling, audio_path_uk, audio_path_us FROM Words WHERE list_id IN (SELECT list_id FROM WordLists WHERE book_id = (SELECT book_id FROM Books WHERE book_name = '初中英语词汇'))")
    words = cursor.fetchall()
    
    uk_exists_count = 0
    us_exists_count = 0
    uk_missing_count = 0
    us_missing_count = 0
    missing_files = []
    
    for word_id, spelling, audio_path_uk, audio_path_us in words:
        # 检查英音文件
        if audio_path_uk:
            uk_file_path = os.path.join(MEDIA_DIR, audio_path_uk)
            if os.path.exists(uk_file_path):
                uk_exists_count += 1
            else:
                uk_missing_count += 1
                missing_files.append((spelling, 'uk', audio_path_uk))
        
        # 检查美音文件
        if audio_path_us:
            us_file_path = os.path.join(MEDIA_DIR, audio_path_us)
            if os.path.exists(us_file_path):
                us_exists_count += 1
            else:
                us_missing_count += 1
                missing_files.append((spelling, 'us', audio_path_us))
    
    print(f"验证完成！")
    print(f"英音文件存在: {uk_exists_count} 个")
    print(f"英音文件缺失: {uk_missing_count} 个")
    print(f"美音文件存在: {us_exists_count} 个")
    print(f"美音文件缺失: {us_missing_count} 个")
    
    if missing_files:
        print("\n缺失的音频文件示例 (最多显示10个):")
        for spelling, accent, path in missing_files[:10]:
            print(f"  - {spelling} ({accent}): {path}")
        if len(missing_files) > 10:
            print(f"  ... 以及其他 {len(missing_files) - 10} 个文件")

def main():
    # 连接数据库
    conn = sqlite3.connect(DATABASE_FILE)
    
    # 从TXT加载音频数据到内存
    audio_map = load_audio_paths_from_txt(TXT_FILE_PATH)
    
    # 更新数据库中的音频路径
    if audio_map is not None:
        update_audio_paths(conn, audio_map)
        
        # 验证音频文件是否存在
        verify_audio_files(conn)
    
    conn.close()
    print("所有操作已完成。")

# --- 运行主函数 ---
if __name__ == '__main__':
    main()