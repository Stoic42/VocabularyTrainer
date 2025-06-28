import sqlite3

# 连接到数据库
conn = sqlite3.connect('vocabulary.db')
cursor = conn.cursor()

# 查询所有表名
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()

# 将结果写入文件
with open('d:/Projects/VocabularyTrainer/db_tables.txt', 'w', encoding='utf-8') as f:
    f.write('数据库中的表:\n')
    for table in tables:
        f.write(f'{table[0]}\n')
        
        # 查询表结构
        try:
            cursor.execute(f'PRAGMA table_info({table[0]})')
            columns = cursor.fetchall()
            f.write(f'  表结构:\n')
            for col in columns:
                f.write(f'    {col[1]} ({col[2]})\n')
        except Exception as e:
            f.write(f'  无法获取表结构: {str(e)}\n')
        
        f.write('\n')

# 关闭连接
conn.close()

print(f'数据库表结构已写入: d:/Projects/VocabularyTrainer/db_tables.txt')