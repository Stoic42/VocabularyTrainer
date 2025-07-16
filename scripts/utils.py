"""
工具模块 - 提供通用的路径和数据库连接功能
"""
import os
import sqlite3
import sys

# 添加scripts目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def get_project_root():
    """
    获取项目根目录路径
    从当前脚本位置向上查找，直到找到包含app.py的目录
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 从scripts目录向上查找项目根目录
    while current_dir and not os.path.exists(os.path.join(current_dir, 'app.py')):
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # 到达根目录
            break
        current_dir = parent_dir
    
    return current_dir

def get_database_path():
    """
    获取数据库文件的完整路径
    """
    project_root = get_project_root()
    return os.path.join(project_root, 'vocabulary.db')

def get_database_connection():
    """
    获取数据库连接
    """
    db_path = get_database_path()
    return sqlite3.connect(db_path)

def get_wordlists_path():
    """
    获取wordlists目录的完整路径
    """
    project_root = get_project_root()
    return os.path.join(project_root, 'wordlists')

def get_assets_path():
    """
    获取assets目录的完整路径
    """
    project_root = get_project_root()
    return os.path.join(project_root, 'assets') 