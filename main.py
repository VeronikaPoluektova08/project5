import sqlite3
import pandas as pd

# Создаем базу в памяти
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Создаем таблицу сотрудников
cursor.execute("""
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    DepartmentID INTEGER
)
""")

# Создаем таблицу отделов
cursor.execute("""
CREATE TABLE Departments (
    DepartmentID INTEGER PRIMARY KEY,
    DepartmentName TEXT,
    ManagerID INTEGER
)
""")

# Добавляем данные
cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?)", [
    (1, "Иван", "Иванов", 10),
    (2, "Петр", "Петров", 20),
    (3, "Сергей", "Сидоров", None),   # сотрудник без отдела
])

cursor.executemany("INSERT INTO Departments VALUES (?, ?, ?)", [
    (10, "Отдел продаж", 101),
    (20, "Бухгалтерия", 102)
])

# SQL-запрос с INNER JOIN
query = """
SELECT e.EmployeeID, e.FirstName, e.LastName, d.DepartmentName
FROM Employees e
INNER JOIN Departments d ON e.DepartmentID = d.DepartmentID
"""

# Загружаем в pandas DataFrame
df = pd.read_sql_query(query, conn)

# Закрываем соединение
conn.close()

# Вывод таблицы
print(df.to_string(index=False))