#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SRS增强功能
验证错词优先和掌握度记录功能
"""

from utils import get_database_connection, get_database_path
import sqlite3
import os
from datetime import datetime, timedelta

# 数据库文件路径
DATABASE_FILE = get_database_path()

def test_srs_enhancement():
    """测试SRS增强功能"""
    print("🧪 开始测试SRS增强功能...")
    
    if not os.path.exists(DATABASE_FILE):
        print("❌ 数据库文件不存在，请先运行应用")
        return
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        # 1. 检查表结构
        print("\n1. 检查数据库表结构...")
        
        # 检查StudentWordProgress表
        cursor.execute("PRAGMA table_info(StudentWordProgress)")
        columns = cursor.fetchall()
        print(f"StudentWordProgress表列数: {len(columns)}")
        
        # 检查ErrorLogs表
        cursor.execute("PRAGMA table_info(ErrorLogs)")
        columns = cursor.fetchall()
        print(f"ErrorLogs表列数: {len(columns)}")
        
        # 2. 检查示例数据
        print("\n2. 检查示例数据...")
        
        # 检查用户
        cursor.execute("SELECT id, username FROM Users LIMIT 5")
        users = cursor.fetchall()
        print(f"用户数量: {len(users)}")
        if users:
            print(f"示例用户: {users[0]}")
        
        # 检查单词
        cursor.execute("SELECT word_id, spelling FROM Words LIMIT 5")
        words = cursor.fetchall()
        print(f"单词数量: {len(words)}")
        if words:
            print(f"示例单词: {words[0]}")
        
        # 3. 检查SRS进度
        print("\n3. 检查SRS进度数据...")
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN repetitions = 0 THEN 1 ELSE 0 END) as unfamiliar,
                   SUM(CASE WHEN repetitions = 1 THEN 1 ELSE 0 END) as beginner,
                   SUM(CASE WHEN repetitions > 1 AND repetitions <= 3 THEN 1 ELSE 0 END) as familiar,
                   SUM(CASE WHEN repetitions > 3 AND repetitions <= 10 THEN 1 ELSE 0 END) as mastered,
                   SUM(CASE WHEN repetitions > 10 THEN 1 ELSE 0 END) as expert
            FROM StudentWordProgress
        """)
        stats = cursor.fetchone()
        if stats:
            print(f"总进度记录: {stats[0]}")
            print(f"不熟悉: {stats[1]}")
            print(f"初学: {stats[2]}")
            print(f"熟悉: {stats[3]}")
            print(f"掌握: {stats[4]}")
            print(f"精通: {stats[5]}")
        
        # 4. 检查错词记录
        print("\n4. 检查错词记录...")
        cursor.execute("SELECT COUNT(*) FROM ErrorLogs")
        error_count = cursor.fetchone()[0]
        print(f"错词记录总数: {error_count}")
        
        # 5. 测试错词优先查询
        print("\n5. 测试错词优先查询...")
        if users and words:
            test_user_id = users[0][0]
            
            # 模拟错词优先查询
            cursor.execute("""
                SELECT w.word_id, w.spelling, p.repetitions, p.interval,
                       (SELECT COUNT(*) FROM ErrorLogs e WHERE e.word_id = w.word_id AND e.student_id = p.student_id) as error_count
                FROM StudentWordProgress p
                JOIN Words w ON p.word_id = w.word_id
                WHERE p.student_id = ?
                ORDER BY error_count DESC, p.next_review_date ASC
                LIMIT 10
            """, (test_user_id,))
            
            due_words = cursor.fetchall()
            print(f"待复习单词数量: {len(due_words)}")
            
            if due_words:
                print("前5个待复习单词:")
                for i, word in enumerate(due_words[:5]):
                    print(f"  {i+1}. {word[1]} (掌握度:{word[2]}, 间隔:{word[3]}天, 错误:{word[4]}次)")
        
        # 6. 检查掌握度分布
        print("\n6. 检查掌握度分布...")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN repetitions = 0 THEN '🔴 不熟悉'
                    WHEN repetitions = 1 THEN '🟡 初学'
                    WHEN repetitions <= 3 THEN '🟠 熟悉'
                    WHEN repetitions <= 10 THEN '🟢 掌握'
                    ELSE '🔵 精通'
                END as mastery_level,
                COUNT(*) as count
            FROM StudentWordProgress 
            GROUP BY mastery_level
            ORDER BY 
                CASE mastery_level
                    WHEN '🔴 不熟悉' THEN 1
                    WHEN '🟡 初学' THEN 2
                    WHEN '🟠 熟悉' THEN 3
                    WHEN '🟢 掌握' THEN 4
                    WHEN '🔵 精通' THEN 5
                END
        """)
        
        mastery_distribution = cursor.fetchall()
        print("掌握度分布:")
        for level, count in mastery_distribution:
            print(f"  {level}: {count}个单词")
        
        print("\n✅ SRS增强功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

def simulate_learning_session():
    """模拟学习会话，创建测试数据"""
    print("\n🎯 模拟学习会话...")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        # 获取测试用户
        cursor.execute("SELECT id FROM Users LIMIT 1")
        user = cursor.fetchone()
        if not user:
            print("❌ 没有找到用户，请先注册用户")
            return
        
        user_id = user[0]
        
        # 获取一些单词进行测试
        cursor.execute("SELECT word_id, spelling FROM Words LIMIT 10")
        words = cursor.fetchall()
        
        if not words:
            print("❌ 没有找到单词数据")
            return
        
        print(f"模拟用户 {user_id} 学习 {len(words)} 个单词...")
        
        # 模拟学习过程
        for i, (word_id, spelling) in enumerate(words):
            # 模拟一些答对，一些答错
            is_correct = i % 3 != 0  # 每3个单词错1个
            
            # 获取当前进度
            cursor.execute("""
                SELECT repetitions, interval FROM StudentWordProgress 
                WHERE student_id = ? AND word_id = ?
            """, (user_id, word_id))
            
            progress = cursor.fetchone()
            
            if not progress:
                # 创建新进度
                repetitions = 0
                interval = 1
            else:
                repetitions = progress[0] or 0
                interval = progress[1] or 1
            
            # 根据答案正确性更新进度
            if is_correct:
                if repetitions == 0:
                    repetitions = 1
                    interval = 1
                elif repetitions == 1:
                    repetitions = 2
                    interval = 6
                else:
                    repetitions += 1
                    interval = int(interval * 1.5)
            else:
                # 答错了，记录到ErrorLogs
                cursor.execute("""
                    INSERT INTO ErrorLogs (student_id, word_id, error_type, student_answer, error_date)
                    VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
                """, (user_id, word_id, 'spelling_test', 'wrong_answer'))
                
                if repetitions > 0:
                    repetitions = max(0, repetitions - 1)
                    interval = max(1, interval // 2)
            
            # 限制最大间隔
            interval = min(interval, 365)
            
            # 计算下次复习日期
            next_review_date = (datetime.now() + timedelta(days=interval)).strftime('%Y-%m-%d')
            
            # 更新进度
            cursor.execute("""
                INSERT OR REPLACE INTO StudentWordProgress 
                (student_id, word_id, repetitions, interval, next_review_date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, word_id, repetitions, interval, next_review_date))
            
            status = "✅" if is_correct else "❌"
            print(f"  {status} {spelling} -> 掌握度:{repetitions}, 间隔:{interval}天")
        
        conn.commit()
        print("✅ 模拟学习会话完成！")
        
    except Exception as e:
        print(f"❌ 模拟学习会话出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 SRS增强功能测试工具")
    print("=" * 50)
    
    # 询问是否要模拟学习会话
    choice = input("是否要模拟学习会话来创建测试数据？(y/n): ").lower().strip()
    
    if choice == 'y':
        simulate_learning_session()
    
    # 运行测试
    test_srs_enhancement() 