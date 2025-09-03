import sqlite3
from datetime import date

# Подключаемся к базе данных
conn = sqlite3.connect("online_library.db")
cursor = conn.cursor()

# Вставляем жанры
genres = [
     ("Приключения",),
    ("Романтика",),
    ("Драма",),
    ("Фантастика",),
    ("Ужасы",)
]
cursor.executemany("INSERT OR IGNORE INTO Genres (name) VALUES (?)", genres)

# Вставляем авторов
authors = [
    ("Жюль Верн", 1828),
    ("Джейн Остин", 1775),
    ("Агата Кристи", 1890),
    ("Эрнест Хемингуэй", 1899),
    ("Айзек Азимов", 1920)
]
cursor.executemany("INSERT OR IGNORE INTO Authors (full_name, birth_year) VALUES (?, ?)", authors)

# Вставляем книги
books = [
    ("20 000 лье под водой", 1870, 1, 1),   # Жюль Верн, Приключения
    ("Гордость и предубеждение", 1813, 2, 2),  # Джейн Остин, Романтика
    ("Убийство в «Восточном экспрессе»", 1934, 3, 3),  # Агата Кристи, Драма
    ("Старик и море", 1952, 4, 4),  # Эрнест Хемингуэй, Фантастика
    ("Основание", 1951, 5, 5)  # Айзек Азимов, Ужасы (для примера жанр условный)
]
cursor.executemany("""
INSERT OR IGNORE INTO Books (title, publish_year, author_id, genre_id)
VALUES (?, ?, ?, ?)
""", books)

# Вставляем пользователей
users = [
    ("Алексей Иванов", "alexey@example.com", "pass123", str(date.today())),
    ("Мария Петрова", "maria@example.com", "qwerty", str(date.today())),
    ("Дмитрий Смирнов", "dmitry@example.com", "secure456", str(date.today())),
    ("Анна Кузнецова", "anna@example.com", "mypassword", str(date.today()))
]
cursor.executemany("""
INSERT OR IGNORE INTO Users (name, email, password, registration_date)
VALUES (?, ?, ?, ?)
""", users)

# Вставляем отзывы
reviews = [
    (1, 1, 5, "Очень глубокая книга, заставляет задуматься.", str(date.today())),   # Алексей про "1984"
    (2, 2, 5, "Настоящая магия, одна из любимых книг детства!", str(date.today())), # Мария про "Гарри Поттер"
    (3, 3, 4, "Местами жутковато, но читается с интересом.", str(date.today())),   # Дмитрий про "Сияние"
    (4, 15, 5, "Эпическая история, мир Толкина поражает!", str(date.today())),      # Анна про "Властелин колец"
    (1, 5, 4, "Очень масштабное произведение, но тяжело читать.", str(date.today())) # Алексей про "Война и мир"
]
cursor.executemany("""
INSERT OR IGNORE INTO Reviews (user_id, book_id, rating, comment, review_date)
VALUES (?, ?, ?, ?, ?)
""", reviews)

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Данные о книгах, авторах, жанрах, пользователях и отзывах успешно добавлены.")