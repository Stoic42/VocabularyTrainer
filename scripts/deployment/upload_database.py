#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传数据库到服务器脚本

使用方法：
    python upload_database.py [服务器IP] [用户名]

示例：
    python upload_database.py 82.157.204.20 root
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def get_database_path():
    """获取数据库文件路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(project_root, 'vocabulary.db')

def backup_database():
    """备份当前数据库"""
    db_path = get_database_path()
    if not os.path.exists(db_path):
        print(f"错误：数据库文件不存在: {db_path}")
        return None
    
    # 创建备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"✓ 数据库已备份到: {backup_path}")
    return backup_path

def upload_database(server_ip, username):
    """上传数据库到服务器"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"错误：数据库文件不存在: {db_path}")
        return False
    
    # 检查数据库文件大小
    file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    print(f"数据库文件大小: {file_size:.2f} MB")
    
    # 构建scp命令
    scp_command = [
        'scp',
        db_path,
        f'{username}@{server_ip}:/var/www/vocabulary/'
    ]
    
    print(f"正在上传数据库到服务器...")
    print(f"命令: {' '.join(scp_command)}")
    
    try:
        # 执行scp命令
        result = subprocess.run(scp_command, check=True, capture_output=True, text=True)
        print("✓ 数据库上传成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 上传失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ 错误：未找到scp命令，请确保已安装SSH客户端")
        return False

def set_server_permissions(server_ip, username):
    """设置服务器上的文件权限"""
    print("正在设置服务器文件权限...")
    
    ssh_commands = [
        f'ssh {username}@{server_ip} "sudo chmod 644 /var/www/vocabulary/vocabulary.db"',
        f'ssh {username}@{server_ip} "sudo chown www-data:www-data /var/www/vocabulary/vocabulary.db"',
        f'ssh {username}@{server_ip} "sudo systemctl restart vocabulary"'
    ]
    
    for command in ssh_commands:
        try:
            print(f"执行: {command}")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("✓ 命令执行成功")
        except subprocess.CalledProcessError as e:
            print(f"⚠ 命令执行失败: {e}")
            print(f"错误输出: {e.stderr}")

def check_server_status(server_ip, username):
    """检查服务器状态"""
    print("检查服务器状态...")
    
    check_commands = [
        f'ssh {username}@{server_ip} "sudo systemctl status vocabulary"',
        f'ssh {username}@{server_ip} "curl -s http://127.0.0.1:8000 | head -20"'
    ]
    
    for command in check_commands:
        try:
            print(f"执行: {command}")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("✓ 服务状态正常")
            if "curl" in command:
                print("应用响应正常")
        except subprocess.CalledProcessError as e:
            print(f"⚠ 检查失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("使用方法: python upload_database.py [服务器IP] [用户名]")
        print("示例: python upload_database.py 82.157.204.20 root")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    username = sys.argv[2]
    
    print("=" * 50)
    print("词汇训练营 - 数据库上传脚本")
    print("=" * 50)
    print(f"服务器: {username}@{server_ip}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 备份数据库
    print("步骤 1: 备份当前数据库")
    backup_path = backup_database()
    if not backup_path:
        sys.exit(1)
    
    # 2. 上传数据库
    print("\n步骤 2: 上传数据库到服务器")
    if not upload_database(server_ip, username):
        print("上传失败，请检查网络连接和服务器状态")
        sys.exit(1)
    
    # 3. 设置权限
    print("\n步骤 3: 设置服务器文件权限")
    set_server_permissions(server_ip, username)
    
    # 4. 检查状态
    print("\n步骤 4: 检查服务器状态")
    check_server_status(server_ip, username)
    
    print("\n" + "=" * 50)
    print("✓ 数据库上传完成！")
    print("=" * 50)

if __name__ == "__main__":
    main() 