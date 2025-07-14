#!/usr/bin/env python3
"""
清理脚本：解决日志文件锁定问题并启动应用
"""
import os
import sys
import time
import shutil
from pathlib import Path

def cleanup_logs():
    """清理日志文件"""
    logs_dir = Path('logs')
    if logs_dir.exists():
        print("正在清理日志文件...")
        try:
            # 重命名现有的日志文件以避免冲突
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            if (logs_dir / 'app.log').exists():
                backup_name = f'app.log.backup_{timestamp}'
                shutil.move(str(logs_dir / 'app.log'), str(logs_dir / backup_name))
                print(f"已备份 app.log 为 {backup_name}")
            
            # 清理旧的备份文件
            for backup_file in logs_dir.glob('app.log.*'):
                if backup_file.is_file():
                    backup_file.unlink()
                    print(f"已删除旧备份文件: {backup_file}")
                    
        except Exception as e:
            print(f"清理日志文件时出错: {e}")
    else:
        print("logs 目录不存在，将创建新目录")

def main():
    print("=== 词汇训练器启动脚本 ===")
    
    # 清理日志文件
    cleanup_logs()
    
    # 等待一下确保文件系统操作完成
    time.sleep(1)
    
    print("正在启动应用...")
    
    # 启动应用
    try:
        import app
        print("应用启动成功！")
    except Exception as e:
        print(f"启动应用时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 