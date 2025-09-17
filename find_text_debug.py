# find_text_debug.py
import sqlite3
import re
import unicodedata
from pathlib import Path

DB_PATH = Path("chroma.sqlite3")

def normalize_spaces(s: str) -> str:
    # нормализуем юникод, заменим NBSP на обычный пробел и схлопнём подряд идущие пробелы/переносы
    if s is None:
        return ""
    s = s.replace("\u00A0", " ")
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def make_flexible_pattern(inp: str) -> str:
    # разбиваем на токены и собираем паттерн, где между токенами может быть любой пробел-последовательность
    tokens = [t for t in re.split(r"\s+", inp.strip()) if t]
    if not tokens:
        return None
    esc = [re.escape(t) for t in tokens]
    return r"\s+".join(esc)

def load_all_rows(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT id, string_value FROM embedding_fulltext_search ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def try_search(rows, user_input):
    # подготовка
    user_input_raw = user_input
    user_input = user_input.replace("\u00A0", " ").strip()
    pattern_tokens = make_flexible_pattern(user_input)
    if not pattern_tokens:
        return None, "Пустой ввод"

    # сначала попробуем найти фрагмент *в начале строки* (как ты просил — начало → продолжение)
    start_pattern = r"^\s*" + pattern_tokens
    start_re = re.compile(start_pattern, flags=re.IGNORECASE)

    for rid, txt in rows:
        txt_for_search = txt.replace("\u00A0", " ")
        m = start_re.search(txt_for_search)
        if m:
            tail = txt[m.end():]
            return (rid, txt, tail, "match_start"), None

    # если не найдено, попробуем найти фрагмент в любом месте строки (гибко по пробелам)
    any_pattern = pattern_tokens
    any_re = re.compile(any_pattern, flags=re.IGNORECASE)
    for rid, txt in rows:
        txt_for_search = txt.replace("\u00A0", " ")
        m = any_re.search(txt_for_search)
        if m:
            tail = txt[m.end():]
            return (rid, txt, tail, "match_any"), None

    # как запасной вариант — попробуем по нормализованным строкам (слово в слове, после схлопывания пробелов)
    norm_user = normalize_spaces(user_input)
    for rid, txt in rows:
        norm_txt = normalize_spaces(txt)
        pos = norm_txt.lower().find(norm_user.lower())
        if pos != -1:
            # Найдём соответствующий участок в оригинальной строке — попробуем искать первый токен последовательности
            tokens = [t for t in re.split(r"\s+", norm_user) if t]
            if tokens:
                # ищем первый токен в оригинале, затем ищем последовательность токенов
                first_tok = re.escape(tokens[0])
                seq_pattern = r"(?i)" + r"\s+".join(re.escape(t) for t in tokens)
                seq_re = re.compile(seq_pattern)
                m = seq_re.search(txt.replace("\u00A0", " "))
                if m:
                    tail = txt[m.end():]
                    return (rid, txt, tail, "match_norm"), None
            # если не получилось, просто вернём строку целиком
            return (rid, txt, "", "match_norm_no_pos"), None

    return None, "Совпадений не найдено"

if __name__ == "_main_":
    if not DB_PATH.exists():
        print(f"Файл базы не найден: {DB_PATH.resolve()}")
        raise SystemExit(1)

    # покажем небольшой сэмпл для отладки
    rows = load_all_rows(DB_PATH)
    print(f"Всего строк в таблице: {len(rows)}\n")
    print("Первые 10 строк (id + начало):")
    for rid, txt in rows[:10]:
        print(f"[{rid}] {txt[:120]}{'...' if len(txt)>120 else ''}")
    print("-" * 60)

    user_input = input("Введи начало строки (или любой фрагмент): ").rstrip("\n")
    if not user_input.strip():
        print("Ввод пустой — выход.")
        raise SystemExit(0)

    found, err = try_search(rows, user_input)
    if err:
        print("Ошибка/ничего не найдено:", err)
        print("Подсказка: скопируй начало нужной строки прямо из списка выше (включая пунктуацию) и вставь его.")
    else:
        rid, full_line, tail, how = found
        print(f"\nНайдено (id={rid}), способ: {how}")
        print("Полная строка:\n", full_line)
        print("\nПродолжение (то, что идёт после введённого фрагмента):\n", tail if tail else "(пустое — совпадение в конце строки или не удалось точно определить хвост)")