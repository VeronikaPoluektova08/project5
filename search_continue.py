import sqlite3

DB_PATH = "chroma.sqlite3"

def show_first_rows():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, string_value FROM embedding_fulltext_search LIMIT 10")
    rows = cur.fetchall()
    conn.close()

    print("Первые 10 строк в базе:")
    for rid, txt in rows:
        print(f"[{rid}] {txt[:80]}{'...' if len(txt)>80 else ''}")
    print("-"*60)

def find_by_prefix(prefix):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT string_value
        FROM embedding_fulltext_search
        WHERE string_value LIKE ?
        ORDER BY id
        LIMIT 3
    """, (prefix + "%",))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

if __name__ == "_main_":
    show_first_rows()
    prefix = input("Введите начало строки точно как в таблице: ").strip()
    matches = find_by_prefix(prefix)
    if matches:
        print("\nНайдено:")
        for m in matches:
            tail = m[len(prefix):]
            print(f"Полная строка: {m}")
            print(f"Продолжение: {tail}\n")
    else:
        print("Ничего не найдено — проверь точность ввода.")