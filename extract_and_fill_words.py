import re
import csv
import os

# --- 配置区 ---
# 输入文件：纯文本词典书文件
INPUT_TXT_FILE = r"D:\Projects\VocabularyTrainer\wordlists\senior_high\Gao Zhong Ying Yu Ci Hui Ci Gen - Yu Min Hong.txt"
# CSV文件：需要填充的CSV文件
CSV_FILE = r'D:\Projects\VocabularyTrainer\wordlists\senior_high\senior_high_complete.csv'
# 输出文件：填充后的CSV文件
OUTPUT_CSV_FILE = r'D:\Projects\VocabularyTrainer\wordlists\senior_high\senior_high_complete_filled.csv'
# ----------------

def extract_word_info(txt_content, word):
    """
    从文本内容中提取指定单词的信息
    """
    # 使用正则表达式匹配单词及其相关信息
    # 匹配模式：单词 + 音标 + 词性和释义 + 可能的记忆方法 + 可能的例句 + 可能的参考信息
    word_pattern = re.escape(word)  # 转义单词中的特殊字符
    
    # 完整模式：包含记忆方法和例句
    pattern = re.compile(r'\n\n' + word_pattern + r'\n\n(/[^/]+/)\n\n([\w\.\s,；:：；、]+)\n\n记　([^\n]+)\n\n例　([^\n]+)')
    match = pattern.search(txt_content)
    
    if match:
        ipa = match.group(1)
        meaning = match.group(2).strip()
        mnemonic = match.group(3).strip()
        example = match.group(4).strip()
        return {
            'ipa': ipa,
            'meaning': meaning,
            'mnemonic': mnemonic,
            'example': example
        }
    
    # 如果没有记忆方法，但有例句
    pattern = re.compile(r'\n\n' + word_pattern + r'\n\n(/[^/]+/)\n\n([\w\.\s,；:：；、]+)\n\n例　([^\n]+)')
    match = pattern.search(txt_content)
    
    if match:
        ipa = match.group(1)
        meaning = match.group(2).strip()
        example = match.group(3).strip()
        return {
            'ipa': ipa,
            'meaning': meaning,
            'mnemonic': '',
            'example': example
        }
    
    # 如果没有例句，但有记忆方法
    pattern = re.compile(r'\n\n' + word_pattern + r'\n\n(/[^/]+/)\n\n([\w\.\s,；:：；、]+)\n\n记　([^\n]+)')
    match = pattern.search(txt_content)
    
    if match:
        ipa = match.group(1)
        meaning = match.group(2).strip()
        mnemonic = match.group(3).strip()
        return {
            'ipa': ipa,
            'meaning': meaning,
            'mnemonic': mnemonic,
            'example': ''
        }
    
    # 如果既没有记忆方法也没有例句
    pattern = re.compile(r'\n\n' + word_pattern + r'\n\n(/[^/]+/)\n\n([\w\.\s,；:：；、]+)')
    match = pattern.search(txt_content)
    
    if match:
        ipa = match.group(1)
        meaning = match.group(2).strip()
        return {
            'ipa': ipa,
            'meaning': meaning,
            'mnemonic': '',
            'example': ''
        }
    
    # 如果上述模式都不匹配，尝试更宽松的匹配
    pattern = re.compile(r'\n\n' + word_pattern + r'\n\n(/[^/]+/)\n\n([^\n]+)')
    match = pattern.search(txt_content)
    
    if match:
        ipa = match.group(1)
        meaning = match.group(2).strip()
        return {
            'ipa': ipa,
            'meaning': meaning,
            'mnemonic': '',
            'example': ''
        }
    
    return None

