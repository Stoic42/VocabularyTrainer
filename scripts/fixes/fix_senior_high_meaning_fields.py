import sqlite3
import re

def clean_meaning_fields():
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()

    # 只处理高中英语词汇
    cursor.execute('''
        SELECT w.word_id, w.spelling, w.meaning_cn, w.exam_sentence, w.derivatives
        FROM Words w
        JOIN WordLists wl ON w.list_id = wl.list_id
        JOIN Books b ON wl.book_id = b.book_id
        WHERE b.book_name = '高中英语词汇'
        AND (w.meaning_cn LIKE '%例%' OR w.meaning_cn LIKE '%参%' OR w.meaning_cn LIKE '%考%')
    ''')
    rows = cursor.fetchall()
    print(f'共需修复 {len(rows)} 个单词')

    update_count = 0
    for word_id, spelling, meaning_cn, exam_sentence, derivatives in rows:
        if not meaning_cn:
            continue
        lines = meaning_cn.split('；')
        new_meaning = []
        new_exam_sentence = exam_sentence or ''
        new_derivatives = derivatives or ''
        for line in lines:
            line = line.strip()
            if line.startswith('例'):
                content = re.sub(r'^例[\s　:：]*', '', line)
                if content:
                    if new_exam_sentence:
                        new_exam_sentence += '\n' + content
                    else:
                        new_exam_sentence = content
            elif line.startswith('参'):
                content = re.sub(r'^参[\s　:：]*', '', line)
                if content:
                    if new_derivatives:
                        new_derivatives += '；' + content
                    else:
                        new_derivatives = content
            elif re.match(r'^(n|v|adj|adv|prep|conj|art|pron|vt|vi|num|int|aux|link)\.', line):
                new_meaning.append(line)
            elif re.match(r'^（美', line):
                new_meaning.append(line)
            elif line:
                new_meaning.append(line)
        final_meaning = '；'.join(new_meaning).strip()
        if final_meaning != meaning_cn or new_exam_sentence != (exam_sentence or '') or new_derivatives != (derivatives or ''):
            cursor.execute('''
                UPDATE Words SET meaning_cn=?, exam_sentence=?, derivatives=? WHERE word_id=?
            ''', (final_meaning, new_exam_sentence, new_derivatives, word_id))
            update_count += 1
            print(f'修复: {spelling} (ID: {word_id})')
            print(f'  新释义: {final_meaning}')
            print(f'  新例句: {new_exam_sentence}')
            print(f'  新派生: {new_derivatives}')
    conn.commit()
    print(f'修复完成，共更新 {update_count} 个单词')
    conn.close()

if __name__ == '__main__':
    clean_meaning_fields() 