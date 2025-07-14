from utils import get_database_connection, get_database_path
import sqlite3
import csv
import os
import re

# --- 配置区 ---
DATABASE_FILE = get_database_path()
# 高中词汇CSV文件路径
CSV_FILE_PATH = 'wordlists/senior_high/senior_high_complete.csv'
# ----------------

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables_if_not_exists(conn):
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
    
    # 创建单词表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Words (
        word_id INTEGER PRIMARY KEY AUTOINCREMENT,
        spelling TEXT NOT NULL,
        meaning_cn TEXT,
        pos TEXT,
        ipa TEXT,
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

def import_senior_high_data(conn, csv_path):
    """从CSV文件导入高中词汇数据到数据库"""
    print(f"正在从 '{csv_path}' 导入高中词汇数据...")
    cursor = conn.cursor()
    count = 0
    try:
        # 创建高中词书
        book_name = "高中英语词汇"
        cursor.execute("SELECT book_id FROM Books WHERE book_name = ?", (book_name,))
        book_result = cursor.fetchone()
        
        if book_result:
            book_id = book_result[0]
            print(f"使用已存在的词书：{book_name} (ID: {book_id})")
        else:
            cursor.execute("INSERT INTO Books (book_name) VALUES (?)", (book_name,))
            book_id = cursor.lastrowid
            print(f"创建词书：{book_name} (ID: {book_id})")
        
        # 用于记录已创建的单元
        created_lists = {}
        
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader, None)  # 跳过表头

            for i, row in enumerate(csv_reader):
                if len(row) < 4:
                    continue
                
                # 从CSV获取基础数据
                list_name = row[0].strip()
                spelling = row[1].strip()
                ipa = row[2].strip()
                meaning_cn = row[3].strip()
                example = row[4].strip() if len(row) > 4 else ""
                
                # 跳过词缀和词根行
                if list_name in ["前缀", "后缀", "词根"]:
                    continue
                
                # 提取词性
                pos = ""
                if meaning_cn:
                    # 尝试从meaning_cn中提取词性
                    pos_match = re.match(r'^([a-z]+\.)\s', meaning_cn)
                    if pos_match:
                        pos = pos_match.group(1)
                
                # 处理单元名称
                if list_name.startswith("Word List"):
                    list_num = list_name.replace("Word List", "").strip()
                    list_name = f"Unit {list_num}"
                
                # 如果这个单元还没有创建，就创建它
                if list_name not in created_lists:
                    cursor.execute(
                        "SELECT list_id FROM WordLists WHERE list_name = ? AND book_id = ?",
                        (list_name, book_id)
                    )
                    list_result = cursor.fetchone()
                    
                    if list_result:
                        list_id = list_result[0]
                        created_lists[list_name] = list_id
                        print(f"使用已存在的单元：{list_name} (ID: {list_id})")
                    else:
                        cursor.execute(
                            "INSERT INTO WordLists (list_name, book_id) VALUES (?, ?)",
                            (list_name, book_id)
                        )
                        list_id = cursor.lastrowid
                        created_lists[list_name] = list_id
                        print(f"创建单元：{list_name} (ID: {list_id})")
                else:
                    list_id = created_lists[list_name]
                
                # 检查单词是否已存在
                cursor.execute(
                    "SELECT word_id FROM Words WHERE spelling = ? AND list_id = ?",
                    (spelling, list_id)
                )
                word_result = cursor.fetchone()
                
                if word_result:
                    print(f"跳过已存在的单词：{spelling}")
                    continue
                
                # 插入单词数据到数据库
                sql = "INSERT INTO Words (spelling, meaning_cn, pos, ipa, audio_path_uk, audio_path_us, list_id) VALUES (?, ?, ?, ?, ?, ?, ?);"
                cursor.execute(sql, (spelling, meaning_cn, pos, ipa, "", "", list_id))
                count += 1
                
                if count % 100 == 0:
                    print(f"已导入 {count} 个单词...")
        
        conn.commit()
        print(f"数据导入完成！成功导入 {count} 个单词。")

    except FileNotFoundError:
        print(f"错误: 找不到CSV文件 '{csv_path}'")
    except Exception as e:
        print(f"导入过程中出错: {e}")
        conn.rollback()

def main():
    """主执行函数"""
    # 检查CSV文件是否存在
    if not os.path.exists(CSV_FILE_PATH):
        print(f"错误: 找不到CSV文件 '{CSV_FILE_PATH}'")
        return
    
    # 检查数据库是否存在，如果不存在则创建
    db_exists = os.path.exists(DATABASE_FILE)
    
    conn = get_db_connection()
    
    # 创建表（如果不存在）
    create_tables_if_not_exists(conn)
    
    # 导入高中词汇数据
    import_senior_high_data(conn, CSV_FILE_PATH)
    
    conn.close()
    print("所有操作已完成。")

# --- 运行主函数 ---
if __name__ == '__main__':
    main()