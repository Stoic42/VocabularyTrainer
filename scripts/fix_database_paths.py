#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动检测和修复脚本中的数据库路径引用
确保所有脚本都使用utils模块的get_database_path函数
"""

import os
import re
import glob
import sys

def find_python_files():
    """查找所有Python脚本文件"""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    python_files = []
    
    # 递归查找所有.py文件
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith('.py') and file != 'utils.py' and file != 'fix_database_paths.py':
                python_files.append(os.path.join(root, file))
    
    return python_files

def check_file_path_usage(file_path):
    """检查文件中的数据库路径使用情况"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 检查是否直接使用了vocabulary.db
        if re.search(r'[\'"](vocabulary\.db)[\'"]', content):
            issues.append("直接使用vocabulary.db字符串")
        
        # 检查是否使用了os.path.join拼接vocabulary.db
        if re.search(r'os\.path\.join.*vocabulary\.db', content):
            issues.append("使用os.path.join拼接vocabulary.db")
        
        # 检查是否导入了utils模块
        if 'from utils import' not in content and 'import utils' not in content:
            if 'sqlite3.connect' in content:
                issues.append("未导入utils模块但使用了数据库连接")
        
        # 检查是否使用了get_database_path
        if 'get_database_path' not in content and 'sqlite3.connect' in content:
            issues.append("未使用get_database_path函数")
        
        return issues
    
    except Exception as e:
        return [f"读取文件时出错: {e}"]

def fix_file_path_usage(file_path):
    """修复文件中的数据库路径使用"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # 添加sys导入（如果需要）
        if 'import sys' not in content and ('from utils import' in content or 'import utils' in content):
            if 'import os' in content:
                content = re.sub(r'(import os)', r'\1\nimport sys', content)
            else:
                content = re.sub(r'(import sqlite3)', r'import os\nimport sys\n\1', content)
            modified = True
        
        # 添加utils导入
        if 'from utils import' not in content and 'import utils' not in content:
            if 'import sqlite3' in content:
                # 添加sys.path设置
                sys_path_code = '''# 添加scripts目录到Python路径，确保能导入utils模块
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.dirname(current_dir)
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from utils import get_database_path
'''
                content = re.sub(r'(import sqlite3.*?\n)', r'\1\n' + sys_path_code, content)
                modified = True
        
        # 替换直接的vocabulary.db字符串
        content = re.sub(
            r'[\'"](vocabulary\.db)[\'"]',
            'get_database_path()',
            content
        )
        if content != original_content:
            modified = True
        
        # 替换os.path.join拼接vocabulary.db
        content = re.sub(
            r'os\.path\.join\([^,]+,\s*[\'"](vocabulary\.db)[\'"]\)',
            'get_database_path()',
            content
        )
        if content != original_content:
            modified = True
        
        # 替换变量定义
        content = re.sub(
            r'(\w+)\s*=\s*[\'"](vocabulary\.db)[\'"]',
            r'\1 = get_database_path()',
            content
        )
        if content != original_content:
            modified = True
        
        # 替换sqlite3.connect调用
        content = re.sub(
            r'sqlite3\.connect\([\'"](vocabulary\.db)[\'"]\)',
            'sqlite3.connect(get_database_path())',
            content
        )
        if content != original_content:
            modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"修复文件 {file_path} 时出错: {e}")
        return False

def main():
    """主函数"""
    print("=== 数据库路径检测和修复工具 ===")
    
    python_files = find_python_files()
    print(f"找到 {len(python_files)} 个Python脚本文件")
    
    files_with_issues = []
    files_fixed = []
    
    for file_path in python_files:
        relative_path = os.path.relpath(file_path)
        issues = check_file_path_usage(file_path)
        
        if issues:
            files_with_issues.append((file_path, issues))
            print(f"\n❌ {relative_path}")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"✅ {relative_path}")
    
    if files_with_issues:
        print(f"\n发现 {len(files_with_issues)} 个文件有路径问题")
        
        response = input("\n是否要自动修复这些问题？(y/n): ").strip().lower()
        if response in ['y', 'yes', '是']:
            print("\n开始修复...")
            
            for file_path, issues in files_with_issues:
                if fix_file_path_usage(file_path):
                    files_fixed.append(file_path)
                    print(f"✅ 已修复: {os.path.relpath(file_path)}")
                else:
                    print(f"❌ 修复失败: {os.path.relpath(file_path)}")
            
            print(f"\n修复完成！共修复了 {len(files_fixed)} 个文件")
        else:
            print("跳过自动修复")
    else:
        print("\n🎉 所有脚本都已正确使用数据库路径！")

if __name__ == "__main__":
    main() 