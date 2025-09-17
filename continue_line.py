# continue_line.py
import sqlite3
from difflib import SequenceMatcher

print(">>> Скрипт запущен")

DB_PATH = "chroma.sqlite3"
TOP_N = 5  # сколько совпадений выводить

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Проверяем структуру таблицы и количество строк
cur.execute("PRAGMA table_info(embedding_fulltext_search)")
print("Структура таблицы:", cur.fetchall())
cur.execute("SELECT COUNT(*) FROM embedding_fulltext_search")
print("Всего строк в таблице:", cur.fetchone()[0])

while True:
    fragment = input("\nВведите начало строки (пусто — выход): ").strip()
    if not fragment:
        break

    cur.execute("""
        SELECT id, string_value
        FROM embedding_fulltext_search
        WHERE lower(string_value) LIKE lower(?)
    """, (f"%{fragment}%",))
    rows = cur.fetchall()

    if not rows:
        print("❌ Совпадений не найдено")
        continue

    # считаем похожесть и сортируем
    scored = [
        (similarity(fragment.lower(), text.lower()), row_id, text)
        for row_id, text in rows
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    print(f"\nНайдено {len(scored)} совпадений, показываю топ {TOP_N}:\n")
    for i, (score, row_id, text) in enumerate(scored[:TOP_N], start=1):
        pos = text.lower().find(fragment.lower())
        tail = text[pos + len(fragment):] if pos != -1 else ""
        print(f"{i}) id={row_id}, схожесть={score:.2f}")
        print(f"   Полный текст: {text}")
        if tail.strip():
            print(f"   ➡ Продолжение: {tail.strip()}")
        print()

    print("-" * 60)

conn.close()