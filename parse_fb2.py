from lxml import etree
import pandas as pd

# --- путь к файлу ---
fb2_path = "khrustalnaia_tufelka.fb2"

# --- парсинг FB2 ---
tree = etree.parse(fb2_path)
# Все абзацы в FB2 обычно лежат в тегах <p>
paragraphs = [p.text.strip() for p in tree.xpath("//p") if p.text and p.text.strip()]

# --- создаём DataFrame ---
df = pd.DataFrame({
    "id": range(1, len(paragraphs)+1),
    "string_value": paragraphs
})

# Сохраняем в SQLite (если надо)
import sqlite3
conn = sqlite3.connect("chroma_storage/chroma.sqlite3")
df.to_sql("embedding_fulltext_search", conn, if_exists="append", index=False)

# Или просто выводим первые строки
print(df.head())