#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复初中词表中"poun"的拼写错误
将"poun"改为"pound"
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os

# 配置
DATABASE_FILE = get_database_path()

def fix_pound_spelling():
    """修复数据库中"poun"的拼写错误"""
    print("正在修复数据库中'poun'的拼写错误...")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        # 查找初中词书中的"poun"
        cursor.execute("""
            SELECT w.word_id, w.spelling, w.meaning_cn, wl.list_name, b.book_name 
            FROM Words w 
            JOIN WordLists wl ON w.list_id = wl.list_id 
            JOIN Books b ON wl.book_id = b.book_id 
            WHERE w.spelling = 'poun' AND b.book_name = '初中英语词汇'
        """)
        
        result = cursor.fetchone()
        if result:
            word_id, spelling, meaning_cn, list_name, book_name = result
            print(f"找到错误的单词：{spelling} (ID: {word_id})")
            print(f"位置：{book_name} - {list_name}")
            print(f"含义：{meaning_cn}")
            
            # 更新拼写
            cursor.execute("UPDATE Words SET spelling = 'pound' WHERE word_id = ?", (word_id,))
            conn.commit()
            
            print("✓ 拼写已修复：'poun' → 'pound'")
            
            # 验证修复结果
            cursor.execute("SELECT spelling FROM Words WHERE word_id = ?", (word_id,))
            new_spelling = cursor.fetchone()[0]
            print(f"✓ 验证：单词ID {word_id} 的拼写现在是 '{new_spelling}'")
            
        else:
            print("未找到需要修复的'poun'单词")
            
    except Exception as e:
        print(f"修复过程中出错：{e}")
        conn.rollback()
    finally:
        conn.close()

def check_fix_result():
    """检查修复结果"""
    print("\n检查修复结果...")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        # 检查是否还有"poun"
        cursor.execute("SELECT COUNT(*) FROM Words WHERE spelling = 'poun'")
        poun_count = cursor.fetchone()[0]
        
        # 检查"pound"的数量
        cursor.execute("SELECT COUNT(*) FROM Words WHERE spelling = 'pound'")
        pound_count = cursor.fetchone()[0]
        
        print(f"数据库中'poun'的数量：{poun_count}")
        print(f"数据库中'pound'的数量：{pound_count}")
        
        if poun_count == 0 and pound_count > 0:
            print("✓ 修复成功！所有'poun'都已更正为'pound'")
        else:
            print("⚠ 修复可能不完整，请检查")
            
    except Exception as e:
        print(f"检查过程中出错：{e}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("===== 修复初中词表中'poun'的拼写错误 =====")
    
    # 检查数据库文件是否存在
    if not os.path.exists(DATABASE_FILE):
        print(f"错误：找不到数据库文件 '{DATABASE_FILE}'")
        return
    
    # 执行修复
    fix_pound_spelling()
    
    # 检查结果
    check_fix_result()
    
    print("\n修复操作完成！")

if __name__ == "__main__":
    main() 