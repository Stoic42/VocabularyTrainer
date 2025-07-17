#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复原始数据源文件中的"poun"拼写错误
"""

import os
import shutil
from datetime import datetime

# 配置
SOURCE_FILES = [
    'wordlists/junior_high/初中 乱序 绿宝书.txt',
    'wordlists/junior_high/junior_high_vocab_random.csv'
]

def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"✓ 已备份：{file_path} → {backup_path}")
        return backup_path
    return None

def fix_txt_file(file_path):
    """修复TXT文件中的'poun'拼写错误"""
    print(f"\n正在修复TXT文件：{file_path}")
    
    if not os.path.exists(file_path):
        print(f"⚠ 文件不存在：{file_path}")
        return False
    
    # 备份文件
    backup_path = backup_file(file_path)
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 统计替换次数
        original_count = content.count('poun')
        if original_count == 0:
            print("✓ 文件中没有找到'poun'，无需修复")
            return True
        
        # 替换'poun'为'pound'
        new_content = content.replace('poun', 'pound')
        new_count = new_content.count('pound') - content.count('pound')
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ 修复完成：替换了 {new_count} 个'poun'为'pound'")
        return True
        
    except Exception as e:
        print(f"✗ 修复TXT文件时出错：{e}")
        # 恢复备份
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"✓ 已恢复备份：{backup_path}")
        return False

def fix_csv_file(file_path):
    """修复CSV文件中的'poun'拼写错误"""
    print(f"\n正在修复CSV文件：{file_path}")
    
    if not os.path.exists(file_path):
        print(f"⚠ 文件不存在：{file_path}")
        return False
    
    # 备份文件
    backup_path = backup_file(file_path)
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        # 查找并修复包含'poun'的行
        fixed_count = 0
        for i, line in enumerate(lines):
            if 'poun,' in line:
                lines[i] = line.replace('poun,', 'pound,')
                fixed_count += 1
                print(f"  修复第 {i+1} 行：'poun,' → 'pound,'")
        
        if fixed_count == 0:
            print("✓ 文件中没有找到'poun,'，无需修复")
            return True
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(lines)
        
        print(f"✓ 修复完成：修复了 {fixed_count} 行")
        return True
        
    except Exception as e:
        print(f"✗ 修复CSV文件时出错：{e}")
        # 恢复备份
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"✓ 已恢复备份：{backup_path}")
        return False

def main():
    """主函数"""
    print("===== 修复原始数据源文件中的'poun'拼写错误 =====")
    
    success_count = 0
    total_count = len(SOURCE_FILES)
    
    for file_path in SOURCE_FILES:
        print(f"\n--- 处理文件：{file_path} ---")
        
        if file_path.endswith('.txt'):
            success = fix_txt_file(file_path)
        elif file_path.endswith('.csv'):
            success = fix_csv_file(file_path)
        else:
            print(f"⚠ 不支持的文件类型：{file_path}")
            success = False
        
        if success:
            success_count += 1
    
    print(f"\n===== 修复完成 =====")
    print(f"成功修复：{success_count}/{total_count} 个文件")
    
    if success_count == total_count:
        print("✓ 所有文件修复成功！")
    else:
        print("⚠ 部分文件修复失败，请检查错误信息")

if __name__ == "__main__":
    main() 