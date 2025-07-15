import sqlite3
import re

def fix_spelling_variants():
    """处理英式/美式拼写变体，将spelling字段格式化为organise/organize形式"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 查找包含"（美"的meaning_cn字段
    cursor.execute("""
        SELECT word_id, spelling, meaning_cn, pos 
        FROM Words 
        WHERE meaning_cn LIKE '%（美%' OR meaning_cn LIKE '%(美%'
    """)
    
    results = cursor.fetchall()
    print(f"找到 {len(results)} 个包含美式拼写的单词")
    
    update_count = 0
    for word_id, spelling, meaning_cn, pos in results:
        # 提取美式拼写
        american_match = re.search(r'（美([^）]+)）|\(美([^)]+)\)', meaning_cn)
        if american_match:
            american_spelling = american_match.group(1) or american_match.group(2)
            
            # 创建新的spelling格式
            new_spelling = f"{spelling}/{american_spelling}"
            
            # 清理meaning_cn，移除"（美xxx）"部分
            new_meaning = re.sub(r'（美[^）]+）|\(美[^)]+\)', '', meaning_cn).strip()
            # 清理多余的分号和空格
            new_meaning = re.sub(r'；+', '；', new_meaning).strip('；')
            
            # 更新数据库
            cursor.execute("""
                UPDATE Words SET spelling = ?, meaning_cn = ? WHERE word_id = ?
            """, (new_spelling, new_meaning, word_id))
            
            update_count += 1
            print(f"修复: {spelling} -> {new_spelling}")
            print(f"  新词义: {new_meaning}")
            print("---")
    
    # 处理一些常见的英式/美式拼写对，如果它们在数据库中同时存在
    common_variants = [
        ('organise', 'organize'),
        ('colour', 'color'),
        ('favour', 'favor'),
        ('labour', 'labor'),
        ('centre', 'center'),
        ('metre', 'meter'),
        ('litre', 'liter'),
        ('theatre', 'theater'),
        ('fibre', 'fiber'),
        ('tyre', 'tire'),
        ('programme', 'program'),
        ('catalogue', 'catalog'),
        ('dialogue', 'dialog'),
        ('analogue', 'analog'),
        ('travelled', 'traveled'),
        ('cancelled', 'canceled'),
        ('modelled', 'modeled'),
        ('levelled', 'leveled'),
        ('jewellery', 'jewelry'),
        ('marvellous', 'marvelous')
    ]
    
    print("\n处理常见的英式/美式拼写对:")
    for british, american in common_variants:
        # 检查是否两个版本都存在
        cursor.execute("SELECT word_id, spelling, meaning_cn FROM Words WHERE spelling = ? OR spelling = ?", (british, american))
        variants = cursor.fetchall()
        
        if len(variants) == 2:
            # 两个版本都存在，需要合并
            british_record = None
            american_record = None
            
            for variant in variants:
                if variant[1] == british:
                    british_record = variant
                elif variant[1] == american:
                    american_record = variant
            
            if british_record and american_record:
                # 保留英式拼写的记录，更新spelling为组合格式
                new_spelling = f"{british}/{american}"
                cursor.execute("""
                    UPDATE Words SET spelling = ? WHERE word_id = ?
                """, (new_spelling, british_record[0]))
                
                # 删除美式拼写的重复记录
                cursor.execute("DELETE FROM Words WHERE word_id = ?", (american_record[0],))
                
                print(f"合并: {british} + {american} -> {new_spelling}")
                print(f"  保留ID: {british_record[0]}, 删除ID: {american_record[0]}")
                update_count += 1
    
    conn.commit()
    print(f"\n修复完成，共更新 {update_count} 个单词")
    conn.close()

def create_spelling_variants_table():
    """创建一个拼写变体表，用于批改时检查"""
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 创建拼写变体表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SpellingVariants (
            variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            spelling_variant TEXT NOT NULL,
            is_primary BOOLEAN DEFAULT 0,
            FOREIGN KEY (word_id) REFERENCES Words(word_id)
        )
    """)
    
    # 从Words表中提取拼写变体
    cursor.execute("SELECT word_id, spelling FROM Words WHERE spelling LIKE '%/%'")
    variant_words = cursor.fetchall()
    
    for word_id, spelling in variant_words:
        variants = spelling.split('/')
        for i, variant in enumerate(variants):
            is_primary = (i == 0)  # 第一个变体作为主要拼写
            cursor.execute("""
                INSERT INTO SpellingVariants (word_id, spelling_variant, is_primary)
                VALUES (?, ?, ?)
            """, (word_id, variant.strip(), is_primary))
    
    conn.commit()
    print(f"拼写变体表创建完成，共处理 {len(variant_words)} 个单词")
    conn.close()

if __name__ == '__main__':
    print("开始处理拼写变体...")
    fix_spelling_variants()
    print("\n创建拼写变体表...")
    create_spelling_variants_table()
    print("所有操作完成！") 