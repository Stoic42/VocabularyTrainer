import csv
import re
import os
from bs4 import BeautifulSoup

# --- 配置区 ---
# 输入文件：您从Anki导出的、包含HTML和媒体信息的高中词库TXT文件
INPUT_TXT_FILE = r'wordlists\senior_high\新东方高中词汇乱序绿宝书plain text.txt'

# 输出文件：我们最终生成的、干净的标准CSV文件
OUTPUT_CSV_FILE = r'wordlists\senior_high\highschool_standard.csv'

# 定义我们标准CSV的表头
CSV_HEADER = [
    'list_id',
    'spelling',
    'ipa_us',
    'pos_and_meaning_cn',
    'definition_en',
    'example_en',
    'audio_path_uk',
    'audio_path_us'
]
# ----------------

def clean_html(html_content):
    """使用BeautifulSoup清理HTML并提取关键信息"""
    if not html_content or not html_content.strip():
        return "", ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取第一个英文定义
    first_def_element = soup.find('b', class_='def')
    definition_en = first_def_element.get_text(strip=True) if first_def_element else ""

    # 提取第一个例句
    first_examp_element = soup.find('div', class_='examp')
    example_en = first_examp_element.get_text(strip=True) if first_examp_element else ""
    
    return definition_en, example_en

def parse_anki_txt_to_standard_csv():
    """
    读取复杂的Anki TXT文件，解析HTML内容，并转换为标准的CSV格式。
    """
    print(f"开始转换文件: {INPUT_TXT_FILE}")
    
    if not os.path.exists(INPUT_TXT_FILE):
        print(f"错误：输入文件不存在！请检查路径: {INPUT_TXT_FILE}")
        return

    processed_rows = []
    
    try:
        with open(INPUT_TXT_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for i, row in enumerate(reader):
                # 跳过注释行和格式不正确的行
                if not row or row[0].startswith('#'):
                    continue

                try:
                    # --- 数据提取和清洗 ---
                    spelling = row[0].strip()
                    pos_and_meaning_cn = row[1].strip()
                    
                    # 从整行文本中用正则表达式安全地提取所有音频文件
                    full_row_text = "\t".join(row)
                    audio_files = re.findall(r'\[sound:(.*?)\]', full_row_text)
                    
                    audio_path_uk = ""
                    audio_path_us = ""
                    for audio_file in audio_files:
                        if "cambridgeee" in audio_file: # 根据您的文件名规律判断
                            audio_path_us = audio_file
                        else:
                            audio_path_uk = audio_file
                    
                    ipa_us = row[8].strip() if len(row) > 8 else ""
                    
                    # 解析包含剑桥词典释义的HTML列
                    cambridge_html = row[7].strip() if len(row) > 7 else ""
                    definition_en, example_en = clean_html(cambridge_html)

                    # 处理list_id，格式为"L26"这样的形式，位于每行的最后
                    list_id_str = ""
                    # 检查最后一列是否包含list_id
                    if len(row) > 0:
                        # 获取最后一列的值
                        last_col = row[-1].strip()
                        # 检查是否符合"L数字"的格式
                        if last_col.startswith("L") and last_col[1:].isdigit():
                            list_id_str = last_col[1:]
                    
                    # 如果没有找到合适的list_id，则使用默认值1
                    list_id = int(list_id_str) if list_id_str.isdigit() else 1

                    processed_rows.append([
                        list_id,
                        spelling,
                        ipa_us,
                        pos_and_meaning_cn,
                        definition_en,
                        example_en,
                        audio_path_uk,
                        audio_path_us
                    ])

                except Exception as e:
                    print(f"警告：处理第 {i+1} 行时发生错误，已跳过。错误: {e}, 内容: {row[:2]}...")
                    continue
        
        print(f"数据提取完成，共处理 {len(processed_rows)} 个单词。")

        # 将处理好的数据写入新的CSV文件
        with open(OUTPUT_CSV_FILE, mode='w', newline='', encoding='utf-8-sig') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(CSV_HEADER) # 写入表头
            writer.writerows(processed_rows) # 写入所有数据
        
        print(f"成功！已生成标准CSV文件: {OUTPUT_CSV_FILE}")

    except Exception as e:
        print(f"处理文件时发生严重错误: {e}")

# --- 运行主函数 ---
if __name__ == '__main__':
    parse_anki_txt_to_standard_csv()