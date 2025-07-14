#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
词性和意思显示修复脚本注入工具

该脚本用于将修复脚本注入到LumiCamp_for_Alan的HTML模板中，
以修复考核和错词界面中词性和意思的显示问题。
"""

import os
import sys
import shutil
import argparse
from datetime import datetime

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LUMICAMP_DIR = os.path.join(BASE_DIR, 'LumiCamp_for_Alan')
TEMPLATES_DIR = os.path.join(LUMICAMP_DIR, 'templates')
STATIC_DIR = os.path.join(LUMICAMP_DIR, 'static')
JS_DIR = os.path.join(STATIC_DIR, 'js')

# 修复脚本路径
FIX_SCRIPT_PATH = os.path.join(BASE_DIR, 'fix_pos_meaning_display.js')

# 需要修改的模板文件
TEMPLATE_FILES = [
    os.path.join(TEMPLATES_DIR, 'index.html'),
    os.path.join(TEMPLATES_DIR, 'error_history.html')
]

# 注入脚本标签
SCRIPT_TAG = '<script src="/static/js/fix_pos_meaning_display.js"></script>'


def backup_file(file_path):
    """
    备份文件
    """
    backup_dir = os.path.join(BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.basename(file_path)
    backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
    
    shutil.copy2(file_path, backup_path)
    print(f"已备份文件: {backup_path}")
    return backup_path


def inject_script(file_path, script_tag):
    """
    向HTML文件注入脚本标签
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查脚本是否已经注入
    if script_tag in content:
        print(f"脚本已存在于 {file_path}")
        return False
    
    # 在</body>标签前注入脚本
    if '</body>' in content:
        new_content = content.replace('</body>', f"{script_tag}\n</body>")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"已向 {file_path} 注入脚本")
        return True
    else:
        print(f"无法在 {file_path} 中找到</body>标签")
        return False


def remove_script(file_path, script_tag):
    """
    从HTML文件中移除脚本标签
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查脚本是否存在
    if script_tag not in content:
        print(f"脚本不存在于 {file_path}")
        return False
    
    # 移除脚本标签
    new_content = content.replace(script_tag, '')
    new_content = new_content.replace(f"{script_tag}\n", '')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已从 {file_path} 移除脚本")
    return True


def copy_fix_script():
    """
    复制修复脚本到LumiCamp_for_Alan的静态文件目录
    """
    if not os.path.exists(JS_DIR):
        os.makedirs(JS_DIR)
    
    dest_path = os.path.join(JS_DIR, 'fix_pos_meaning_display.js')
    shutil.copy2(FIX_SCRIPT_PATH, dest_path)
    print(f"已复制修复脚本到 {dest_path}")
    return dest_path


def main():
    parser = argparse.ArgumentParser(description='词性和意思显示修复脚本注入工具')
    parser.add_argument('--action', choices=['inject', 'remove'], default='inject',
                        help='执行操作: inject(注入脚本) 或 remove(移除脚本)')
    parser.add_argument('--no-backup', action='store_true', help='不备份原始文件')
    
    args = parser.parse_args()
    
    # 检查LumiCamp_for_Alan目录是否存在
    if not os.path.exists(LUMICAMP_DIR):
        print(f"错误: LumiCamp_for_Alan目录不存在: {LUMICAMP_DIR}")
        return 1
    
    # 检查模板文件是否存在
    for template_file in TEMPLATE_FILES:
        if not os.path.exists(template_file):
            print(f"错误: 模板文件不存在: {template_file}")
            return 1
    
    if args.action == 'inject':
        # 检查修复脚本是否存在
        if not os.path.exists(FIX_SCRIPT_PATH):
            print(f"错误: 修复脚本不存在: {FIX_SCRIPT_PATH}")
            return 1
        
        # 复制修复脚本
        copy_fix_script()
        
        # 注入脚本
        for template_file in TEMPLATE_FILES:
            if not args.no_backup:
                backup_file(template_file)
            inject_script(template_file, SCRIPT_TAG)
        
        print("\n修复脚本注入完成！请刷新考核和错词页面查看效果。")
    
    elif args.action == 'remove':
        # 移除脚本
        for template_file in TEMPLATE_FILES:
            if not args.no_backup:
                backup_file(template_file)
            remove_script(template_file, SCRIPT_TAG)
        
        # 删除修复脚本
        script_path = os.path.join(JS_DIR, 'fix_pos_meaning_display.js')
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"已删除修复脚本: {script_path}")
        
        print("\n修复脚本移除完成！")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())