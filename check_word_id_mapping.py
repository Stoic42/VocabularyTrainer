import sqlite3
import os
from datetime import datetime

# 获取当前时间作为报告文件名的一部分
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# 设置数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary.db")

# 从HTML文件中提取的错词列表
alan_error_words = [
    "diary", "glue", "cotton", "under", "terrible", "careful", "several", "marathon", 
    "plastic", "purpose", "discovery", "seal", "reveal", "association", "clothes", 
    "convenient", "Atlantic", "author", "escalator", "nature", "cabbage", "ground", 
    "bill", "globe", "pain", "cap", "age", "Jew", "vocabulary", "dialogue", 
    "project", "list", "weekend", "matter", "pear", "positive", "hallway", "enemy", "schoolbag"
]

# ErrorLogs中的单词ID
error_word_ids = [
    1186, 1175, 1163, 1185, 1180, 1183, 1197, 1204, 1173, 1215, 1208, 1172, 1203, 1217, 1213,
    1179, 1233, 1222, 1256, 1276, 1228, 1252, 1238, 1225, 1237, 1253, 1248, 1223, 1277, 1234,
    1272, 1278, 1261, 1267, 1242, 1239, 1230, 1274, 1264
]

# 新的单词ID（从Unit 21和Unit 22中找到的）
new_word_ids = {
    "diary": 18008, "glue": 17997, "cotton": 17985, "under": 18007, "terrible": 18002, 
    "careful": 18005, "several": 18019, "marathon": 18026, "plastic": 17995, "purpose": 18037, 
    "discovery": 18030, "seal": 17994, "reveal": 18025, "association": 18039, "clothes": 18035, 
    "convenient": 18001, "Atlantic": 18055, "author": 18044, "escalator": 18078, "nature": 18098, 
    "cabbage": 18050, "ground": 18074, "bill": 18060, "globe": 18047, "pain": 18059, 
    "cap": 18075, "age": 18070, "Jew": 18045, "vocabulary": 18099, "dialogue": 18056, 
    "project": 18094, "list": 18100, "weekend": 18083, "matter": 18089, "pear": 18064, 
    "positive": 18061, "hallway": 18052, "enemy": 18096, "schoolbag": 18086
}

# 创建报告文件
report_file = f"word_id_mapping_report_{current_time}.txt"
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), report_file)

try:
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 打开报告文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("单词ID映射关系报告\n")
        f.write("================\n\n")
        
        # 检查数据库中是否有旧的单词ID记录
        f.write("检查数据库中是否有旧的单词ID记录:\n")
        for word_id in error_word_ids:
            cursor.execute("SELECT * FROM Words WHERE word_id = ?", (word_id,))
            result = cursor.fetchone()
            if result:
                f.write(f"单词ID {word_id} 在Words表中存在\n")
            else:
                f.write(f"单词ID {word_id} 在Words表中不存在\n")
        
        f.write("\n")
        
        # 尝试查找旧单词ID和新单词ID之间的映射关系
        f.write("尝试查找旧单词ID和新单词ID之间的映射关系:\n")
        
        # 检查是否有备份表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%Words%'")
        tables = cursor.fetchall()
        f.write(f"找到以下与Words相关的表: {[table[0] for table in tables]}\n\n")
        
        # 检查是否有旧的单词记录
        f.write("在数据库中查找旧的单词记录:\n")
        for i, (word, word_id) in enumerate(zip(alan_error_words, error_word_ids)):
            # 在所有表中查找这个单词
            found = False
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE spelling LIKE ?", (f"%{word}%",))
                    results = cursor.fetchall()
                    if results:
                        f.write(f"单词 '{word}' (错误ID: {word_id}) 在表 {table_name} 中找到 {len(results)} 条记录\n")
                        for result in results:
                            f.write(f"  记录: {result}\n")
                        found = True
                except sqlite3.Error as e:
                    f.write(f"查询表 {table_name} 时出错: {e}\n")
            
            if not found:
                f.write(f"单词 '{word}' (错误ID: {word_id}) 在所有表中均未找到\n")
        
        f.write("\n")
        
        # 尝试建立旧ID和新ID的映射关系
        f.write("尝试建立旧ID和新ID的映射关系:\n")
        for i, (old_id, word) in enumerate(zip(error_word_ids, alan_error_words)):
            new_id = new_word_ids.get(word)
            f.write(f"{i+1}. 单词: {word}, 旧ID: {old_id}, 新ID: {new_id}\n")
        
        f.write("\n")
        
        # 检查是否有任何表记录了单词ID的变更历史
        f.write("检查是否有任何表记录了单词ID的变更历史:\n")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = cursor.fetchall()
        for table in all_tables:
            table_name = table[0]
            if 'history' in table_name.lower() or 'log' in table_name.lower() or 'backup' in table_name.lower() or 'old' in table_name.lower():
                f.write(f"可能包含历史记录的表: {table_name}\n")
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                    results = cursor.fetchall()
                    if results:
                        f.write(f"  表 {table_name} 的前5条记录: {results}\n")
                except sqlite3.Error as e:
                    f.write(f"  查询表 {table_name} 时出错: {e}\n")
        
        f.write("\n")
        
        # 检查数据库中是否有任何与重新导入单词书相关的记录
        f.write("检查数据库中是否有任何与重新导入单词书相关的记录:\n")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%import%'")
        import_tables = cursor.fetchall()
        for table in import_tables:
            table_name = table[0]
            f.write(f"可能与导入相关的表: {table_name}\n")
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                results = cursor.fetchall()
                if results:
                    f.write(f"  表 {table_name} 的前5条记录: {results}\n")
            except sqlite3.Error as e:
                f.write(f"  查询表 {table_name} 时出错: {e}\n")
        
        # 总结发现
        f.write("\n总结发现:\n")
        f.write("1. ErrorLogs表中Alan在2025-06-25的39条错词记录使用的单词ID (1163-1278) 在当前Words表中不存在\n")
        f.write("2. 这些单词在当前Words表中有新的ID (17985-18100)，来自初中单词书的Unit 21和Unit 22\n")
        f.write("3. 这表明单词书可能被重新导入，导致单词ID发生了变化\n")
        f.write("4. 由于ErrorLogs表中仍然引用旧的单词ID，而这些ID在当前Words表中不存在，导致错词记录无法正确显示\n")
        
        f.write("\n解决方案建议:\n")
        f.write("1. 更新ErrorLogs表中的word_id，将旧ID映射到新ID\n")
        f.write("2. 在未来的单词书重新导入过程中，保留单词ID的映射关系\n")
        f.write("3. 考虑使用更稳定的标识符（如单词拼写）作为外键，而不仅仅依赖自增ID\n")
        
        f.write("\n报告生成完成\n")
    
    print(f"报告已生成: {report_path}")

except sqlite3.Error as e:
    print(f"数据库错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    if 'conn' in locals():
        conn.close()