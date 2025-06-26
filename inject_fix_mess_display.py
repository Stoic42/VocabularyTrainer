import os
import re
import shutil
import datetime

# 定义文件路径
template_dir = 'd:/Projects/VocabularyTrainer/templates'
error_history_path = os.path.join(template_dir, 'error_history.html')

# 创建备份目录
backup_dir = os.path.join('d:/Projects/VocabularyTrainer', 'backups')
os.makedirs(backup_dir, exist_ok=True)

# 创建备份文件名
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(backup_dir, f'error_history.html.{timestamp}.bak')

# 备份原始文件
shutil.copy2(error_history_path, backup_file)
print(f'已创建备份: {backup_file}')

# 读取错误历史页面内容
with open(error_history_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 检查是否已经注入了修复脚本
if 'fix_mess_display.js' in content:
    print('修复脚本已经注入，无需重复操作')
    exit(0)

# 在</body>标签前注入修复脚本
fix_script = '\n<!-- 修复单词"mess"被错误显示为"mass"的问题 -->\n'
fix_script += '<script src="/fix_mess_display.js"></script>\n'

# 使用正则表达式在</body>标签前插入脚本
modified_content = re.sub(r'(\s*</body>)', f'{fix_script}\1', content)

# 写入修改后的内容
with open(error_history_path, 'w', encoding='utf-8') as file:
    file.write(modified_content)

print(f'已成功注入修复脚本到 {error_history_path}')

# 修改app.py以提供静态文件访问
app_path = 'd:/Projects/VocabularyTrainer/app.py'

# 备份app.py
app_backup_file = os.path.join(backup_dir, f'app.py.{timestamp}.bak')
shutil.copy2(app_path, app_backup_file)
print(f'已创建备份: {app_backup_file}')

# 读取app.py内容
with open(app_path, 'r', encoding='utf-8') as file:
    app_content = file.read()

# 检查是否需要添加静态文件路由
if 'fix_mess_display.js' in app_content:
    print('app.py中已存在修复脚本的路由，无需修改')
else:
    # 查找静态文件路由部分
    static_route_pattern = r'@app\.route\([\'"]/([^\'"]+)[\'"]\)\s*def\s+get_static_file\([^)]*\):\s*.*?return\s+send_from_directory\([^)]*\)'
    static_route_match = re.search(static_route_pattern, app_content, re.DOTALL)
    
    if static_route_match:
        print('找到现有的静态文件路由，添加修复脚本路由')
        # 在现有路由后添加新路由
        new_route = '''
# 提供修复脚本访问
@app.route('/fix_mess_display.js')
def get_fix_mess_display_js():
    return send_from_directory('.', 'fix_mess_display.js')
'''
        # 在最后一个路由后添加新路由
        app_content = re.sub(r'(# --- PDF导出功能 ---)', f'{new_route}\n\n\1', app_content)
    else:
        print('未找到静态文件路由，添加新的路由')
        # 在app.py末尾添加新路由
        new_route = '''
# 提供修复脚本访问
@app.route('/fix_mess_display.js')
def get_fix_mess_display_js():
    return send_from_directory('.', 'fix_mess_display.js')
'''
        app_content += f'\n{new_route}\n'
    
    # 确保导入了send_from_directory
    if 'from flask import send_from_directory' not in app_content:
        app_content = re.sub(r'from flask import ([^\n]*)', r'from flask import \1, send_from_directory', app_content)
    
    # 写入修改后的app.py
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(app_content)
    
    print(f'已成功修改 {app_path} 添加修复脚本路由')

print('修复脚本注入完成，请重启应用以应用更改')