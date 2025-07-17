from utils import get_database_connection, get_database_path
import sqlite3

def add_audio_column():
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # 添加 audio_url 列
        cursor.execute('ALTER TABLE Words ADD COLUMN audio_url TEXT')
        
        conn.commit()
        print('成功添加 audio_url 字段！')
        
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print('audio_url 字段已经存在，无需重复添加。')
        else:
            print(f'添加字段时出错: {e}')
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    add_audio_column()