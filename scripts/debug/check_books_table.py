#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_books_table():
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # 检查Books表的结构
    cursor.execute("PRAGMA table_info(Books)")
    columns = cursor.fetchall()
    print("Books表的列:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 检查Books表的内容
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    print("\nBooks表的内容:")
    for book in books:
        print(f"  {book}")
    
    # 检查WordLists表的结构
    cursor.execute("PRAGMA table_info(WordLists)")
    columns = cursor.fetchall()
    print("\nWordLists表的列:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 检查WordLists表的内容
    cursor.execute("SELECT * FROM WordLists LIMIT 5")
    wordlists = cursor.fetchall()
    print("\nWordLists表的内容:")
    for wl in wordlists:
        print(f"  {wl}")
    
    conn.close()

if __name__ == "__main__":
    check_books_table() 