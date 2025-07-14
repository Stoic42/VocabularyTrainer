import os
import sqlite3
import subprocess
import sys

# 定义文件路径
DATABASE_FILE = 'vocabulary.db'
CSV_FILE_PATH = 'wordlists/junior_high/junior_high_vocab_random.csv'
TXT_FILE_PATH = 'wordlists/junior_high/初中 乱序 绿宝书.txt'

# 检查文件是否存在
def check_file_exists(file_path, file_description):
    if os.path.exists(file_path):
        print(f"✓ {file_description}已存在: '{file_path}'")
        return True
    else:
        print(f"✗ {file_description}不存在: '{file_path}'")
        return False

# 创建示例TXT文件
def create_sample_txt():
    os.makedirs(os.path.dirname(TXT_FILE_PATH), exist_ok=True)
    
    with open(TXT_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write("1\thello\t/həˈləʊ/\t你好\t\t\t\t\t\t\t[sound:hello_uk.mp3]\t[sound:hello_us.mp3]\n")
        file.write("2\tworld\t/wɜːld/\t世界\t\t\t\t\t\t\t[sound:world_uk.mp3]\t[sound:world_us.mp3]\n")
        file.write("3\tapple\t/ˈæpl/\t苹果\t\t\t\t\t\t\t[sound:apple_uk.mp3]\t[sound:apple_us.mp3]\n")
        file.write("4\tbanana\t/bəˈnɑːnə/\t香蕉\t\t\t\t\t\t\t[sound:banana_uk.mp3]\t[sound:banana_us.mp3]\n")
    
    print(f"✓ 已创建示例TXT文件: '{TXT_FILE_PATH}'")
    print("  注意：这只是一个示例文件，请替换为实际的单词数据。")

# 主函数
def main():
    print("===== Lumi单词训练营 - 初始化工具 =====")
    print("此工具将帮助您完成应用的初始化设置。")
    
    # 检查数据库文件
    db_exists = check_file_exists(DATABASE_FILE, "数据库文件")
    
    # 检查CSV文件
    csv_exists = check_file_exists(CSV_FILE_PATH, "CSV数据文件")
    if not csv_exists:
        print("\n正在运行check_and_create_csv.py创建示例CSV文件...")
        try:
            subprocess.run([sys.executable, 'check_and_create_csv.py'], check=True)
            csv_exists = True
        except subprocess.CalledProcessError:
            print("创建CSV文件失败，请手动运行check_and_create_csv.py")
    
    # 检查TXT文件
    txt_exists = check_file_exists(TXT_FILE_PATH, "TXT音频数据文件")
    if not txt_exists:
        print("\n正在创建示例TXT文件...")
        create_sample_txt()
        txt_exists = True
    
    # 如果数据库不存在，或者用户选择重新初始化
    if not db_exists or input("\n是否要重新初始化数据库？(y/n): ").lower() == 'y':
        if csv_exists and txt_exists:
            print("\n正在运行import_data.py初始化数据库...")
            try:
                subprocess.run([sys.executable, 'import_data.py'], check=True)
                print("\n✓ 数据库初始化成功！")
            except subprocess.CalledProcessError:
                print("\n✗ 数据库初始化失败，请检查错误信息并手动运行import_data.py")
        else:
            print("\n✗ 无法初始化数据库：缺少必要的数据文件")
    
    # 检查requirements.txt并安装依赖
    if check_file_exists('requirements.txt', "依赖文件"):
        if input("\n是否要安装依赖？(y/n): ").lower() == 'y':
            print("\n正在安装依赖...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
                print("\n✓ 依赖安装成功！")
            except subprocess.CalledProcessError:
                print("\n✗ 依赖安装失败，请手动运行pip install -r requirements.txt")
    
    print("\n===== 初始化完成 =====")
    print("您现在可以运行'flask run --host=0.0.0.0'启动应用。")
    print("默认管理员账户：用户名'admin'，密码'admin123'")

# 运行主函数
if __name__ == '__main__':
    main()