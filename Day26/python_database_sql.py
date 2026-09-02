import sqlite3
from datetime import datetime


# ============================================================
# Configuration
# ============================================================

DATABASE_NAME = "company.db"


# ============================================================
# Database Connection
# ============================================================

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# ============================================================
# Database Initialization
# ============================================================

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            salary REAL NOT NULL CHECK(salary > 0),
            department_id INTEGER,
            hired_at TEXT NOT NULL,
            FOREIGN KEY (department_id)
                REFERENCES departments(id)
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            budget REAL NOT NULL CHECK(budget >= 0),
            start_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employee_projects (
            employee_id INTEGER,
            project_id INTEGER,
            role TEXT NOT NULL,
            PRIMARY KEY (employee_id, project_id),
            FOREIGN KEY (employee_id)
                REFERENCES employees(id)
                ON DELETE CASCADE,
            FOREIGN KEY (project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE
        );
    """)

    connection.commit()
    connection.close()


# ============================================================
# Seed Data
# ============================================================

def insert_sample_data():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        departments = [
            ("Software Engineering",),
            ("Data Science",),
            ("Cyber Security",),
            ("Human Resources",)
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO departments (name)
            VALUES (?)
        """, departments)

        projects = [
            ("E-Commerce Platform", 75000, "2026-01-15"),
            ("AI Recommendation System", 120000, "2026-03-01"),
            ("Security Monitoring System", 90000, "2026-04-10")
        ]

        for project in projects:
            cursor.execute("""
                INSERT OR IGNORE INTO projects
                (name, budget, start_date)
                VALUES (?, ?, ?)
            """, project)

        connection.commit()

        print("Sample departments and projects loaded.")

    except sqlite3.Error as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


# ============================================================
# Create Employee
# ============================================================

def add_employee():
    print("\n--- Add Employee ---")

    name = input("Name: ").strip()
    email = input("Email: ").strip()
    salary_input = input("Salary: ").strip()
    department_id_input = input("Department ID: ").strip()

    try:
        salary = float(salary_input)
        department_id = int(department_id_input)

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO employees
            (name, email, salary, department_id, hired_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            salary,
            department_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()

        print("Employee added successfully.")

    except ValueError:
        print("Please enter valid numbers.")

    except sqlite3.IntegrityError as error:
        print("Could not add employee:", error)

    finally:
        if "connection" in locals():
            connection.close()


# ============================================================
# List Departments
# ============================================================

def list_departments():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM departments
        ORDER BY id
    """)

    departments = cursor.fetchall()

    print("\n--- Departments ---")

    for department in departments:
        print(f"{department['id']}. {department['name']}")

    connection.close()


# ============================================================
# List Employees
# ============================================================

def list_employees():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            e.id,
            e.name,
            e.email,
            e.salary,
            d.name AS department,
            e.hired_at
        FROM employees e
        LEFT JOIN departments d
            ON e.department_id = d.id
        ORDER BY e.id
    """)

    employees = cursor.fetchall()

    print("\n--- Employees ---")

    if not employees:
        print("No employees found.")

    for employee in employees:
        print(
            f"\nID: {employee['id']}\n"
            f"Name: {employee['name']}\n"
            f"Email: {employee['email']}\n"
            f"Salary: ${employee['salary']:,.2f}\n"
            f"Department: {employee['department']}\n"
            f"Hired: {employee['hired_at']}"
        )

    connection.close()


# ============================================================
# Search Employees
# ============================================================

def search_employees():
    search_term = input("\nSearch employee: ").strip()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            e.id,
            e.name,
            e.email,
            e.salary,
            d.name AS department
        FROM employees e
        LEFT JOIN departments d
            ON e.department_id = d.id
        WHERE e.name LIKE ?
           OR e.email LIKE ?
           OR d.name LIKE ?
        ORDER BY e.name
    """, (
        f"%{search_term}%",
        f"%{search_term}%",
        f"%{search_term}%"
    ))

    employees = cursor.fetchall()

    print("\n--- Search Results ---")

    for employee in employees:
        print(
            f"{employee['id']} | "
            f"{employee['name']} | "
            f"{employee['email']} | "
            f"${employee['salary']:,.2f} | "
            f"{employee['department']}"
        )

    if not employees:
        print("No matching employees.")

    connection.close()


# ============================================================
# Update Employee Salary
# ============================================================

def update_salary():
    print("\n--- Update Salary ---")

    employee_id = input("Employee ID: ").strip()
    new_salary = input("New salary: ").strip()

    try:
        employee_id = int(employee_id)
        new_salary = float(new_salary)

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE employees
            SET salary = ?
            WHERE id = ?
        """, (new_salary, employee_id))

        if cursor.rowcount == 0:
            print("Employee not found.")
        else:
            connection.commit()
            print("Salary updated successfully.")

    except ValueError:
        print("Invalid input.")

    except sqlite3.Error as error:
        print("Database error:", error)

    finally:
        if "connection" in locals():
            connection.close()


