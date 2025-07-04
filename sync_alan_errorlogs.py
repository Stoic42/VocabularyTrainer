import sqlite3
import os

def fetch_alan_errorlogs(classroom_db_path, student_id):
    conn = sqlite3.connect(classroom_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ErrorLogs WHERE student_id=?", (student_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def fetch_existing_errorlogs(main_db_path, student_id):
    conn = sqlite3.connect(main_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT word_id, error_type, error_date FROM ErrorLogs WHERE student_id=?", (student_id,))
    records = set(cursor.fetchall())
    conn.close()
    return records

def insert_new_errorlogs(main_db_path, new_records):
    conn = sqlite3.connect(main_db_path)
    cursor = conn.cursor()
    inserted = 0
    for rec in new_records:
        # rec: (error_id, student_id, word_id, error_type, student_answer, error_date)
        # error_id 是自增主键，插入时应忽略
        cursor.execute("INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date) VALUES (?, ?, ?, ?, ?)",
                       (rec[1], rec[2], rec[3], rec[4], rec[5]))
        inserted += 1
    conn.commit()
    conn.close()
    return inserted

def main():
    classroom_db = os.path.join('Alan', 'vocabulary_classroom.db')
    main_db = 'vocabulary.db'
    alan_id = 3
    print("读取教室数据库 Alan 的 ErrorLogs...")
    alan_records = fetch_alan_errorlogs(classroom_db, alan_id)
    print(f"教室数据库 Alan 的 ErrorLogs 记录数: {len(alan_records)}")
    print("读取当前数据库已存在的 ErrorLogs...")
    existing = fetch_existing_errorlogs(main_db, alan_id)
    print(f"当前数据库 Alan 的 ErrorLogs 记录数: {len(existing)}")
    # 以 (word_id, error_type, error_date) 作为唯一性判断，避免重复
    existing_keys = set(existing)
    new_records = [rec for rec in alan_records if (rec[2], rec[3], rec[5]) not in existing_keys]
    print(f"需要插入的新记录数: {len(new_records)}")
    if new_records:
        inserted = insert_new_errorlogs(main_db, new_records)
        print(f"已插入 {inserted} 条新记录。")
    else:
        print("没有需要插入的新记录。")

if __name__ == "__main__":
    main() 