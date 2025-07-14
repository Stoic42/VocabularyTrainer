import sqlite3
import csv
import os
import sqlite3

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
    
    # 创建词书表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_name TEXT NOT NULL UNIQUE
    );
    """)
    
    # 创建单元表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS WordLists (
        list_id INTEGER PRIMARY KEY AUTOINCREMENT,
        list_name TEXT NOT NULL,
        book_id INTEGER,
        FOREIGN KEY (book_id) REFERENCES Books(book_id)
    );
    """)
    
    # 创建单词表，修改外键引用
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Words (
        word_id INTEGER PRIMARY KEY AUTOINCREMENT,
        spelling TEXT NOT NULL,
        meaning_cn TEXT,
        pos TEXT,
        audio_path_uk TEXT,
        audio_path_us TEXT,
        list_id INTEGER,
        FOREIGN KEY (list_id) REFERENCES WordLists(list_id)
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
        FOREIGN KEY (word_id) REFERENCES Words(word_id),
        FOREIGN KEY (student_id) REFERENCES Users(id)
    );
    """)
    
    # 创建用户表
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
    第二步：扫描CSV文件，创建词书和单元，合并音频数据，并导入数据库。
    """
    print(f"正在从 '{csv_path}' 导入单词并合并音频数据...")
    cursor = conn.cursor()
    count = 0
    try:
        # 创建初中词书
        book_name = "初中英语词汇"
        cursor.execute("INSERT INTO Books (book_name) VALUES (?)", (book_name,))
        book_id = cursor.lastrowid
        print(f"创建词书：{book_name} (ID: {book_id})")
        
        # 用于记录已创建的单元
        created_lists = set()
        
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader, None) # 跳过表头

            for i, row in enumerate(csv_reader):
                if len(row) < 4:
                    continue

                # 从CSV获取基础数据
                list_id_str = row[0].replace("List", "").strip()
                list_num = int(list_id_str)
                spelling = row[1].strip()
                full_meaning = row[3].strip()

                # 如果这个单元还没有创建，就创建它
                if list_num not in created_lists:
                    list_name = f"Unit {list_num}"
                    cursor.execute(
                        "INSERT INTO WordLists (list_name, book_id) VALUES (?, ?)",
                        (list_name, book_id)
                    )
                    list_id = cursor.lastrowid
                    created_lists.add(list_num)
                    print(f"创建单元：{list_name} (ID: {list_id})")
                else:
                    # 获取已创建的单元ID
                    cursor.execute(
                        "SELECT list_id FROM WordLists WHERE book_id = ? AND list_name = ?",
                        (book_id, f"Unit {list_num}")
                    )
                    list_id = cursor.fetchone()[0]

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
    # 连接数据库，如果不存在则创建
    conn = sqlite3.connect(DATABASE_FILE)
    
    # 1. 创建表（如果不存在）
    create_tables(conn)
    
    # 2. 删除特定词书的数据，而不是整个数据库
    cursor = conn.cursor()
    book_name = "初中英语词汇"
    cursor.execute("SELECT book_id FROM Books WHERE book_name = ?", (book_name,))
    book_result = cursor.fetchone()
    
    if book_result:
        book_id = book_result[0]
        print(f"找到词书：{book_name} (ID: {book_id})，正在删除相关数据...")
        
        # 获取该词书下的所有单元
        cursor.execute("SELECT list_id FROM WordLists WHERE book_id = ?",(book_id,))
        list_results = cursor.fetchall()
        
        # 删除这些单元下的所有单词
        for list_result in list_results:
            list_id = list_result[0]
            cursor.execute("DELETE FROM Words WHERE list_id = ?", (list_id,))
        
        # 删除这些单元
        cursor.execute("DELETE FROM WordLists WHERE book_id = ?",(book_id,))
        
        # 删除词书
        cursor.execute("DELETE FROM Books WHERE book_id = ?",(book_id,))
        
        conn.commit()
        print(f"已删除词书 {book_name} 及其相关数据")
    else:
        print(f"未找到词书：{book_name}，将创建新词书")
    
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