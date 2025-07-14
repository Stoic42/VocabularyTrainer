import os
import csv

# 定义文件路径
CSV_FILE_PATH = 'wordlists/junior_high/junior_high_vocab_random.csv'

# 检查CSV文件是否存在
def check_and_create_csv():
    # 确保目录存在
    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
    
    # 检查文件是否存在
    if not os.path.exists(CSV_FILE_PATH):
        print(f"CSV文件 '{CSV_FILE_PATH}' 不存在，正在创建示例文件...")
        
        # 创建示例数据
        sample_data = [
            ['List', 'Word', 'Phonetic', 'Meaning'],
            ['List1', 'hello', '/həˈləʊ/', 'n.问候；打招呼'],
            ['List1', 'world', '/wɜːld/', 'n.世界；地球'],
            ['List2', 'apple', '/ˈæpl/', 'n.苹果'],
            ['List2', 'banana', '/bəˈnɑːnə/', 'n.香蕉'],
        ]
        
        # 写入CSV文件
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerows(sample_data)
            
        print(f"示例CSV文件已创建: '{CSV_FILE_PATH}'")
        print("注意：这只是一个示例文件，请替换为实际的单词数据。")
    else:
        print(f"CSV文件已存在: '{CSV_FILE_PATH}'")

# 主函数
if __name__ == '__main__':
    check_and_create_csv()