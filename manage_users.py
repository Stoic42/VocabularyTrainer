import sqlite3
import os
from werkzeug.security import generate_password_hash

# 数据库文件路径
DATABASE_FILE = 'vocabulary.db'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table_if_not_exists():
    """如果用户表不存在，则创建它"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student', 'admin'))
    );
    """)
    
    conn.commit()
    conn.close()
    print("用户表已确认或创建。")

def list_users():
    """列出所有用户"""
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, role FROM Users ORDER BY id').fetchall()
    conn.close()
    
    if not users:
        print("\n当前没有用户。")
        return
    
    print("\n当前用户列表:")
    print("-" * 40)
    print(f"{'ID':<5} {'用户名':<20} {'角色':<10}")
    print("-" * 40)
    for user in users:
        print(f"{user['id']:<5} {user['username']:<20} {user['role']:<10}")
    print("-" * 40)

def create_user(username, password, role='student'):
    """创建新用户"""
    if not username or not password:
        print("错误: 用户名和密码不能为空")
        return False
    
    if role not in ['student', 'admin']:
        print("错误: 角色必须是 'student' 或 'admin'")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户名是否已存在
    user = cursor.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
    if user:
        print(f"错误: 用户名 '{username}' 已存在")
        conn.close()
        return False
    
    # 将密码加密后存储
    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute('INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)', 
                      (username, password_hash, role))
        conn.commit()
        print(f"成功: 用户 '{username}' 已创建，角色为 '{role}'")
        return True
    except sqlite3.Error as e:
        print(f"错误: 创建用户时出错: {e}")
        return False
    finally:
        conn.close()

def change_user_role(user_id, new_role):
    """修改用户角色"""
    if new_role not in ['student', 'admin']:
        print("错误: 角色必须是 'student' 或 'admin'")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户是否存在
    user = cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        print(f"错误: 用户ID {user_id} 不存在")
        conn.close()
        return False
    
    try:
        cursor.execute('UPDATE Users SET role = ? WHERE id = ?', (new_role, user_id))
        conn.commit()
        print(f"成功: 用户 '{user['username']}' 的角色已更改为 '{new_role}'")
        return True
    except sqlite3.Error as e:
        print(f"错误: 修改用户角色时出错: {e}")
        return False
    finally:
        conn.close()

def delete_user(user_id):
    """删除用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户是否存在
    user = cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        print(f"错误: 用户ID {user_id} 不存在")
        conn.close()
        return False
    
    try:
        cursor.execute('DELETE FROM Users WHERE id = ?', (user_id,))
        conn.commit()
        print(f"成功: 用户 '{user['username']}' 已删除")
        return True
    except sqlite3.Error as e:
        print(f"错误: 删除用户时出错: {e}")
        return False
    finally:
        conn.close()

def main_menu():
    """主菜单"""
    while True:
        print("\n===== 用户管理系统 =====")
        print("1. 列出所有用户")
        print("2. 创建新用户")
        print("3. 修改用户角色")
        print("4. 删除用户")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-4): ")
        
        if choice == '0':
            print("感谢使用，再见！")
            break
        elif choice == '1':
            list_users()
        elif choice == '2':
            username = input("请输入用户名: ")
            password = input("请输入密码: ")
            role = input("请输入角色 (student/admin，默认为student): ").lower() or 'student'
            create_user(username, password, role)
        elif choice == '3':
            list_users()
            user_id = input("请输入要修改的用户ID: ")
            new_role = input("请输入新角色 (student/admin): ").lower()
            change_user_role(user_id, new_role)
        elif choice == '4':
            list_users()
            user_id = input("请输入要删除的用户ID: ")
            confirm = input(f"确定要删除用户ID {user_id} 吗？(y/n): ").lower()
            if confirm == 'y':
                delete_user(user_id)
        else:
            print("无效的选择，请重试。")

if __name__ == '__main__':
    # 检查数据库文件是否存在
    if not os.path.exists(DATABASE_FILE):
        print(f"错误: 数据库文件 '{DATABASE_FILE}' 不存在。请先运行 import_data.py 创建数据库。")
        sys.exit(1)
    
    # 确保用户表存在
    create_users_table_if_not_exists()
    
    # 检查是否有命令行参数
    import sys
    if len(sys.argv) > 1:
        # 快速创建管理员用户
        if sys.argv[1] == 'create_admin':
            if len(sys.argv) >= 4:
                username = sys.argv[2]
                password = sys.argv[3]
                create_user(username, password, 'admin')
                sys.exit(0)
            else:
                print("用法: python manage_users.py create_admin <username> <password>")
                sys.exit(1)
        # 快速创建学生用户
        elif sys.argv[1] == 'create_student':
            if len(sys.argv) >= 4:
                username = sys.argv[2]
                password = sys.argv[3]
                create_user(username, password, 'student')
                sys.exit(0)
            else:
                print("用法: python manage_users.py create_student <username> <password>")
                sys.exit(1)
        # 列出所有用户
        elif sys.argv[1] == 'list':
            list_users()
            sys.exit(0)
        else:
            print("未知的命令行参数。可用命令: create_admin, create_student, list")
            print("用法:")
            print("  python manage_users.py create_admin <username> <password>")
            print("  python manage_users.py create_student <username> <password>")
            print("  python manage_users.py list")
            sys.exit(1)
    else:
        # 启动交互式菜单
        try:
            main_menu()
        except KeyboardInterrupt:
            print("\n程序被用户中断，退出。")
            sys.exit(0)