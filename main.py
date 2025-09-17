import chromadb
import os
from dotenv import load_dotenv
from chromadb.utils import embedding_functions

# --- 1. Загрузка API-ключа ---
load_dotenv()  # Загружаем переменные из файла .env
API_KEY = os.getenv('GOOGLE_API_KEY')

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY не найден. Убедитесь, что он есть в файле .env")

# --- 2. Настройка ChromaDB с эмбеддингами (без использования Google Gemini) ---
client = chromadb.Client()

# Используем встроенную эмбеддинг-функцию Chroma для создания эмбеддингов
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction()

# Создаем коллекцию
try:
    collection = client.create_collection(
        name="student_test_collection",  # Название коллекции
        embedding_function=embedding_function  # Используем стандартную эмбеддинг-функцию
    )
    print("Коллекция успешно создана.")
except chromadb.errors.UniqueConstraintError:
    # Если коллекция уже существует, удаляем её и создаем новую
    client.delete_collection(name="student_test_collection")
    collection = client.create_collection(
        name="student_test_collection",
        embedding_function=embedding_function
    )
    print("Старая коллекция удалена, создана новая.")

# --- 3. Добавление данных (Индексация) ---
print("Добавление документов в ChromaDB...")

collection.add(
    documents=[
        "Python - это высокоуровневый язык программирования, известный своей простотой.",
        "SQL (Structured Query Language) используется для управления реляционными базами данных.",
        "Велосипед - это транспортное средство, приводимое в движение мускульной силой человека.",
        "Самое высокое здание в мире - Бурдж-Халифа."
    ],
    metadatas=[
        {"source": "wiki", "topic": "programming"},
        {"source": "textbook", "topic": "database"},
        {"source": "dictionary", "topic": "transport"},
        {"source": "web", "topic": "architecture"}
    ],
    ids=["doc1", "doc2", "doc3", "doc4"]  # Уникальные ID для каждого документа
)

print(f"Документы добавлены. Всего в коллекции: {collection.count()} элементов.")

# --- 4. Тестирование запроса (Поиск) ---
print("\n--- ТЕСТИРОВАНИЕ ЗАПРОСА ---")

query_text = "Что такое язык для работы с БД?"

results = collection.query(
    query_texts=[query_text],
    n_results=2  # Попросим 2 самых релевантных результата
)

# Выводим результаты запроса
print(f"Результаты по запросу: '{query_text}'")
print(results)

# Выводим наиболее релевантный документ
print("\nСамый релевантный документ:")
print(f"Текст: {results['documents'][0][0]}")
print(f"Источник: {results['metadatas'][0][0]['source']}")
