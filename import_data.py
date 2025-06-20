# 导入两个我们需要的Python标准库
import sqlite3 # 用于操作SQLite数据库
import csv     # 用于读取CSV文件

# --- 请在这里配置您的文件名 ---
DATABASE_FILE = 'vocabulary.db'  # 您的数据库文件名
CSV_FILE = 'anki_words.csv'        # 您的Anki CSV文件名
# -----------------------------

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
            # Anki的CSV通常用分号(;)分隔，如果您的文件用逗号(,)分隔，请将 delimiter=';' 改为 delimiter=','
            csv_reader = csv.reader(file, delimiter=';') 
            
            # 跳过CSV文件的第一行（表头）
            next(csv_reader, None)

            print("开始从CSV文件导入单词...")
            count = 0
            for row in csv_reader:
                # --- 重要：请根据您CSV文件的列顺序修改这里的索引 ---
                # 假设第1列是英文拼写，第2列是中文意思，第3列是音频路径...
                # 如果您的CSV文件顺序不同，请修改 row[0], row[1] 等数字。
                spelling = row[0]
                meaning_cn = row[1]
                # 其他字段可以暂时留空或根据您的CSV文件添加
                # audio_path_us = row[2] 
                
                # 准备SQL插入语句
                # 我们只插入了最重要的几个字段，您可以根据需要增加
                sql = """
                INSERT INTO Words (spelling, meaning_cn, list_id) 
                VALUES (?, ?, ?);
                """
                # 执行SQL语句 (这里的list_id我们暂时硬编码为1，表示导入到第一个List)
                cursor.execute(sql, (spelling, meaning_cn, 1))
                count += 1
            
            # 提交所有更改到数据库
            conn.commit()
            print(f"成功导入 {count} 个单词！")

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
    import_words_from_csv()