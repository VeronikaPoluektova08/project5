from lxml import etree

# Открываем и парсим файл .fb2
with open('book.fb2', 'rb') as fb2_file:
    tree = etree.parse(fb2_file)
    
# Извлекаем все текстовые элементы из файла
text_elements = tree.xpath('//body//p/text()')  # Все параграфы текста

# Преобразуем список текстовых элементов в один длинный текст
book_text = "\n".join(text_elements)

# Разбиваем текст на абзацы (обычно они разделяются двумя переносами строк)
paragraphs = book_text.split("\n\n")

# Пример вывода первых 3 абзацев
for i, paragraph in enumerate(paragraphs[:3]):
    print(f"Абзац {i + 1}:\n{paragraph}\n{'-' * 40}")
