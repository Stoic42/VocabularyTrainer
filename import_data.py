# 导入两个我们需要的Python标准库
import sqlite3 # 用于操作SQLite数据库
import csv     # 用于读取CSV文件

# --- 请在这里配置您的文件名 ---
DATABASE_FILE = 'vocabulary.db'  # 您的数据库文件名
# 使用wordlists文件夹中的词汇列表文件
WORDLIST_FILE = 'wordlists/junior_high/初中 乱序 绿宝书.txt'  # 词汇列表文件
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
            audio_path_uk TEXT,  -- 英式发音文件路径
            audio_path_us TEXT,  -- 美式发音文件路径
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

def import_words_from_txt():
    """
    从TXT文件读取单词并导入到SQLite数据库中。
    """
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        print(f"成功连接到数据库: {DATABASE_FILE}")

        # 打开TXT文件进行读取
        with open(WORDLIST_FILE, mode='r', encoding='utf-8') as file:
            print("开始从词汇列表文件导入单词...")
            count = 0
            # 打印前几行数据以便调试
            print("词汇列表文件的前几行数据结构:")
            for i, line in enumerate(file):
                if i < 3:  # 只打印前3行用于调试
                    print(f"行 {i+1}: {line.strip()}")
                
                # 使用制表符分割行
                row = line.strip().split('\t')
                
                # 检查行是否有足够的列（至少需要12列：ID、单词、音标、近义词、中文释义、例句等）
                if len(row) < 12:
                    print(f"警告: 行 {i+1} 列数不足，跳过此行: {row}")
                    continue
                
                # 跳过空行或无效行
                if not row[1].strip() or row[1].strip() == 'Word':
                    continue
                    
                try:
                    spelling = row[1]      # 第2列是单词拼写
                    ipa = row[2]          # 第3列是音标
                    meaning_cn = row[4]    # 第5列是中文意思
                    
                    # 从中文意思中提取词性
                    # 格式通常是"n. 牙科医生"这样的形式
                    parts = meaning_cn.split(" ", 1)  # 最多分割一次
                    pos = ""
                    if len(parts) > 1 and parts[0].endswith("."):
                        pos = parts[0]  # 提取词性部分，如"n."
                        meaning_cn = parts[1]  # 提取剩余的中文意思部分
                    
                    # 提取音频文件路径
                    # 假设音频引用格式为 [sound:cambridge-xxx.mp3]
                    audio_uk = ""
                    audio_us = ""
                    if len(row) >= 12:  # 确保有足够的列
                        uk_ref = row[10].strip()  # 第11列是英音
                        us_ref = row[11].strip()  # 第12列是美音
                        if uk_ref.startswith('[sound:') and uk_ref.endswith(']'):
                            audio_uk = uk_ref[7:-1]  # 移除 [sound: 和 ]
                        if us_ref.startswith('[sound:') and us_ref.endswith(']'):
                            audio_us = us_ref[7:-1]  # 移除 [sound: 和 ]
                        
                    # 打印处理后的数据，用于调试
                    if i < 3:  # 只打印前3行的处理结果
                        print(f"处理结果: spelling={spelling}, ipa={ipa}, pos={pos}, meaning_cn={meaning_cn}, audio_uk={audio_uk}, audio_us={audio_us}")
                    
                    # 准备SQL插入语句
                    sql = """
                    INSERT INTO Words (spelling, meaning_cn, pos, audio_path_uk, audio_path_us, list_id) 
                    VALUES (?, ?, ?, ?, ?, ?);
                    """
                    # 执行SQL语句
                    cursor.execute(sql, (spelling, meaning_cn, pos, audio_uk, audio_us, 1))  # 暂时将所有单词设为list_id=1
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
    import_words_from_txt()   # 然后导入数据