import sqlite3

def add_sample_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Добавим студентов
    students = [
        ('Иван', 'Иванов'),
        ('Петр', 'Петров'),
        ('Ирина', 'Ильина'),
        ('Сергей', 'Сидоров'),
        ('Анна', 'Исаева'),
    ]
    cursor.executemany('INSERT INTO Students (FirstName, LastName) VALUES (?, ?)', students)

    # Добавим курсы
    courses = [
        ('Математика',),
        ('Физика',),
        ('Информатика',)
    ]
    cursor.executemany('INSERT INTO Courses (CourseName) VALUES (?)', courses)

    # Добавим записи о зачислениях (Enrollments)
    # Для простоты, допустим, что StudentID и CourseID начинаются с 1 по порядку вставки
    enrollments = [
        (1, 1),  # Иван Иванов - Математика
        (1, 3),  # Иван Иванов - Информатика
        (2, 2),  # Петр Петров - Физика
        (3, 3),  # Ирина Ильина - Информатика
        (5, 1),  # Анна Исаева - Математика
        (4, 2)   # Сергей Сидоров - Физика
    ]
    cursor.executemany('INSERT INTO Enrollments (StudentID, CourseID) VALUES (?, ?)', enrollments)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_sample_data()
    print("Данные добавлены в базу.")
