import re
import csv
import os

# --- 配置区 ---
# 输入文件：纯文本词典书文件
INPUT_TXT_FILE = r"D:\Projects\VocabularyTrainer\wordlists\senior_high\Gao Zhong Ying Yu Ci Hui Ci Gen - Yu Min Hong.txt"
# CSV文件：需要填充的CSV文件
CSV_FILE = r'D:\Projects\VocabularyTrainer\wordlists\senior_high\senior_high_complete.csv'
# 输出文件：填充后的CSV文件
OUTPUT_CSV_FILE = r'D:\Projects\VocabularyTrainer\wordlists\senior_high\senior_high_complete_filled_cognitive.csv'
# 认知词部分的行范围
COGNITIVE_WORDS_START_LINE = 24433
COGNITIVE_WORDS_END_LINE = 32004
# ----------------

def extract_cognitive_word_info(txt_content):
    """
    从认知词部分提取单词信息
    """
    # 使用正则表达式匹配认知词格式
    # 格式：单词 + 音标 + 词性和释义 + 可能的记忆方法 + 可能的例句
    pattern = re.compile(r'\n+([a-zA-Z\-]+)\n+(/[^/]+/)\n+([^\n]+)(?:\n+记　([^\n]+))?(?:\n+例　([^\n]+))?', re.DOTALL)
    matches = pattern.finditer(txt_content)
    
    # 存储所有认知词信息的字典
    cognitive_words_info = {}
    
    for match in matches:
        word = match.group(1).strip().lower()
        ipa = match.group(2).strip()
        meaning = match.group(3).strip()
        mnemonic = match.group(4).strip() if match.group(4) else ''
        example = match.group(5).strip() if match.group(5) else ''
        
        cognitive_words_info[word] = {
            'ipa': ipa,
            'meaning': meaning,
            'mnemonic': mnemonic,
            'example': example
        }
        
        # 输出提取到的单词信息，用于调试
        print(f"提取到认知词: {word}, IPA: {ipa}, 词义: {meaning[:20]}..., 记忆方法: {mnemonic[:20]}..., 例句: {example[:20]}...")
    
    print(f"从认知词部分提取了 {len(cognitive_words_info)} 个单词的信息")
    return cognitive_words_info

def get_basic_word_info():
    """
    为一些基础词汇提供基本信息
    """
    basic_words = {
        'about': {
            'ipa': '/əˈbaʊt/',
            'meaning': 'prep. 关于；在...周围 adv. 大约；到处',
            'mnemonic': '联想记忆：a+bout(拳击比赛)→围绕着拳击比赛→关于；在...周围',
            'example': 'What are you talking about? 你在说什么？'
        },
        'above': {
            'ipa': '/əˈbʌv/',
            'meaning': 'prep. 在...上面；高于 adv. 在上面',
            'mnemonic': '联想记忆：a+bove(看作move移动)→向上移动→在...上面',
            'example': 'The temperature is above zero. 温度在零度以上。'
        },
        'abroad': {
            'ipa': '/əˈbrɔːd/',
            'meaning': 'adv. 到国外；在国外',
            'mnemonic': '联想记忆：a+broad(宽广的)→去到宽广的地方→到国外',
            'example': 'He has gone abroad for further study. 他出国深造去了。'
        },
        'and': {
            'ipa': '/ænd/',
            'meaning': 'conj. 和，与，而且',
            'mnemonic': '基础连词，表示连接和并列关系',
            'example': 'I like apples and oranges. 我喜欢苹果和橙子。'
        },
        'but': {
            'ipa': '/bʌt/',
            'meaning': 'conj. 但是，可是 prep. 除了',
            'mnemonic': '基础连词，表示转折关系',
            'example': 'I like him, but he doesn\'t like me. 我喜欢他，但他不喜欢我。'
        },
        'or': {
            'ipa': '/ɔː/',
            'meaning': 'conj. 或者，否则',
            'mnemonic': '基础连词，表示选择关系',
            'example': 'Do you want tea or coffee? 你要茶还是咖啡？'
        },
        'if': {
            'ipa': '/ɪf/',
            'meaning': 'conj. 如果，假如',
            'mnemonic': '基础连词，表示条件关系',
            'example': 'If it rains, I will stay at home. 如果下雨，我就待在家里。'
        },
        'because': {
            'ipa': '/bɪˈkɒz/',
            'meaning': 'conj. 因为',
            'mnemonic': '基础连词，表示原因关系',
            'example': 'I stayed at home because it was raining. 我待在家里因为下雨了。'
        },
        'so': {
            'ipa': '/səʊ/',
            'meaning': 'adv. 如此，这么 conj. 所以，因此',
            'mnemonic': '基础连词，表示结果关系',
            'example': 'It was raining, so I stayed at home. 下雨了，所以我待在家里。'
        },
        'when': {
            'ipa': '/wen/',
            'meaning': 'conj. 当...的时候 adv. 什么时候',
            'mnemonic': '基础连词，表示时间关系',
            'example': 'When will you come? 你什么时候来？'
        },
        'where': {
            'ipa': '/weə/',
            'meaning': 'adv. 在哪里 conj. 在...的地方',
            'mnemonic': '基础疑问词，表示地点',
            'example': 'Where do you live? 你住在哪里？'
        },
        'what': {
            'ipa': '/wɒt/',
            'meaning': 'pron. 什么 adj. 什么样的',
            'mnemonic': '基础疑问词，表示事物',
            'example': 'What is your name? 你叫什么名字？'
        },
        'who': {
            'ipa': '/huː/',
            'meaning': 'pron. 谁',
            'mnemonic': '基础疑问词，表示人',
            'example': 'Who is that man? 那个人是谁？'
        },
        'how': {
            'ipa': '/haʊ/',
            'meaning': 'adv. 怎样，如何',
            'mnemonic': '基础疑问词，表示方式',
            'example': 'How do you do this? 你怎么做这个？'
        },
        'why': {
            'ipa': '/waɪ/',
            'meaning': 'adv. 为什么',
            'mnemonic': '基础疑问词，表示原因',
            'example': 'Why are you late? 你为什么迟到？'
        },
        'yet': {
            'ipa': '/jet/',
            'meaning': 'adv. 到目前为止；还；仍然',
            'mnemonic': '基础副词，常用于否定句和疑问句',
            'example': 'Have you finished your homework yet? 你完成作业了吗？'
        }
    }
    return basic_words

