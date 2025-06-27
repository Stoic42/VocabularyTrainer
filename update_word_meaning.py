import sqlite3
import os

# 连接到数据库
DATABASE_FILE = 'd:\\Projects\\VocabularyTrainer\\vocabulary.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 查询单词信息
def get_word_info(spelling):
    conn = get_db_connection()
    query = "SELECT word_id, spelling, meaning_cn, pos, list_id FROM Words WHERE spelling = ?"
    row = conn.execute(query, (spelling,)).fetchone()
    conn.close()
    
    if row:
        return dict(row)
    else:
        return None

# 更新单词意思
def update_word_meaning(word_id, new_meaning, new_pos=None):
    conn = get_db_connection()
    
    if new_pos:
        update_query = "UPDATE Words SET meaning_cn = ?, pos = ? WHERE word_id = ?"
        conn.execute(update_query, (new_meaning, new_pos, word_id))
    else:
        update_query = "UPDATE Words SET meaning_cn = ? WHERE word_id = ?"
        conn.execute(update_query, (new_meaning, word_id))
    
    conn.commit()
    conn.close()
    return True

# 主函数
def main():
    print("===== 单词意思更新工具 =====")
    print("此工具用于更新数据库中单词的意思和词性")
    print("-" * 50)
    
    # 要更新的单词列表 - 格式: [单词, 新意思, 新词性]
    words_to_update = [
        # 示例: ['two-thirds', '三分之二', 'n.'],
        # 在下面添加更多单词
        ['two-thirds', '三分之二', 'n.'],
        # 可以添加更多需要修改的单词
    ]
    
    results = []
    
    for word_data in words_to_update:
        spelling = word_data[0]
        new_meaning = word_data[1]
        new_pos = word_data[2] if len(word_data) > 2 else None
        
        print(f"\n处理单词: {spelling}")
        
        # 查询单词信息
        word_info = get_word_info(spelling)
        
        if not word_info:
            print(f"单词 '{spelling}' 在数据库中不存在")
            results.append({'spelling': spelling, 'status': 'not_found'})
            continue
        
        print(f"当前意思: {word_info['meaning_cn']}")
        print(f"当前词性: {word_info['pos']}")
        
        # 更新单词意思
        try:
            update_word_meaning(word_info['word_id'], new_meaning, new_pos)
            
            # 验证更新
            updated_info = get_word_info(spelling)
            print("更新后:")
            print(f"意思: {updated_info['meaning_cn']}")
            print(f"词性: {updated_info['pos']}")
            
            results.append({
                'spelling': spelling,
                'old_meaning': word_info['meaning_cn'],
                'new_meaning': updated_info['meaning_cn'],
                'old_pos': word_info['pos'],
                'new_pos': updated_info['pos'],
                'status': 'updated'
            })
        except Exception as e:
            print(f"更新单词 '{spelling}' 时出错: {str(e)}")
            results.append({'spelling': spelling, 'status': 'error', 'error': str(e)})
    
    # 显示结果摘要
    print("\n===== 更新结果摘要 =====")
    for result in results:
        status = result['status']
        word = result['spelling']
        
        if status == 'updated':
            print(f"✓ {word}: 已更新 - 意思: '{result['old_meaning']}' -> '{result['new_meaning']}', 词性: '{result['old_pos']}' -> '{result['new_pos']}'")
        elif status == 'not_found':
            print(f"✗ {word}: 单词在数据库中不存在")
        else:
            print(f"✗ {word}: 更新失败 - {result.get('error', '未知错误')}")
    
    print("\n更新完成。请重启应用以应用更改。")

if __name__ == "__main__":
    main()