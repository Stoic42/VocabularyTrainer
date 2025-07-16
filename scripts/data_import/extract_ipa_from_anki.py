#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Anki文件中提取IPA信息并更新数据库
"""

from utils import get_database_connection, get_database_path
import sqlite3
import re
import os

# 配置
DATABASE_FILE = get_database_path()
SENIOR_HIGH_ANKI_FILE = 'wordlists/senior_high/高中 乱序 绿宝书.txt'
JUNIOR_HIGH_ANKI_FILE = 'wordlists/junior_high/初中 乱序 绿宝书.txt'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def extract_ipa_from_anki_file(anki_file_path):
    """从Anki文件中提取IPA信息"""
    print(f"正在从 '{anki_file_path}' 提取IPA信息...")
    ipa_map = {}
    
    try:
        with open(anki_file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                # 分割行，Anki文件使用制表符分隔
                parts = line.split('\t')
                if len(parts) < 3:
                    continue
                
                # 提取单词和IPA
                # 格式通常是: [ID] [Word] [IPA] [其他字段...]
                if len(parts) >= 3:
                    word = parts[1].strip().lower()
                    ipa_field = parts[2].strip()
                    
                    # 提取IPA，格式可能是 [ɪnˈvɛnt] 或 /ɪnˈvɛnt/ 或 ɪnˈvɛnt
                    ipa = ""
                    if ipa_field:
                        # 移除方括号和斜杠
                        ipa = ipa_field.strip('[]/')
                        # 如果包含HTML实体，解码
                        ipa = ipa.replace('&#x27;', "'")
                        ipa = ipa.replace('&#x2C;', ',')
                        
                        if ipa and ipa != word:  # 确保IPA不是单词本身
                            ipa_map[word] = ipa
                
                if line_num % 1000 == 0:
                    print(f"已处理 {line_num} 行...")
    
    except FileNotFoundError:
        print(f"错误: 找不到Anki文件 '{anki_file_path}'")
        return None
    except Exception as e:
        print(f"处理Anki文件时出错: {e}")
        return None
    
    print(f"IPA提取完成！共找到 {len(ipa_map)} 个单词的IPA信息。")
    return ipa_map

def update_database_with_ipa(conn, ipa_map):
    """更新数据库中的IPA信息"""
    print("正在更新数据库中的IPA信息...")
    cursor = conn.cursor()
    updated_count = 0
    
    try:
        for word, ipa in ipa_map.items():
            # 更新所有匹配的单词记录
            cursor.execute(
                "UPDATE Words SET ipa = ? WHERE LOWER(spelling) = ?",
                (ipa, word)
            )
            if cursor.rowcount > 0:
                updated_count += cursor.rowcount
        
        conn.commit()
        print(f"IPA更新完成！共更新了 {updated_count} 个单词记录。")
        
    except Exception as e:
        print(f"更新数据库时出错: {e}")
        conn.rollback()

def main():
    """主执行函数"""
    # 检查数据库是否存在
    if not os.path.exists(DATABASE_FILE):
        print(f"错误: 找不到数据库文件 '{DATABASE_FILE}'")
        return
    
    # 连接数据库
    conn = get_db_connection()
    
    # 处理高中单词书
    if os.path.exists(SENIOR_HIGH_ANKI_FILE):
        print("\n=== 处理高中单词书 ===")
        senior_ipa_map = extract_ipa_from_anki_file(SENIOR_HIGH_ANKI_FILE)
        if senior_ipa_map:
            update_database_with_ipa(conn, senior_ipa_map)
    else:
        print(f"警告: 找不到高中Anki文件 '{SENIOR_HIGH_ANKI_FILE}'")
    
    # 处理初中单词书
    if os.path.exists(JUNIOR_HIGH_ANKI_FILE):
        print("\n=== 处理初中单词书 ===")
        junior_ipa_map = extract_ipa_from_anki_file(JUNIOR_HIGH_ANKI_FILE)
        if junior_ipa_map:
            update_database_with_ipa(conn, junior_ipa_map)
    else:
        print(f"警告: 找不到初中Anki文件 '{JUNIOR_HIGH_ANKI_FILE}'")
    
    conn.close()
    print("\nIPA提取和更新操作已完成。")

if __name__ == '__main__':
    main() 