def fill_csv_with_cognitive_word_info(cognitive_words_info):
    """
    使用认知词信息填充CSV文件
    """
    # cognitive_words_info是从main函数传入的认知词信息字典
    
    # 获取基础词汇信息
    basic_words_info = get_basic_word_info()
    
    # 读取CSV文件
    csv_data = []
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    
    # 获取表头
    header = csv_data[0]
    
    # 查找需要填充的列索引
    ipa_index = -1
    meaning_index = -1
    example_index = -1
    mnemonic_index = -1
    
    # 尝试不同的可能列名
    for i, col_name in enumerate(header):
        if col_name == 'IPA':
            ipa_index = i
        elif col_name == 'Meaning (CN)':
            meaning_index = i
        elif col_name == 'Example':
            example_index = i
        elif col_name == 'Mnemonic':
            mnemonic_index = i
    
    # 输出找到的列索引
    print(f"IPA列索引: {ipa_index}")
    print(f"Meaning列索引: {meaning_index}")
    print(f"Example列索引: {example_index}")
    print(f"Mnemonic列索引: {mnemonic_index}")
    
    # 如果找不到列，输出警告
    if ipa_index == -1:
        print("警告：找不到IPA列")
    if meaning_index == -1:
        print("警告：找不到Meaning列")
    if example_index == -1:
        print("警告：找不到Example列")
    if mnemonic_index == -1:
        print("警告：找不到Mnemonic列")
    
    # 统计信息
    total_words = 0
    filled_words = 0
    filled_basic_words = 0
    filled_cognitive_words = 0
    
    # 遍历CSV数据，填充单词信息
    for i in range(1, len(csv_data)):
        row = csv_data[i]
        
        # 跳过词缀
        if len(row) < 2 or not row[1] or row[1].endswith('-') or row[1].startswith('-'):
            continue
        
        word = row[1].strip().lower()
        total_words += 1
        
        # 检查是否需要填充
        needs_filling = False
        if ipa_index >= 0 and (len(row) <= ipa_index or not row[ipa_index]):
            needs_filling = True
        elif meaning_index >= 0 and (len(row) <= meaning_index or not row[meaning_index]):
            needs_filling = True
        elif example_index >= 0 and (len(row) <= example_index or not row[example_index]):
            needs_filling = True
        elif mnemonic_index >= 0 and (len(row) <= mnemonic_index or not row[mnemonic_index]):
            needs_filling = True
        
        if not needs_filling:
            continue
        
        # 优先使用基础词汇信息
        if word in basic_words_info:
            word_info = basic_words_info[word]
            
            # 填充IPA
            if ipa_index >= 0 and (len(row) <= ipa_index or not row[ipa_index]) and word_info['ipa']:
                while len(row) <= ipa_index:
                    row.append('')
                row[ipa_index] = word_info['ipa']
            
            # 填充词义
            if meaning_index >= 0 and (len(row) <= meaning_index or not row[meaning_index]) and word_info['meaning']:
                while len(row) <= meaning_index:
                    row.append('')
                row[meaning_index] = word_info['meaning']
            
            # 填充例句
            if example_index >= 0 and (len(row) <= example_index or not row[example_index]) and word_info['example']:
                while len(row) <= example_index:
                    row.append('')
                row[example_index] = word_info['example']
            
            # 填充记忆方法
            if mnemonic_index >= 0 and (len(row) <= mnemonic_index or not row[mnemonic_index]) and word_info['mnemonic']:
                while len(row) <= mnemonic_index:
                    row.append('')
                row[mnemonic_index] = word_info['mnemonic']
            
            filled_words += 1
            filled_basic_words += 1
            print(f"已填充基础单词 '{word}' 的信息")
        
        # 然后使用认知词信息
        elif word in cognitive_words_info:
            word_info = cognitive_words_info[word]
            
            # 填充IPA
            if ipa_index >= 0 and (len(row) <= ipa_index or not row[ipa_index]) and word_info['ipa']:
                while len(row) <= ipa_index:
                    row.append('')
                row[ipa_index] = word_info['ipa']
            
            # 填充词义
            if meaning_index >= 0 and (len(row) <= meaning_index or not row[meaning_index]) and word_info['meaning']:
                while len(row) <= meaning_index:
                    row.append('')
                row[meaning_index] = word_info['meaning']
            
            # 填充例句
            if example_index >= 0 and (len(row) <= example_index or not row[example_index]) and word_info['example']:
                while len(row) <= example_index:
                    row.append('')
                row[example_index] = word_info['example']
            
            # 填充记忆方法
            if mnemonic_index >= 0 and (len(row) <= mnemonic_index or not row[mnemonic_index]) and word_info['mnemonic']:
                while len(row) <= mnemonic_index:
                    row.append('')
                row[mnemonic_index] = word_info['mnemonic']
            
            filled_words += 1
            filled_cognitive_words += 1
            print(f"已填充认知词 '{word}' 的信息")
    
    # 写入输出文件
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    print(f"成功！已将填充后的数据写入CSV文件: {OUTPUT_CSV_FILE}")
    print(f"总共处理了 {total_words} 个单词，成功填充了 {filled_words} 个单词的信息")
    print(f"其中，填充了 {filled_basic_words} 个基础单词的信息，{filled_cognitive_words} 个认知词的信息")
    print(f"填充率: {filled_words/total_words*100:.2f}%" if total_words > 0 else "没有需要填充的单词")

