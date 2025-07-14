#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
同步脚本：将主程序的更改同步到LumiCamp_for_Alan定制版本

使用方法：
    python sync_to_custom.py [选项]

选项：
    --dry-run: 只显示将要同步的文件，不实际执行同步
    --help: 显示帮助信息
"""

import os
import sys
import shutil
import filecmp
import argparse
from datetime import datetime

# 定义主程序和定制版本的路径
MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_DIR = os.path.join(MAIN_DIR, 'LumiCamp_for_Alan')

# 定义需要同步的文件类型
SYNC_EXTENSIONS = [
    '.py',  # Python源文件
    '.html',  # HTML模板
    '.css',  # CSS样式
    '.js',  # JavaScript脚本
    '.svg',  # SVG图像
]

# 定义不需要同步的文件和目录
EXCLUDE_FILES = [
    'app.py',  # 主应用文件可能有定制化修改
    'README.md',  # 定制版本有自己的README
    'CUSTOM_VERSION.md',  # 定制版本标记文件
    '.gitignore',  # Git忽略文件
    'sync_to_custom.py',  # 本同步脚本
    'environment.yml',  # 环境配置文件
]

EXCLUDE_DIRS = [
    '.git',  # Git目录
    '__pycache__',  # Python缓存
    'logs',  # 日志目录
    'env',  # 虚拟环境
    '.venv',  # 虚拟环境
    '.idea',  # IDE配置
    '.vscode',  # IDE配置
]

# 创建备份目录
def create_backup_dir():
    backup_dir = os.path.join(MAIN_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

# 备份文件
def backup_file(file_path, backup_dir):
    if not os.path.exists(file_path):
        return
    
    filename = os.path.basename(file_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
    
    shutil.copy2(file_path, backup_path)
    print(f"已备份: {file_path} -> {backup_path}")

# 同步文件
def sync_file(src, dst, dry_run=False, backup_dir=None):
    # 检查源文件是否存在
    if not os.path.exists(src):
        print(f"源文件不存在: {src}")
        return False
    
    # 检查目标目录是否存在，不存在则创建
    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
        if not dry_run:
            os.makedirs(dst_dir)
        print(f"创建目录: {dst_dir}")
    
    # 检查文件是否相同
    if os.path.exists(dst) and filecmp.cmp(src, dst):
        print(f"文件相同，跳过: {src}")
        return False
    
    # 备份目标文件
    if backup_dir and os.path.exists(dst):
        backup_file(dst, backup_dir)
    
    # 复制文件
    if not dry_run:
        shutil.copy2(src, dst)
    
    print(f"{'将要同步' if dry_run else '已同步'}: {src} -> {dst}")
    return True

# 同步目录
def sync_directory(src_dir, dst_dir, dry_run=False):
    if not os.path.exists(src_dir):
        print(f"源目录不存在: {src_dir}")
        return
    
    backup_dir = create_backup_dir() if not dry_run else None
    synced_files = 0
    
    for root, dirs, files in os.walk(src_dir):
        # 排除不需要同步的目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # 计算相对路径
        rel_path = os.path.relpath(root, src_dir)
        
        # 处理文件
        for file in files:
            # 排除不需要同步的文件
            if file in EXCLUDE_FILES:
                continue
            
            # 检查文件扩展名
            _, ext = os.path.splitext(file)
            if ext not in SYNC_EXTENSIONS:
                continue
            
            # 构建源文件和目标文件的完整路径
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_dir, rel_path, file) if rel_path != '.' else os.path.join(dst_dir, file)
            
            # 同步文件
            if sync_file(src_file, dst_file, dry_run, backup_dir):
                synced_files += 1
    
    return synced_files

# 主函数
def main():
    parser = argparse.ArgumentParser(description='将主程序的更改同步到LumiCamp_for_Alan定制版本')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要同步的文件，不实际执行同步')
    args = parser.parse_args()
    
    print("=" * 80)
    print(f"开始{'模拟' if args.dry_run else ''}同步主程序到定制版本")
    print(f"主程序目录: {MAIN_DIR}")
    print(f"定制版本目录: {CUSTOM_DIR}")
    print("=" * 80)
    
    # 检查定制版本目录是否存在
    if not os.path.exists(CUSTOM_DIR):
        print(f"错误: 定制版本目录不存在: {CUSTOM_DIR}")
        return 1
    
    # 同步文件
    synced_files = sync_directory(MAIN_DIR, CUSTOM_DIR, args.dry_run)
    
    print("=" * 80)
    print(f"同步{'模拟' if args.dry_run else ''}完成，{'将要' if args.dry_run else '已'}同步 {synced_files} 个文件")
    if args.dry_run:
        print("提示: 使用 python sync_to_custom.py 执行实际同步")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())