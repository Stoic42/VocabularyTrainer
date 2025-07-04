import sqlite3
import os

def check_database_structure():
    """检查数据库结构和ErrorLogs表内容"""
    
    # 检查当前数据库
    print("=== 当前数据库结构 ===")
    if os.path.exists('vocabulary.db'):
        conn = sqlite3.connect('vocabulary.db')
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"当前数据库中的表: {[table[0] for table in tables]}")
        
        # 检查ErrorLogs表结构
        if any('ErrorLogs' in table for table in tables):
            cursor.execute("PRAGMA table_info(ErrorLogs)")
            columns = cursor.fetchall()
            print(f"\nErrorLogs表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # 获取ErrorLogs记录数
            cursor.execute("SELECT COUNT(*) FROM ErrorLogs")
            count = cursor.fetchone()[0]
            print(f"\nErrorLogs表记录数: {count}")
            
            # 获取最近的几条记录
            cursor.execute("SELECT * FROM ErrorLogs ORDER BY timestamp DESC LIMIT 5")
            recent_records = cursor.fetchall()
            print(f"\n最近的5条ErrorLogs记录:")
            for record in recent_records:
                print(f"  {record}")
        else:
            print("当前数据库中没有ErrorLogs表")
        
        conn.close()
    else:
        print("当前目录下没有vocabulary.db文件")

if __name__ == "__main__":
    check_database_structure()