# 添加认知词到CSV文件
def add_cognitive_words_to_csv():
    """
    将认知词添加到CSV文件中
    """
    # 读取认知词部分的内容
    with open(INPUT_TXT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        cognitive_words_content = ''.join(lines[COGNITIVE_WORDS_START_LINE-1:COGNITIVE_WORDS_END_LINE])
    
    # 提取认知词信息
    cognitive_words_info = extract_cognitive_word_info(cognitive_words_content)
    
    # 读取CSV文件
    csv_data = []
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    
    # 获取表头
    header = csv_data[0]
    
    # 查找需要填充的列索引
    ipa_index = -1
    meaning_index = -1
    example_index = -1
    mnemonic_index = -1
    
    # 尝试不同的可能列名
    for i, col_name in enumerate(header):
        if col_name == 'IPA':
            ipa_index = i
        elif col_name == 'Meaning (CN)':
            meaning_index = i
        elif col_name == 'Example':
            example_index = i
        elif col_name == 'Mnemonic':
            mnemonic_index = i
    
    # 输出找到的列索引
    print(f"添加认知词 - IPA列索引: {ipa_index}")
    print(f"添加认知词 - Meaning列索引: {meaning_index}")
    print(f"添加认知词 - Example列索引: {example_index}")
    print(f"添加认知词 - Mnemonic列索引: {mnemonic_index}")
    
    # 获取CSV文件中已有的单词
    existing_words = set()
    for row in csv_data[1:]:
        if len(row) > 1:
            existing_words.add(row[1].strip().lower())
    
    # 添加认知词到CSV文件
    new_words_count = 0
    for word, info in cognitive_words_info.items():
        if word not in existing_words:
            # 创建一个与表头长度相同的空行
            new_row = [''] * len(header)
            # 设置Word List列
            new_row[0] = '认知词'
            # 设置Word列
            new_row[1] = word
            # 设置IPA列
            if ipa_index >= 0:
                new_row[ipa_index] = info['ipa']
            # 设置Meaning列
            if meaning_index >= 0:
                new_row[meaning_index] = info['meaning']
            # 设置Example列
            if example_index >= 0:
                new_row[example_index] = info['example']
            # 设置Mnemonic列
            if mnemonic_index >= 0:
                new_row[mnemonic_index] = info['mnemonic']
            csv_data.append(new_row)
            new_words_count += 1
            print(f"已添加认知词 '{word}' 到CSV文件")
    
    # 写入输出文件
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    print(f"成功！已将 {new_words_count} 个新认知词添加到CSV文件: {OUTPUT_CSV_FILE}")

def main():
    # 读取认知词部分的内容
    with open(INPUT_TXT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        cognitive_words_content = ''.join(lines[COGNITIVE_WORDS_START_LINE-1:COGNITIVE_WORDS_END_LINE])
    
    # 提取认知词信息
    cognitive_words_info = extract_cognitive_word_info(cognitive_words_content)
    
    # 填充CSV文件
    fill_csv_with_cognitive_word_info(cognitive_words_info)
    
    # 添加认知词到CSV文件
    add_cognitive_words_to_csv()

if __name__ == '__main__':
    main()