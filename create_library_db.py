import sqlite3

def create_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Courses (
        CourseID INTEGER PRIMARY KEY AUTOINCREMENT,
        CourseName TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Enrollments (
        EnrollmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentID INTEGER,
        CourseID INTEGER,
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
        FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
    print("База данных и таблицы созданы.")
