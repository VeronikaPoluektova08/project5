-- Вставка данных в таблицу Employees (сотрудники, которые сейчас работают)
INSERT INTO Employees (EmployeeID, FullName, Department) VALUES (1, 'Ivan Ivanov', 'HR');
INSERT INTO Employees (EmployeeID, FullName, Department) VALUES (2, 'Petr Petrov', 'IT');
INSERT INTO Employees (EmployeeID, FullName, Department) VALUES (3, 'Anna Sidorova', 'Finance');
INSERT INTO Employees (EmployeeID, FullName, Department) VALUES (4, 'John Doe', 'Marketing');

-- Вставка данных в таблицу FormerEmployees (сотрудники, которые когда-то работали, но уволились)
INSERT INTO FormerEmployees (EmployeeID, FullName, Department) VALUES (2, 'Petr Petrov', 'IT');
INSERT INTO FormerEmployees (EmployeeID, FullName, Department) VALUES (3, 'Anna Sidorova', 'Finance');
INSERT INTO FormerEmployees (EmployeeID, FullName, Department) VALUES (5, 'Maria Ivanova', 'HR');
