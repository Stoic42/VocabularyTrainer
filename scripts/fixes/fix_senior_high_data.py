#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正高中词书数据库中的单词数据
正确分离词性、释义、例句、词根记忆等信息
保持word_id不变，避免影响用户错误记录
"""

import sqlite3
import re
import os
from typing import Dict, List, Tuple, Optional

def connect_db():
    """连接数据库"""
    return sqlite3.connect('vocabulary.db')

def extract_pos_and_meaning(text: str) -> Tuple[str, str]:
    """
    从混合文本中提取词性和释义
    例如: "（美elevator）n. 电梯　vt. 举起，抬起　vi. 升起，（云、烟等）消散"
    返回: ("n. 电梯　vt. 举起，抬起　vi. 升起，（云、烟等）消散", "（美elevator）")
    """
    if not text:
        return "", ""
    
    # 移除括号中的美式英语变体
    pattern = r'（美[^）]+）'
    match = re.search(pattern, text)
    variant = match.group(0) if match else ""
    
    # 移除变体信息，保留词性和释义
    cleaned_text = re.sub(pattern, '', text).strip()
    
    return cleaned_text, variant

def extract_examples(text: str) -> Tuple[str, str]:
    """
    从文本中提取例句
    例如: "例　wait for the lift等电梯//Please lift the box and put it on the table. 请把盒子抬起来放到桌子上。"
    返回: ("wait for the lift等电梯", "Please lift the box and put it on the table. 请把盒子抬起来放到桌子上。")
    """
    if not text:
        return "", ""
    
    # 查找"例"开头的例句
    pattern = r'例　(.*?)(?=\n|$)'
    match = re.search(pattern, text)
    if match:
        examples = match.group(1)
        # 分离中英文例句
        parts = examples.split('//')
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()
        else:
            return examples.strip(), ""
    
    return "", ""

def extract_mnemonic(text: str) -> str:
    """
    从文本中提取记忆方法
    例如: "记　联想记忆：s＋wall（墙）＋（l）ow→燕子在墙角垒窝"
    """
    if not text:
        return ""
    
    # 查找"记"开头的记忆方法
    pattern = r'记　(.*?)(?=\n|$)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    return ""

def extract_collocation(text: str) -> str:
    """
    从文本中提取搭配用法
    例如: "考　1．as/so far as I know就我所知2．as/so far as I am concerned就我而言，我认为..."
    """
    if not text:
        return ""
    
    # 查找"考"开头的搭配用法
    pattern = r'考　(.*?)(?=\n|$)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    return ""

def extract_usage(text: str) -> str:
    """
    从文本中提取用法说明
    例如: "用　1．（be）dressed in...穿着…：Dressed in a white uniform, he looks more like a cook than a doctor."
    """
    if not text:
        return ""
    
    # 查找"用"开头的用法说明
    pattern = r'用　(.*?)(?=\n|$)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    return ""

def extract_comparison(text: str) -> str:
    """
    从文本中提取词义辨析
    例如: "辨　cure，heal，treat"
    """
    if not text:
        return ""
    
    # 查找"辨"开头的词义辨析
    pattern = r'辨　(.*?)(?=\n|$)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    return ""

def extract_derivatives(text: str) -> str:
    """
    从文本中提取派生词
    例如: "参　picker（n. 采集者）"
    """
    if not text:
        return ""
    
    # 查找"参"开头的派生词
    pattern = r'参　(.*?)(?=\n|$)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    return ""

def clean_meaning_cn(meaning_cn: str) -> Dict[str, str]:
    """
    清理meaning_cn字段，分离出各个组成部分
    """
    if not meaning_cn:
        return {
            'pos': '',
            'meaning_cn': '',
            'example_cn': '',
            'example_en': '',
            'mnemonic': '',
            'collocation': '',
            'usage': '',
            'comparison': '',
            'derivatives': '',
            'variant': ''
        }
    
    # 提取词性和释义
    pos_and_meaning, variant = extract_pos_and_meaning(meaning_cn)
    
    # 提取例句
    example_cn, example_en = extract_examples(meaning_cn)
    
    # 提取记忆方法
    mnemonic = extract_mnemonic(meaning_cn)
    
    # 提取搭配用法
    collocation = extract_collocation(meaning_cn)
    
    # 提取用法说明
    usage = extract_usage(meaning_cn)
    
    # 提取词义辨析
    comparison = extract_comparison(meaning_cn)
    
    # 提取派生词
    derivatives = extract_derivatives(meaning_cn)
    
    return {
        'pos': pos_and_meaning,
        'meaning_cn': pos_and_meaning,  # 保持原字段不变，但内容已清理
        'example_cn': example_cn,
        'example_en': example_en,
        'mnemonic': mnemonic,
        'collocation': collocation,
        'usage': usage,
        'comparison': comparison,
        'derivatives': derivatives,
        'variant': variant
    }

def update_word_data(cursor, word_id: int, cleaned_data: Dict[str, str]):
    """
    更新单词数据
    """
    try:
        cursor.execute("""
            UPDATE Words SET 
                pos = ?,
                meaning_cn = ?,
                mnemonic = ?,
                collocation = ?,
                tips = ?,
                comparison = ?,
                derivatives = ?,
                exam_sentence = ?
            WHERE word_id = ?
        """, (
            cleaned_data['pos'],
            cleaned_data['meaning_cn'],
            cleaned_data['mnemonic'],
            cleaned_data['collocation'],
            cleaned_data['usage'],  # 用法说明放在tips字段
            cleaned_data['comparison'],
            cleaned_data['derivatives'],
            cleaned_data['example_en'],  # 例句放在exam_sentence字段
            word_id
        ))
        return True
    except Exception as e:
        print(f"更新单词 {word_id} 时出错: {e}")
        return False

def get_senior_high_words(cursor) -> List[Tuple]:
    """
    获取高中词书的所有单词
    """
    cursor.execute("""
        SELECT w.word_id, w.spelling, w.pos, w.meaning_cn, w.mnemonic, w.collocation, 
               w.tips, w.comparison, w.derivatives, w.exam_sentence
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE b.book_name LIKE '%高中%' OR b.book_name LIKE '%senior%'
        ORDER BY w.word_id
    """)
    return cursor.fetchall()

def main():
    """主函数"""
    print("开始修正高中词书数据...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # 获取所有高中词书的单词
    words = get_senior_high_words(cursor)
    print(f"找到 {len(words)} 个高中词书单词")
    
    updated_count = 0
    error_count = 0
    
    for word_data in words:
        word_id, spelling, pos, meaning_cn, mnemonic, collocation, tips, comparison, derivatives, exam_sentence = word_data
        
        print(f"处理单词: {spelling} (ID: {word_id})")
        
        # 清理meaning_cn字段
        cleaned_data = clean_meaning_cn(meaning_cn)
        
        # 如果清理后的数据与原始数据不同，则更新
        if (cleaned_data['meaning_cn'] != meaning_cn or 
            cleaned_data['example_en'] != exam_sentence or
            cleaned_data['mnemonic'] != mnemonic or
            cleaned_data['collocation'] != collocation or
            cleaned_data['usage'] != tips or
            cleaned_data['comparison'] != comparison or
            cleaned_data['derivatives'] != derivatives):
            
            print(f"  需要更新: {spelling}")
            print(f"    原meaning_cn: {meaning_cn[:100]}...")
            print(f"    新meaning_cn: {cleaned_data['meaning_cn'][:100]}...")
            print(f"    例句: {cleaned_data['example_en']}")
            print(f"    记忆: {cleaned_data['mnemonic']}")
            print(f"    搭配: {cleaned_data['collocation'][:50]}...")
            
            if update_word_data(cursor, word_id, cleaned_data):
                updated_count += 1
                print(f"  ✓ 更新成功")
            else:
                error_count += 1
                print(f"  ✗ 更新失败")
        else:
            print(f"  无需更新: {spelling}")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print(f"\n修正完成!")
    print(f"成功更新: {updated_count} 个单词")
    print(f"更新失败: {error_count} 个单词")
    print(f"总计处理: {len(words)} 个单词")

if __name__ == "__main__":
    main() 