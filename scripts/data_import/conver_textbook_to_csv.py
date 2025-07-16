import re
import csv
import os

# --- 配置区 ---
# 输入文件：您的纯文本词典书文件
INPUT_TXT_FILE = r"D:\Projects\VocabularyTrainer\wordlists\senior_high\Gao Zhong Ying Yu Ci Hui Ci Gen - Yu Min Hong.txt"
# 输出文件：我们最终生成的、干净的标准CSV文件
OUTPUT_CSV_FILE = r'D:\Projects\VocabularyTrainer\wordlists\senior_high\highschool_standard_from_txt.csv'

# 定义我们标准CSV的表头
CSV_HEADER = [
    'spelling', 'ipa', 'pos_and_meaning', 'etymology', 'mnemonic', 'example', 'notes', 'word_list'
]
# ----------------

def create_empty_word_data():
    return {
        'spelling': '',
        'ipa': '',
        'pos_and_meaning': '',
        'etymology': '',
        'mnemonic': '',
        'example': '',
        'notes': '',
        'word_list': ''
    }

def parse_textbook_file():
    """
    读取并解析书籍格式的TXT文件，提取单词及其所有属性。
    """
    if not os.path.exists(INPUT_TXT_FILE):
        print(f"错误: 输入文件 '{INPUT_TXT_FILE}' 不存在。")
        return

    print(f"开始解析文件: {INPUT_TXT_FILE}")
    
    all_words_data = []
    current_word_data = {}
    current_word_list = ""  # 用于跟踪当前的词表编号

    # 正则表达式来识别不同类型的信息
    # 匹配一个单词，通常是纯英文字母，可能带*号
    word_pattern = re.compile(r'^[a-z]+[\*]*$')
    # 匹配音标，通常在方括号[]或斜杠//里
    ipa_pattern = re.compile(r'^\[.*\]$|^/.*/$')
    # 匹配词性+词义，通常以 n./v./adj. 等开头
    meaning_pattern = re.compile(r'^(n|v|adj|adv|prep|conj|art|pron|vt|vi)\\..*')
    # 匹配例句，通常以"例"或"例　"开头
    example_pattern = re.compile(r'^例[\s　]*(.*)')
    # 匹配考点，通常以"考"或"考　"开头
    note_pattern = re.compile(r'^考[\s　]*(.*)')
    # 匹配参考，通常以"参"或"参　"开头
    ref_pattern = re.compile(r'^参[\s　]*(.*)')
    # 匹配【记】、【根】、【例】等标签
    tag_pattern = re.compile(r'^【(记|根|派|辨|同|反|例)】(.*)')
    # 匹配词表编号，例如 "Word List 1"
    word_list_pattern = re.compile(r'^Word List (\d+)$')
    # 匹配词缀，例如 "前缀\na-"
    prefix_pattern = re.compile(r'^前缀$')
    # 匹配词根，例如 "词根\n-able"
    root_pattern = re.compile(r'^词根$')
    # 匹配词根项，例如 "acu："
    root_item_pattern = re.compile(r'^([a-z]+[，,]?[a-z]*[（(]?[a-z]?[）)]?[，,]?[a-z]*[，,]?[a-z]*[（(]?[a-z]?[）)]?[，,]?[a-z]*：)$')
    # 匹配词根解释
    root_explanation_pattern = re.compile(r'^([^a-zA-Z].+：.+)$')
    # 匹配核心单词
    core_word_pattern = re.compile(r'^核心单词$')

    with open(INPUT_TXT_FILE, 'r', encoding='utf-8') as f:
        # 用于跟踪当前的类型（普通词表、词缀、词根、核心单词）
        current_type = "normal"
        
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 检查是否是词表编号
            word_list_match = word_list_pattern.match(line)
            if word_list_match:
                current_word_list = word_list_match.group(1)
                current_type = "normal"
                print(f"找到词表编号: Word List {current_word_list}")
                continue
                
            # 检查是否是词缀部分
            if prefix_pattern.match(line):
                current_type = "prefix"
                current_word_list = "词缀"
                print(f"找到词缀部分")
                continue
                
            # 检查是否是词根部分
            elif root_pattern.match(line):
                current_type = "root"
                current_word_list = "词根"
                print(f"找到词根部分")
                continue
            
            # 检查是否是词根项
            elif current_type == "root" and root_item_pattern.match(line):
                # 如果当前有单词在处理，先保存
                if current_word_data and current_word_data['spelling']:
                    all_words_data.append(current_word_data)
                    current_word_data = create_empty_word_data()
                
                # 提取词根名称
                current_word_data['spelling'] = line.strip()
                current_word_data['word_list'] = current_word_list
                is_new_word = True
                continue
                
            # 检查是否是核心单词部分
            if core_word_pattern.match(line):
                current_type = "core"
                current_word_list = "核心单词"
                print(f"找到核心单词部分")
                continue

            # 检查是否是一个新单词的开始
            is_new_word = False
            
            # 根据当前类型使用不同的匹配规则
            if current_type == "normal" or current_type == "core":
                # 普通单词和核心单词使用相同的匹配规则
                if word_pattern.match(line) and len(line) < 30: # 增加长度限制以避免误判长句子
                    is_new_word = True
                    word_spelling = line.replace('*','').strip()
            elif current_type == "prefix" or current_type == "root":
                # 词缀和词根可能是以-开头或结尾的形式，如a-、-able
                if re.match(r'^[a-z]+\-$|^\-[a-z]+$|^[a-z]+$', line) and len(line) < 30:
                    is_new_word = True
                    word_spelling = line.strip()
            
            if is_new_word:
                # 如果是新单词，说明上一个单词的信息已经收集完毕
                # 将上一个单词的数据存起来
                if current_word_data:
                    all_words_data.append(current_word_data)
                
                # 开始为一个新单词收集数据
                current_word_data = {key: '' for key in CSV_HEADER}
                # 确保notes字段被初始化为空字符串
                current_word_data['notes'] = ''
                current_word_data['spelling'] = word_spelling
                # 添加当前词表编号
                current_word_data['word_list'] = current_word_list
                continue

            # 如果当前没有正在处理的单词，就跳过所有其他行
            if not current_word_data:
                continue

            # 匹配其他属性
            tagged_match = tag_pattern.match(line)
            example_match = example_pattern.match(line)
            note_match = note_pattern.match(line)
            ref_match = ref_pattern.match(line)
            
            if ipa_pattern.match(line) and not current_word_data.get('ipa'):
                current_word_data['ipa'] = line
            elif meaning_pattern.match(line):
                # 允许多个词义，用换行符连接
                if current_word_data['pos_and_meaning']:
                    current_word_data['pos_and_meaning'] += '\n' + line
                else:
                    current_word_data['pos_and_meaning'] = line
            # 检查是否是词根解释
            elif current_type == "root" and root_explanation_pattern.match(line) and current_word_data and current_word_data['spelling']:
                # 词根解释直接作为词义处理
                if current_word_data['pos_and_meaning']:
                    current_word_data['pos_and_meaning'] += '\n' + line
                else:
                    current_word_data['pos_and_meaning'] = line
                is_new_word = False
                continue
            
            # 对于词缀和词根，如果不是新单词开始，且当前有单词在处理，则视为词义
            elif (current_type == "prefix" or current_type == "root") and current_word_data and not is_new_word:
                # 词缀和词根的解释通常没有词性标记，直接作为词义处理
                if current_word_data['pos_and_meaning']:
                    current_word_data['pos_and_meaning'] += '\n' + line
                else:
                    current_word_data['pos_and_meaning'] = line
            elif example_match:
                # 提取例句
                content = example_match.group(1).strip()
                if current_word_data['example']:
                    current_word_data['example'] += '\n' + content
                else:
                    current_word_data['example'] = content
            elif note_match:
                # 提取考点信息
                content = note_match.group(1).strip()
                if current_word_data['notes']:
                    current_word_data['notes'] += '考点: ' + content + '\n'
                else:
                    current_word_data['notes'] = '考点: ' + content + '\n'
            elif ref_match:
                # 提取参考信息
                content = ref_match.group(1).strip()
                if current_word_data['notes']:
                    current_word_data['notes'] += '参考: ' + content + '\n'
                else:
                    current_word_data['notes'] = '参考: ' + content + '\n'
            elif tagged_match:
                tag = tagged_match.group(1)
                content = tagged_match.group(2).strip()
                if tag == '根':
                    current_word_data['etymology'] = content
                elif tag == '记':
                    current_word_data['mnemonic'] = content
                elif tag == '例':
                    if current_word_data['example']:
                        current_word_data['example'] += '\n' + content
                    else:
                        current_word_data['example'] = content
                else: # 其他标签如派、辨、同、反等，都放入notes
                    if current_word_data['notes']:
                        current_word_data['notes'] += f"【{tag}】{content}\n"
                    else:
                        current_word_data['notes'] = f"【{tag}】{content}\n"
            # 默认情况下，任何不匹配的行都可能是一个多行的例句或笔记，可以根据需要添加逻辑
            # 这里为简单起见，我们只捕获带【例】标签的例句

    # 不要忘记添加最后一个单词的数据
    if current_word_data:
        all_words_data.append(current_word_data)

    print(f"解析完成，共找到 {len(all_words_data)} 个单词的数据。")
    
    # 写入CSV文件
    try:
        with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=CSV_HEADER)
            writer.writeheader()
            writer.writerows(all_words_data)
        print(f"成功！已将所有数据写入标准CSV文件: {OUTPUT_CSV_FILE}")
    except Exception as e:
        print(f"写入CSV文件时出错: {e}")

if __name__ == '__main__':
    parse_textbook_file()