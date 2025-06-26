#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
注入新版本的 fix_mess_display.js 脚本到应用程序中
该脚本将重新设计错误历史和出题界面中词性和义项的显示逻辑
"""

import os
import shutil
import re
from datetime import datetime
from flask import send_from_directory

# 定义文件路径
APP_PY = 'app.py'
ERROR_HISTORY_HTML = 'templates/error_history.html'
INDEX_HTML = 'templates/index.html'
FIX_MESS_DISPLAY_JS = 'fix_mess_display_new.js'

# 备份文件
def backup_file(file_path):
    """
    创建文件的备份
    """
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"已创建备份: {backup_path}")
        return True
    else:
        print(f"文件不存在，无法备份: {file_path}")
        return False

# 注入脚本到 HTML 文件
def inject_script_to_html(html_file, script_tag):
    """
    向 HTML 文件中注入脚本标签
    """
    if not os.path.exists(html_file):
        print(f"HTML 文件不存在: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经注入了脚本
    if script_tag in content:
        print(f"脚本已存在于 {html_file} 中")
        return True
    
    # 在 </body> 标签前插入脚本
    if '</body>' in content:
        new_content = content.replace('</body>', f'{script_tag}\n</body>')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"已向 {html_file} 注入脚本")
        return True
    else:
        print(f"未找到 </body> 标签在 {html_file} 中")
        return False

# 向 app.py 添加路由
def add_route_to_app(app_py, js_file):
    """
    向 app.py 添加提供 JS 文件的路由
    """
    if not os.path.exists(app_py):
        print(f"app.py 文件不存在: {app_py}")
        return False
    
    with open(app_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经添加了路由
    route_pattern = rf"@app\.route\(\s*['\"]/{os.path.basename(js_file)}['\"]\s*\)"
    if re.search(route_pattern, content):
        print(f"路由已存在于 {app_py} 中")
        return True
    
    # 检查是否导入了 send_from_directory
    if 'from flask import send_from_directory' not in content and 'send_from_directory' not in content:
        # 在第一个 flask 导入后添加 send_from_directory
        content = re.sub(
            r'from flask import ([^\n]+)',
            r'from flask import \1, send_from_directory',
            content,
            count=1
        )
    
    # 添加路由函数
    route_function = f"""
@app.route('/{os.path.basename(js_file)}')
def get_fix_mess_display_new_js():
    return send_from_directory('.', '{js_file}')
"""
    
    # 在文件末尾添加路由函数
    if 'if __name__ == "__main__":' in content:
        content = content.replace(
            'if __name__ == "__main__":',
            f'{route_function}\nif __name__ == "__main__":'
        )
    else:
        content += f"\n{route_function}\n"
    
    with open(app_py, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已向 {app_py} 添加路由")
    return True

# 主函数
def main():
    """
    主函数，执行注入过程
    """
    print("开始注入新版本的 fix_mess_display.js 脚本...")
    
    # 备份文件
    backup_file(ERROR_HISTORY_HTML)
    backup_file(INDEX_HTML)
    backup_file(APP_PY)
    
    # 创建脚本标签
    script_tag = f'<script src="/{os.path.basename(FIX_MESS_DISPLAY_JS)}"></script>'
    
    # 注入脚本到 HTML 文件
    inject_script_to_html(ERROR_HISTORY_HTML, script_tag)
    inject_script_to_html(INDEX_HTML, script_tag)
    
    # 添加路由到 app.py
    add_route_to_app(APP_PY, FIX_MESS_DISPLAY_JS)
    
    print("注入完成！请重启应用程序以应用更改。")

if __name__ == "__main__":
    main()