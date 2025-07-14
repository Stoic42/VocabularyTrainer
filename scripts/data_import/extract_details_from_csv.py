#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从CSV文件中提取详细信息并填充到数据库
"""

import sqlite3
import csv
import os
import re

# 配置
DATABASE_FILE = 'vocabulary.db'
CSV_FILES = {
    'junior_high': 'wordlists/junior_high/junior_high_vocab_random.csv',
    'senior_high': 'wordlists/senior_high/senior_high_complete.csv'
}

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def extract_details_from_csv(csv_file_path):
    """从CSV文件中提取详细信息"""
    print(f"正在从 '{csv_file_path}' 提取详细信息...")
    details_map = {}
    
    if not os.path.exists(csv_file_path):
        print(f"警告: 找不到CSV文件 '{csv_file_path}'")
        return details_map
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                word = row.get('Word', '').strip().lower()
                if not word:
                    continue
                
                # 根据不同的CSV文件格式映射列名
                if 'junior_high' in csv_file_path:
                    # 初中词汇CSV文件的列名映射
                    details = {
                        'derivatives': row.get('Derivatives 派生词', '').strip(),
                        'root_etymology': '',  # 初中词汇没有词源字段
                        'mnemonic': row.get('Mnemonic', '').strip(),
                        'comparison': row.get('Comparison', '').strip(),
                        'collocation': row.get('Collocation', '').strip(),
                        'exam_sentence': row.get('Example', '').strip(),  # 使用Example作为例句
                        'exam_year_source': row.get('Exam Question Year', '').strip(),
                        'exam_options': row.get('Exam Question Options', '').strip(),
                        'exam_explanation': row.get('Exam Question Explanation', '').strip(),
                        'tips': row.get('Tips', '').strip()
                    }
                else:
                    # 高中词汇CSV文件的列名映射
                    details = {
                        'derivatives': row.get('Derivatives 派生词', '').strip(),
                        'root_etymology': row.get('root_etymology', '').strip(),
                        'mnemonic': row.get('Mnemonic', '').strip(),
                        'comparison': row.get('Comparison', '').strip(),
                        'collocation': row.get('Collocation', '').strip(),
                        'exam_sentence': row.get('exam_sentence', '').strip(),
                        'exam_year_source': row.get('exam_year_source', '').strip(),
                        'exam_options': row.get('exam_options', '').strip(),
                        'exam_explanation': row.get('exam_explanation', '').strip(),
                        'tips': row.get('Tips', '').strip()
                    }
                
                # 只保存有内容的详细信息
                has_content = any(details.values())
                if has_content:
                    details_map[word] = details
                
    except Exception as e:
        print(f"处理CSV文件时出错: {e}")
    
    print(f"从CSV文件中提取了 {len(details_map)} 个单词的详细信息。")
    return details_map

def update_database_with_details(conn, details_map):
    """更新数据库中的详细信息"""
    print("正在更新数据库中的详细信息...")
    cursor = conn.cursor()
    updated_count = 0
    
    try:
        for word, details in details_map.items():
            # 更新所有匹配的单词记录
            update_sql = """
                UPDATE Words SET 
                    derivatives = ?,
                    root_etymology = ?,
                    mnemonic = ?,
                    comparison = ?,
                    collocation = ?,
                    exam_sentence = ?,
                    exam_year_source = ?,
                    exam_options = ?,
                    exam_explanation = ?,
                    tips = ?
                WHERE LOWER(spelling) = ?
            """
            
            cursor.execute(update_sql, (
                details['derivatives'],
                details['root_etymology'],
                details['mnemonic'],
                details['comparison'],
                details['collocation'],
                details['exam_sentence'],
                details['exam_year_source'],
                details['exam_options'],
                details['exam_explanation'],
                details['tips'],
                word
            ))
            
            if cursor.rowcount > 0:
                updated_count += cursor.rowcount
        
        conn.commit()
        print(f"详细信息更新完成！共更新了 {updated_count} 个单词记录。")
        
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
    
    # 处理所有CSV文件
    for book_type, csv_file in CSV_FILES.items():
        print(f"\n=== 处理{book_type}单词书 ===")
        details_map = extract_details_from_csv(csv_file)
        if details_map:
            update_database_with_details(conn, details_map)
    
    conn.close()
    print("\n详细信息提取和更新操作已完成。")

if __name__ == '__main__':
    main() 