"""
修复脚本中的导入路径
"""
import os
import re

def fix_imports_in_file(file_path):
    """修复单个文件中的导入路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复utils导入
        if 'from utils import' in content:
            # 计算相对路径
            file_dir = os.path.dirname(file_path)
            scripts_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 计算从文件所在目录到scripts目录的相对路径
            rel_path = os.path.relpath(scripts_dir, file_dir)
            if rel_path == '.':
                import_path = 'from utils import'
            else:
                import_path = f'from {rel_path.replace(os.sep, ".")}.utils import'
            
            content = re.sub(
                r'from utils import',
                import_path,
                content
            )
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已修复导入: {file_path}")
            return True
        else:
            print(f"无需修复导入: {file_path}")
            return False
            
    except Exception as e:
        print(f"修复导入失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 获取scripts目录下的所有Python文件
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    python_files = []
    
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith('.py') and file != 'utils.py' and file != 'fix_paths.py' and file != 'fix_imports.py':
                python_files.append(os.path.join(root, file))
    
    print(f"找到 {len(python_files)} 个Python文件需要检查导入")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n导入修复完成！共修复了 {fixed_count} 个文件")

if __name__ == '__main__':
    main() 