# ============================================================
# Delete Employee
# ============================================================

def delete_employee():
    print("\n--- Delete Employee ---")

    employee_id = input("Employee ID: ").strip()

    try:
        employee_id = int(employee_id)

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM employees
            WHERE id = ?
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            print("Employee not found.")
            return

        confirmation = input(
            f"Delete {employee['name']}? (y/n): "
        ).lower()

        if confirmation == "y":
            cursor.execute("""
                DELETE FROM employees
                WHERE id = ?
            """, (employee_id,))

            connection.commit()

            print("Employee deleted.")

        else:
            print("Deletion cancelled.")

    except ValueError:
        print("Invalid employee ID.")

    finally:
        if "connection" in locals():
            connection.close()


# ============================================================
# Add Employee To Project
# ============================================================

def assign_project():
    print("\n--- Assign Employee To Project ---")

    employee_id = input("Employee ID: ").strip()
    project_id = input("Project ID: ").strip()
    role = input("Role: ").strip()

    try:
        employee_id = int(employee_id)
        project_id = int(project_id)

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO employee_projects
            (employee_id, project_id, role)
            VALUES (?, ?, ?)
        """, (employee_id, project_id, role))

        connection.commit()

        print("Employee assigned to project.")

    except ValueError:
        print("IDs must be numbers.")

    except sqlite3.IntegrityError as error:
        print("Could not assign project:", error)

    finally:
        if "connection" in locals():
            connection.close()


# ============================================================
# Show Employee Projects
# ============================================================

def show_projects():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            e.name AS employee,
            p.name AS project,
            ep.role,
            p.budget
        FROM employee_projects ep
        JOIN employees e
            ON ep.employee_id = e.id
        JOIN projects p
            ON ep.project_id = p.id
        ORDER BY e.name
    """)

    results = cursor.fetchall()

    print("\n--- Employee Projects ---")

    if not results:
        print("No project assignments found.")

    for row in results:
        print(
            f"{row['employee']} | "
            f"{row['project']} | "
            f"Role: {row['role']} | "
            f"Budget: ${row['budget']:,.2f}"
        )

    connection.close()


# ============================================================
# Salary Statistics
# ============================================================

def salary_statistics():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS employee_count,
            ROUND(AVG(salary), 2) AS average_salary,
            ROUND(MIN(salary), 2) AS lowest_salary,
            ROUND(MAX(salary), 2) AS highest_salary,
            ROUND(SUM(salary), 2) AS total_salary
        FROM employees
    """)

    stats = cursor.fetchone()

    print("\n--- Salary Statistics ---")
    print(f"Employees: {stats['employee_count']}")
    print(f"Average salary: ${stats['average_salary'] or 0:,.2f}")
    print(f"Lowest salary: ${stats['lowest_salary'] or 0:,.2f}")
    print(f"Highest salary: ${stats['highest_salary'] or 0:,.2f}")
    print(f"Total salaries: ${stats['total_salary'] or 0:,.2f}")

    connection.close()


# ============================================================
# Department Statistics
# ============================================================

def department_statistics():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            d.name AS department,
            COUNT(e.id) AS employees,
            ROUND(AVG(e.salary), 2) AS average_salary,
            ROUND(SUM(e.salary), 2) AS payroll
        FROM departments d
        LEFT JOIN employees e
            ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY payroll DESC
    """)

    results = cursor.fetchall()

    print("\n--- Department Statistics ---")

    for row in results:
        print(
            f"\nDepartment: {row['department']}\n"
            f"Employees: {row['employees']}\n"
            f"Average Salary: ${row['average_salary'] or 0:,.2f}\n"
            f"Payroll: ${row['payroll'] or 0:,.2f}"
        )

    connection.close()


# ============================================================
# Main Menu
# ============================================================

def display_menu():
    print("""
============================================================
              PYTHON + SQL DATABASE MANAGER
============================================================

1. Add Employee
2. List Employees
3. Search Employees
4. Update Employee Salary
5. Delete Employee
6. List Departments
7. Assign Employee To Project
8. Show Employee Projects
9. Salary Statistics
10. Department Statistics
0. Exit

============================================================
""")


def main():
    initialize_database()
    insert_sample_data()

    while True:
        display_menu()

        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_departments()
            add_employee()

        elif choice == "2":
            list_employees()

        elif choice == "3":
            search_employees()

        elif choice == "4":
            update_salary()

        elif choice == "5":
            delete_employee()

        elif choice == "6":
            list_departments()

        elif choice == "7":
            assign_project()

        elif choice == "8":
            show_projects()

        elif choice == "9":
            salary_statistics()

        elif choice == "10":
            department_statistics()

        elif choice == "0":
            print("\nGoodbye!")
            break

        else:
            print("Invalid option. Please try again.")


# ============================================================
# Program Entry Point
# ============================================================

if __name__ == "__main__":
    main()
