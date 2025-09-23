import sqlite3

# Создаем соединение с базой данных SQLite (или создаем файл базы данных, если его нет)
conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

# Загружаем SQL файлы для создания таблиц и вставки данных
with open('create_tables.sql', 'r') as f:
    cursor.executescript(f.read())

with open('insert_data.sql', 'r') as f:
    cursor.executescript(f.read())

# Запросы с оператором EXCEPT
# 1. Найти сотрудников, которые сейчас работают, но никогда не числились в списке уволенных
query_working_not_fired = """
SELECT EmployeeID, FullName, Department
FROM Employees
EXCEPT
SELECT EmployeeID, FullName, Department
FROM FormerEmployees;
"""

# 2. Найти сотрудников, которые уволились, но снова не были приняты в текущий штат
query_fired_not_working = """
SELECT EmployeeID, FullName, Department
FROM FormerEmployees
EXCEPT
SELECT EmployeeID, FullName, Department
FROM Employees;
"""

# Выполним запросы
cursor.execute(query_working_not_fired)
result_working_not_fired = cursor.fetchall()

cursor.execute(query_fired_not_working)
result_fired_not_working = cursor.fetchall()

# Выведем результаты
print("Сотрудники, которые сейчас работают, но никогда не числились в списке уволенных:")
for row in result_working_not_fired:
    print(row)

print("\nСотрудники, которые уволились, но снова не были приняты в текущий штат:")
for row in result_fired_not_working:
    print(row)

# Закрываем соединение
conn.close()
