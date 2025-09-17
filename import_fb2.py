from pathlib import Path
import sqlite3
from lxml import etree

# === Пути к файлам ===
# Если rip.fb2 в той же папке, где скрипт:
fb2_file = Path("rip.fb2")
db_path = Path("chroma.sqlite3")

# === Проверяем наличие книги ===
if not fb2_file.exists():
    raise FileNotFoundError(f"FB2 файл не найден: {fb2_file.resolve()}")

# === Парсим FB2 с учётом namespace ===
tree = etree.parse(str(fb2_file))

# Пространство имён FictionBook 2.0
NS = {"fb": "http://www.gribuser.ru/xml/fictionbook/2.0"}

# Ищем все <p> внутри <body>
paragraphs = tree.xpath("//fb:body//fb:p", namespaces=NS)
print(f"Найдено {len(paragraphs)} тегов <p> в <body>")

# Извлекаем полный текст каждого <p>
texts = []
for elem in paragraphs:
    txt = "".join(elem.itertext()).strip()
    if txt:
        texts.append(txt)

print(f"После очистки осталось {len(texts)} непустых абзацев")

# === Записываем в базу данных ===
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Создаём таблицу, если её нет
cur.execute("""
CREATE TABLE IF NOT EXISTS embedding_fulltext_search (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    string_value TEXT
)
""")

insert_query = "INSERT INTO embedding_fulltext_search (string_value) VALUES (?)"
for t in texts:
    cur.execute(insert_query, (t,))

conn.commit()
conn.close()

print(f"В базу добавлено {len(texts)} записей")