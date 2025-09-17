import sqlite3

DB_PATH = "chroma.sqlite3"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Посмотрим, есть ли вообще таблица
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Таблицы в базе:", cur.fetchall())

print("\nПервые 20 строк таблицы embedding_fulltext_search:\n")
try:
    cur.execute("SELECT id, string_value FROM embedding_fulltext_search LIMIT 20")
    for row in cur.fetchall():
        print(f"[{row[0]}] {row[1]}")
except Exception as e:
    print("Ошибка при чтении:", e)

conn.close()