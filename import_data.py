# 导入两个我们需要的Python标准库
import sqlite3 # 用于操作SQLite数据库
import csv     # 用于读取CSV文件

# --- 请在这里配置您的文件名 ---
DATABASE_FILE = 'vocabulary.db'  # 您的数据库文件名
# 使用wordlists文件夹中的CSV文件
# 您可以将任何词库CSV文件放在wordlists文件夹中，然后修改下面的文件名
# 示例文件：wordlists/example_wordlist.csv
CSV_FILE = 'wordlists/junior_high_vocab_random.csv'  # 新东方初中英语词汇文件
# -----------------------------

def create_database_tables():
    """
    创建数据库表结构
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # 创建单词表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Words (
            word_id INTEGER PRIMARY KEY AUTOINCREMENT,
            spelling TEXT NOT NULL,
            meaning_cn TEXT NOT NULL,
            pos TEXT,
            list_id INTEGER NOT NULL
        );
        """)
        
        # 创建错误记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ErrorLogs (
            error_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            error_type TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            error_date DATE NOT NULL,
            FOREIGN KEY (word_id) REFERENCES Words(word_id)
        );
        """)
        
        conn.commit()
        print("数据库表创建成功！")
        
    except sqlite3.Error as e:
        print(f"创建数据库表时出错: {e}")
    finally:
        if conn:
            conn.close()

def import_words_from_csv():
    """
    从CSV文件读取单词并导入到SQLite数据库中。
    """
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        print(f"成功连接到数据库: {DATABASE_FILE}")

        # 打开CSV文件进行读取
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:
            # 新东方CSV文件使用逗号(,)分隔
            csv_reader = csv.reader(file, delimiter=',') 
            
            # 跳过CSV文件的第一行（表头）
            next(csv_reader, None)

            print("开始从CSV文件导入单词...")
            count = 0
            # 打印前几行数据以便调试
            print("CSV文件的前几行数据结构:")
            for i, row in enumerate(csv_reader):
                if i < 3:  # 只打印前3行用于调试
                    print(f"行 {i+1}: {row}")
                
                # 检查行是否有足够的列
                if len(row) < 4:
                    print(f"警告: 行 {i+1} 列数不足，跳过此行: {row}")
                    continue
                    
                try:
                    # 根据junior_high_vocab_random.csv文件的列顺序
                    # 第0列是Word List，第1列是Word，第2列是IPA，第3列是Meaning (CN)，第4列是Example
                    list_id = row[0].replace("List ", "")  # 从"List 1"中提取数字部分
                    spelling = row[1]      # 第1列是单词拼写
                    meaning_cn = row[3]    # 第3列是中文意思
                    
                    # 从中文意思中提取词性
                    # 格式通常是"n. 牙科医生"这样的形式
                    parts = meaning_cn.split(" ", 1)  # 最多分割一次
                    pos = ""
                    if len(parts) > 1 and parts[0].endswith("."):
                        pos = parts[0]  # 提取词性部分，如"n."
                        meaning_cn = parts[1]  # 提取剩余的中文意思部分
                        
                    # 打印处理后的数据，用于调试
                    if i < 3:  # 只打印前3行的处理结果
                        print(f"处理结果: list_id={list_id}, spelling={spelling}, pos={pos}, meaning_cn={meaning_cn}")
                    
                    # 准备SQL插入语句
                    # 现在我们插入拼写、中文意思、词性和列表ID
                    sql = """
                    INSERT INTO Words (spelling, meaning_cn, pos, list_id) 
                    VALUES (?, ?, ?, ?);
                    """
                    # 执行SQL语句 (使用CSV中的list_id)
                    cursor.execute(sql, (spelling, meaning_cn, pos, list_id))
                    count += 1
                except Exception as e:
                    print(f"处理行 {i+1} 时出错: {e}, 行内容: {row}")
                    continue
            
            # 提交所有更改到数据库
            conn.commit()
            print(f"成功导入 {count} 个单词！")
            print("导入过程已成功完成！")

    except FileNotFoundError:
        print(f"错误：找不到文件 '{CSV_FILE}'。请确认文件名是否正确，并且文件在同一个目录下。")
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        # 确保数据库连接被关闭
        if conn:
            conn.close()
            print("数据库连接已关闭。")

# --- 运行主函数 ---
if __name__ == '__main__':
    create_database_tables()  # 首先创建数据库表
    import_words_from_csv()   # 然后导入数据