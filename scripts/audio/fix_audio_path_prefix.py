import sqlite3
import os
import re

def strip_prefix(path):
    if not path:
        return None
    # 只保留文件名
    return os.path.basename(path)

def fix_audio_paths():
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()

    # 获取所有词书
    cursor.execute("SELECT book_id, book_name FROM Books")
    books = cursor.fetchall()

    print("音频路径修复统计：")
    print("=" * 60)

    for book_id, book_name in books:
        # 统计修复前的前缀分布
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN audio_path_uk LIKE 'wordlists/senior_high/media/%' THEN 'senior_high'
                    WHEN audio_path_uk LIKE 'wordlists/junior_high/media/%' THEN 'junior_high'
                    WHEN audio_path_uk IS NULL OR audio_path_uk = '' THEN 'no_audio'
                    ELSE 'other'
                END as path_type,
                COUNT(*) as count
            FROM Words w
            LEFT JOIN WordLists wl ON w.list_id = wl.list_id
            WHERE wl.book_id = ?
            GROUP BY path_type
        """, (book_id,))
        stats = cursor.fetchall()
        print(f"修复前 - 词书: {book_name}")
        for path_type, count in stats:
            print(f"  {path_type}: {count}")

        # 批量修复音频路径
        cursor.execute("""
            SELECT w.word_id, w.audio_path_uk, w.audio_path_us
            FROM Words w
            LEFT JOIN WordLists wl ON w.list_id = wl.list_id
            WHERE wl.book_id = ?
        """, (book_id,))
        words = cursor.fetchall()
        for word_id, audio_uk, audio_us in words:
            new_uk = strip_prefix(audio_uk)
            new_us = strip_prefix(audio_us)
            cursor.execute("UPDATE Words SET audio_path_uk = ?, audio_path_us = ? WHERE word_id = ?", (new_uk, new_us, word_id))
        conn.commit()

        # 统计修复后的前缀分布
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN audio_path_uk LIKE 'wordlists/senior_high/media/%' THEN 'senior_high'
                    WHEN audio_path_uk LIKE 'wordlists/junior_high/media/%' THEN 'junior_high'
                    WHEN audio_path_uk IS NULL OR audio_path_uk = '' THEN 'no_audio'
                    ELSE 'file_name_only'
                END as path_type,
                COUNT(*) as count
            FROM Words w
            LEFT JOIN WordLists wl ON w.list_id = wl.list_id
            WHERE wl.book_id = ?
            GROUP BY path_type
        """, (book_id,))
        stats = cursor.fetchall()
        print(f"修复后 - 词书: {book_name}")
        for path_type, count in stats:
            print(f"  {path_type}: {count}")
        print("-" * 60)

    conn.close()
    print("全部修复完成！")

if __name__ == "__main__":
    fix_audio_paths() 