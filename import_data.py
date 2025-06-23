import sqlite3
import csv
import os

# --- 配置区 ---
DATABASE_FILE = 'vocabulary.db'
# 主要数据源 (结构好，但缺音频)
CSV_FILE_PATH = 'wordlists/junior_high/junior_high_vocab_random.csv'
# 音频数据源 (结构乱，但有音频)
TXT_FILE_PATH = 'wordlists/junior_high/初中 乱序 绿宝书.txt'
# ----------------

def create_tables(conn):
    """创建数据库表，如果它们不存在的话"""
    cursor = conn.cursor()
    # 我们之前的建表语句非常完美，直接使用
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Words (
        word_id INTEGER PRIMARY KEY AUTOINCREMENT,
        spelling TEXT NOT NULL,
        meaning_cn TEXT,
        pos TEXT,
        audio_path_uk TEXT,
        audio_path_us TEXT,
        list_id INTEGER
    );
    """)
    
    # 创建错误日志表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ErrorLogs (
        error_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        word_id INTEGER,
        error_type TEXT,
        student_answer TEXT,
        error_date TEXT,
        FOREIGN KEY (word_id) REFERENCES Words(word_id)
    );
    """)
    
    # 新增：创建用户表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student', 'admin'))
    );
    """)
    
    conn.commit()
    print("数据库表已确认或创建。")

def load_audio_paths_from_txt(txt_path):
    """
    第一步：扫描TXT文件，建立一个 "单词 -> 音频路径" 的映射字典。
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

def import_merged_data(conn, csv_path, audio_map):
    """
    第二步：扫描CSV文件，合并音频数据，并导入数据库。
    """
    print(f"正在从 '{csv_path}' 导入单词并合并音频数据...")
    cursor = conn.cursor()
    count = 0
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader, None) # 跳过表头

            for i, row in enumerate(csv_reader):
                if len(row) < 4:
                    continue

                # 从CSV获取基础数据
                list_id_str = row[0].replace("List", "").strip()
                list_id = int(list_id_str)
                spelling = row[1].strip()
                full_meaning = row[3].strip()

                # 解析词性和意思
                pos = ""
                meaning_cn = full_meaning
                parts = full_meaning.split('.', 1)
                if len(parts) == 2 and len(parts[0]) < 5:
                    pos = parts[0] + "."
                    meaning_cn = parts[1].strip()

                # --- 关键的合并步骤 ---
                # 从内存中的audio_map查找音频路径
                spelling_key = spelling.lower()
                audio_data = audio_map.get(spelling_key, {'uk': '', 'us': ''})
                audio_path_uk = audio_data['uk']
                audio_path_us = audio_data['us']
                
                # 插入完整数据到数据库
                sql = "INSERT INTO Words (spelling, meaning_cn, pos, audio_path_uk, audio_path_us, list_id) VALUES (?, ?, ?, ?, ?, ?);"
                cursor.execute(sql, (spelling, meaning_cn, pos, audio_path_uk, audio_path_us, list_id))
                count += 1
        
        conn.commit()
        print(f"数据合并与导入完成！成功导入 {count} 个单词。")

    except FileNotFoundError:
        print(f"错误: 找不到主数据文件 '{csv_path}'")
    except Exception as e:
        print(f"导入过程中出错: {e}")


def main():
    """主执行函数"""
    # 0. 删除旧数据库，确保全新导入
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f"已删除旧数据库 '{DATABASE_FILE}'。")

    conn = sqlite3.connect(DATABASE_FILE)
    
    # 1. 创建表
    create_tables(conn)
    
    # 2. 从TXT加载音频数据到内存
    audio_map = load_audio_paths_from_txt(TXT_FILE_PATH)
    
    # 3. 如果音频数据加载成功，则继续合并导入
    if audio_map is not None:
        import_merged_data(conn, CSV_FILE_PATH, audio_map)
    
    conn.close()
    print("所有操作已完成。")


# --- 运行主函数 ---
if __name__ == '__main__':
    main()