import sqlite3

DB_PATH = "chroma.sqlite3"

def find_continuation(fragment: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, string_value
        FROM embedding_fulltext_search
        WHERE lower(string_value) LIKE lower(?)
        ORDER BY id
        LIMIT 1
    """, (f"%{fragment}%",))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    full_line = row[1]
    pos = full_line.lower().find(fragment.lower())
    if pos != -1:
        return full_line[pos + len(fragment):], full_line
    return "", full_line

if __name__ == "_main_":
    text = input("Введите кусок строки (любое место): ").strip()
    result = find_continuation(text)
    if result is None:
        print("Совпадений не найдено.")
    else:
        tail, full = result
        print("\nНайдена строка:\n", full)
        print("\nПродолжение после введённого текста:\n", tail)