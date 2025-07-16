from utils import get_database_connection, get_database_path
import sqlite3
import os

def get_db_connection():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建数据库文件的路径
    db_path = os.path.join(current_dir, get_database_path())
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    # 设置行工厂为字典，这样查询结果会以字典形式返回
    conn.row_factory = sqlite3.Row
    return conn

def add_detail_columns():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查并添加详情字段
    columns_to_add = [
        "derivatives TEXT",          # 派生词
        "root_etymology TEXT",       # 词根词源
        "mnemonic TEXT",            # 联想记忆
        "comparison TEXT",           # 词义辨析
        "collocation TEXT",          # 搭配用法
        "exam_sentence TEXT",        # 真题例句
        "exam_year_source TEXT",     # 真题出处
        "exam_options TEXT",         # 选项
        "exam_explanation TEXT",     # 解析
        "tips TEXT"                  # 提示
    ]
    
    # 获取当前表结构
    cursor.execute("PRAGMA table_info(Words)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    
    # 添加缺失的列
    for column_def in columns_to_add:
        column_name = column_def.split()[0]
        if column_name not in existing_columns:
            try:
                alter_sql = f"ALTER TABLE Words ADD COLUMN {column_def}"
                cursor.execute(alter_sql)
                print(f"已添加列: {column_def}")
            except sqlite3.Error as e:
                print(f"添加列 {column_def} 时出错: {e}")
    
    conn.commit()
    conn.close()
    print("详情字段添加完成！")

if __name__ == "__main__":
    add_detail_columns()