def extract_all_words_from_txt():
    """
    从文本文件中提取所有单词及其信息
    """
    # 读取文本文件内容
    with open(INPUT_TXT_FILE, 'r', encoding='utf-8') as f:
        txt_content = f.read()
    
    # 使用正则表达式匹配所有单词及其信息
    # 匹配模式：单词 + 音标 + 词性和释义 + 可能的记忆方法 + 可能的例句 + 可能的参考信息
    pattern = re.compile(r'\n\n([a-zA-Z\-]+)\n\n(/[^/]+/)\n\n([^\n]+)')
    matches = pattern.finditer(txt_content)
    
    # 存储所有单词信息的字典
    all_words_info = {}
    
    for match in matches:
        word = match.group(1).strip()
        # 获取单词在文本中的位置，用于后续提取完整信息
        start_pos = match.start()
        
        # 提取单词的完整信息
        word_info = extract_word_info(txt_content[start_pos:start_pos+2000], word)
        if word_info:
            all_words_info[word.lower()] = word_info
    
    print(f"从文本文件中提取了 {len(all_words_info)} 个单词的信息")
    return all_words_info

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

def fill_csv_with_word_info():
    """
    从文本文件中提取单词信息，并填充到CSV文件中
    """
    # 提取所有单词信息
    all_words_info = extract_all_words_from_txt()
    
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
        if col_name == 'IPA' or col_name == 'ipa':
            ipa_index = i
        elif col_name == 'Meaning (CN)' or col_name == 'meaning' or col_name == 'Meaning':
            meaning_index = i
        elif col_name == 'Example' or col_name == 'example':
            example_index = i
        elif col_name == 'Mnemonic' or col_name == 'mnemonic':
            mnemonic_index = i
    
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
    basic_words_filled = 0
    
    # 遍历CSV数据，填充单词信息
    for i in range(1, len(csv_data)):
        row = csv_data[i]
        if len(row) > 1:  # 确保行有足够的列
            word = row[1].strip().lower() if len(row) > 1 else ""  # 假设单词在第二列
            
            # 跳过词缀和已完全填充的单词
            if not word or row[0].startswith('词缀'):
                continue
            
            # 确保行有足够的列
            while len(row) <= max(ipa_index, meaning_index, example_index, mnemonic_index):
                row.append("")
            
            # 检查是否需要填充
            needs_filling = False
            if ipa_index >= 0 and not row[ipa_index]:
                needs_filling = True
            if meaning_index >= 0 and not row[meaning_index]:
                needs_filling = True
            if example_index >= 0 and not row[example_index]:
                needs_filling = True
            if mnemonic_index >= 0 and not row[mnemonic_index]:
                needs_filling = True
            
            if not needs_filling:
                continue
            
            total_words += 1
            
            # 优先使用基础词汇信息
            word_info = None
            is_basic_word = word in basic_words_info
            
            if is_basic_word:
                word_info = basic_words_info[word]
            else:
                word_info = all_words_info.get(word)
            
            if word_info:
                # 填充IPA
                if ipa_index >= 0 and not row[ipa_index]:
                    row[ipa_index] = word_info['ipa']
                
                # 填充词义
                if meaning_index >= 0 and not row[meaning_index]:
                    row[meaning_index] = word_info['meaning']
                
                # 填充例句
                if example_index >= 0 and not row[example_index]:
                    row[example_index] = word_info['example']
                
                # 填充记忆方法
                if mnemonic_index >= 0 and not row[mnemonic_index]:
                    row[mnemonic_index] = word_info['mnemonic']
                
                filled_words += 1
                
                # 输出填充信息
                if is_basic_word:
                    basic_words_filled += 1
                    print(f"已填充基础单词 '{word}' 的信息")
                else:
                    print(f"已填充单词 '{word}' 的信息")
    
    # 写入输出文件
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    print(f"成功！已将填充后的数据写入CSV文件: {OUTPUT_CSV_FILE}")
    print(f"总共处理了 {total_words} 个单词，成功填充了 {filled_words} 个单词的信息")
    print(f"其中，填充了 {basic_words_filled} 个基础单词的信息")
    print(f"填充率: {filled_words/total_words*100:.2f}%" if total_words > 0 else "没有需要填充的单词")

if __name__ == '__main__':
    fill_csv_with_word_info()