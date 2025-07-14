"""
批量修复脚本中的路径引用
将相对路径的数据库引用改为使用utils模块
"""
import os
import re
import glob

def fix_database_paths_in_file(file_path):
    """修复单个文件中的数据库路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 添加utils导入
        if 'import sqlite3' in content and 'from utils import' not in content:
            content = re.sub(
                r'(import sqlite3)',
                r'from utils import get_database_connection, get_database_path\n\1',
                content
            )
        
        # 替换直接的数据库连接
        content = re.sub(
            r'sqlite3\.connect\([\'"](vocabulary\.db|d:\\\\Projects\\\\VocabularyTrainer\\\\vocabulary\.db|d:/Projects/VocabularyTrainer/vocabulary\.db)[\'"]\)',
            'get_database_connection()',
            content
        )
        
        # 替换DATABASE_FILE变量定义
        content = re.sub(
            r'DATABASE_FILE\s*=\s*[\'"](vocabulary\.db|d:\\\\Projects\\\\VocabularyTrainer\\\\vocabulary\.db|d:/Projects/VocabularyTrainer/vocabulary\.db)[\'"]',
            'DATABASE_FILE = get_database_path()',
            content
        )
        
        # 替换target_db变量定义
        content = re.sub(
            r'target_db\s*=\s*[\'"](vocabulary\.db)[\'"]',
            'target_db = get_database_path()',
            content
        )
        
        # 替换直接的vocabulary.db字符串
        content = re.sub(
            r'[\'"](vocabulary\.db)[\'"]',
            'get_database_path()',
            content
        )
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已修复: {file_path}")
            return True
        else:
            print(f"无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"修复失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 获取scripts目录下的所有Python文件
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    python_files = []
    
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith('.py') and file != 'utils.py' and file != 'fix_paths.py':
                python_files.append(os.path.join(root, file))
    
    print(f"找到 {len(python_files)} 个Python文件需要检查")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_database_paths_in_file(file_path):
            fixed_count += 1
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件")

if __name__ == '__main__':
    main() 