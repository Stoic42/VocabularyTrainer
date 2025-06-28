import sqlite3
import os

# 数据库文件路径
DATABASE_FILE = 'vocabulary.db'

def main():
    try:
        # 连接到数据库
        print(f"尝试连接数据库: {os.path.abspath(DATABASE_FILE)}")
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print("数据库连接成功")
        
        # 查询所有词书
        cursor.execute("SELECT book_id, book_name FROM Books ORDER BY book_id")
        books = cursor.fetchall()
        
        print("词书和列表名称格式检查：")
        print("-" * 50)
        
        # 遍历每本词书
        for book in books:
            book_id = book['book_id']
            book_name = book['book_name']
            
            print(f"\n词书ID: {book_id}, 名称: {book_name}")
            print("-" * 30)
            
            # 查询该词书下的所有列表
            cursor.execute(
                "SELECT list_id, list_name FROM WordLists WHERE book_id = ? ORDER BY list_id", 
                (book_id,)
            )
            lists = cursor.fetchall()
            
            if lists:
                print("列表ID\t列表名称")
                print("-" * 30)
                for list_item in lists:
                    print(f"{list_item['list_id']}\t{list_item['list_name']}")
            else:
                print("该词书下没有列表")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()