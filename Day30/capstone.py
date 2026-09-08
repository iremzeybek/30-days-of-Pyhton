```python
"""
=============================================================
DAY 30 - PYTHON PRODUCTIVITY & ANALYTICS HUB
=============================================================

30 Days of Python - Final Capstone Project

Features:
    - Object-Oriented Programming
    - SQLite database
    - JSON persistence
    - CSV export
    - Pandas analytics
    - Matplotlib visualization
    - Regular expressions
    - Password hashing
    - FastAPI REST API
    - Async programming
    - HTTP requests
    - Logging
    - CLI interface
    - Statistics
    - Search and filtering
    - Automated reports
    - Error handling

Author: Irem Zeybek
Version: 1.0.0
=============================================================
"""

import asyncio
import csv
import hashlib
import json
import logging
import os
import re
import sqlite3
import statistics
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# =============================================================
# CONFIGURATION
# =============================================================

APP_NAME = "Python Productivity & Analytics Hub"
VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "productivity.db"
JSON_FILE = BASE_DIR / "tasks.json"
CSV_FILE = BASE_DIR / "tasks.csv"
REPORT_FILE = BASE_DIR / "productivity_report.txt"
CHART_FILE = BASE_DIR / "productivity_chart.png"
LOG_FILE = BASE_DIR / "productivity.log"

API_HOST = "127.0.0.1"
API_PORT = 8000


# =============================================================
# LOGGING
# =============================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(APP_NAME)


# =============================================================
# DATA MODEL
# =============================================================

@dataclass
class Task:
    id: Optional[int]
    title: str
    category: str
    priority: str
    completed: bool
    hours: float
    created_at: str
    email: str = ""


# =============================================================
# SECURITY
# =============================================================

class SecurityManager:
    """Handles simple password hashing."""

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return SecurityManager.hash_password(password) == password_hash


# =============================================================
# VALIDATION
# =============================================================

class Validator:
    """Validation utilities using regular expressions."""

    EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    @staticmethod
    def valid_email(email: str) -> bool:
        return re.match(
            Validator.EMAIL_PATTERN,
            email
        ) is not None

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def valid_priority(priority: str) -> bool:
        return priority.lower() in {
            "low",
            "medium",
            "high"
        }


# =============================================================
# DATABASE MANAGER
# =============================================================

class DatabaseManager:

    def __init__(self, database_file: Path):
        self.database_file = database_file
        self.initialize_database()

    def connect(self):
        return sqlite3.connect(self.database_file)

    def initialize_database(self):
        with self.connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    completed INTEGER NOT NULL,
                    hours REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    email TEXT
                )
            """)

            connection.commit()

        logger.info("Database initialized.")

    def add_task(self, task: Task) -> int:
        with self.connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO tasks
                (
                    title,
                    category,
                    priority,
                    completed,
                    hours,
                    created_at,
                    email
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task.title,
                task.category,
                task.priority,
                int(task.completed),
                task.hours,
                task.created_at,
                task.email
            ))

            connection.commit()

            task_id = cursor.lastrowid

        logger.info("Task added: %s", task.title)

        return task_id

    def get_tasks(self) -> List[Task]:
        with self.connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    id,
                    title,
                    category,
                    priority,
                    completed,
                    hours,
                    created_at,
                    email
                FROM tasks
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

        return [
            Task(
                id=row[0],
                title=row[1],
                category=row[2],
                priority=row[3],
                completed=bool(row[4]),
                hours=row[5],
                created_at=row[6],
                email=row[7] or ""
            )
            for row in rows
        ]

    def get_task(self, task_id: int) -> Optional[Task]:
        with self.connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    id,
                    title,
                    category,
                    priority,
                    completed,
                    hours,
                    created_at,
                    email
                FROM tasks
                WHERE id = ?
            """, (task_id,))

            row = cursor.fetchone()

        if not row:
            return None

        return Task(
            id=row[0],
            title=row[1],
            category=row[2],
            priority=row[3],
            completed=bool(row[4]),
            hours=row[5],
            created_at=row[6],
            email=row[7] or ""
        )

    def complete_task(self, task_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE tasks
                SET completed = 1
                WHERE id = ?
            """, (task_id,))

            connection.commit()

            changed = cursor.rowcount > 0

        if changed:
            logger.info("Task completed: %s", task_id)

        return changed

    def delete_task(self, task_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                DELETE FROM tasks
                WHERE id = ?
            """, (task_id,))

            connection.commit()

            deleted = cursor.rowcount > 0

        if deleted:
            logger.info("Task deleted: %s", task_id)

        return deleted

    def clear_database(self):
        with self.connect() as connection:
            connection.execute("DELETE FROM tasks")
            connection.commit()

        logger.warning("All tasks deleted.")


# =============================================================
# SAMPLE DATA
# =============================================================

class SampleData:

    @staticmethod
    def create(database: DatabaseManager):

        existing_tasks = database.get_tasks()

        if existing_tasks:
            return

        samples = [
            Task(
                None,
                "Learn Python Decorators",
                "Python",
                "High",
                True,
                2.5,
                datetime.now().isoformat(),
                "student@example.com"
            ),
            Task(
                None,
                "Build REST API",
                "Backend",
                "High",
                True,
                3.0,
                datetime.now().isoformat(),
                "student@example.com"
            ),
            Task(
                None,
                "Practice Pandas",
                "Data Science",
                "Medium",
                False,
                2.0,
                datetime.now().isoformat(),
                "student@example.com"
            ),
            Task(
                None,
                "Study Regular Expressions",
                "Python",
                "Medium",
                True,
                1.5,
                datetime.now().isoformat(),
                "student@example.com"
            ),
            Task(
                None,
                "Create GitHub README",
                "GitHub",
                "Low",
                False,
                1.0,
                datetime.now().isoformat(),
                "student@example.com"
            ),
            Task(
                None,
                "Build Final Python Project",
                "Portfolio",
                "High",
                False,
                4.0,
                datetime.now().isoformat(),
                "student@example.com"
            )
        ]

        for task in samples:
            database.add_task(task)

        logger.info("Sample data created.")


# =============================================================
# ANALYTICS ENGINE
# =============================================================

class AnalyticsEngine:

    def __init__(self, database: DatabaseManager):
        self.database = database

    def dataframe(self) -> pd.DataFrame:

        tasks = self.database.get_tasks()

        if not tasks:
            return pd.DataFrame(
                columns=[
                    "id",
                    "title",
                    "category",
                    "priority",
                    "completed",
                    "hours",
                    "created_at",
                    "email"
                ]
            )

        data = [asdict(task) for task in tasks]

        df = pd.DataFrame(data)

        return df

    def total_tasks(self) -> int:
        return len(self.database.get_tasks())

    def completed_tasks(self) -> int:
        return sum(
            task.completed
            for task in self.database.get_tasks()
        )

    def pending_tasks(self) -> int:
        return self.total_tasks() - self.completed_tasks()

    def total_hours(self) -> float:
        return sum(
            task.hours
            for task in self.database.get_tasks()
        )

    def completed_hours(self) -> float:
        return sum(
            task.hours
            for task in self.database.get_tasks()
            if task.completed
        )

    def completion_rate(self) -> float:

        total = self.total_tasks()

        if total == 0:
            return 0.0

        return (
            self.completed_tasks()
            / total
        ) * 100

    def average_hours(self) -> float:

        tasks = self.database.get_tasks()

        if not tasks:
            return 0.0

        return statistics.mean(
            task.hours
            for task in tasks
        )

    def category_statistics(self):

        df = self.dataframe()

        if df.empty:
            return pd.DataFrame()

        return (
            df.groupby("category")
            .agg(
                tasks=("id", "count"),
                hours=("hours", "sum"),
                completed=("completed", "sum")
            )
            .sort_values(
                "hours",
                ascending=False
            )
        )

    def priority_statistics(self):

        df = self.dataframe()

        if df.empty:
            return pd.DataFrame()

        return (
            df.groupby("priority")
            .agg(
                tasks=("id", "count"),
                hours=("hours", "sum")
            )
            .sort_values(
                "hours",
                ascending=False
            )
        )

    def most_productive_category(self) -> str:

        stats = self.category_statistics()

        if stats.empty:
            return "N/A"

        return str(stats["hours"].idxmax())

    def generate_report(self):

        total = self.total_tasks()
        completed = self.completed_tasks()
        pending = self.pending_tasks()
        hours = self.total_hours()
        completed_hours = self.completed_hours()
        rate = self.completion_rate()
        average = self.average_hours()
        productive_category = self.most_productive_category()

        report = f"""
============================================================
PYTHON PRODUCTIVITY & ANALYTICS HUB
PRODUCTIVITY REPORT
============================================================

Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SUMMARY
------------------------------------------------------------
Total Tasks       : {total}
Completed Tasks   : {completed}
Pending Tasks     : {pending}

Total Hours       : {hours:.2f}
Completed Hours   : {completed_hours:.2f}
Average Task Time : {average:.2f} hours

Completion Rate   : {rate:.2f}%

Most Productive
Category          : {productive_category}

============================================================
CATEGORY STATISTICS
============================================================

{self.category_statistics().to_string()}

============================================================
PRIORITY STATISTICS
============================================================

{self.priority_statistics().to_string()}

============================================================
END OF REPORT
============================================================
"""

        REPORT_FILE.write_text(
            report,
            encoding="utf-8"
        )

        logger.info("Report generated.")

        return report

    def generate_chart(self):

        df = self.dataframe()

        if df.empty:
            print("No data available for chart.")
            return

        category_hours = (
            df.groupby("category")["hours"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        plt.figure(figsize=(10, 6))

        category_hours.plot(
            kind="bar"
        )

        plt.title(
            "Study Hours by Category"
        )

        plt.xlabel("Category")
        plt.ylabel("Hours")

        plt.xticks(rotation=30)

        plt.tight_layout()

        plt.savefig(
            CHART_FILE,
            dpi=150
        )

        plt.close()

        logger.info("Chart generated.")

        print(
            f"\nChart saved to: {CHART_FILE}"
        )


# =============================================================
# EXPORT MANAGER
# =============================================================

class ExportManager:

    def __init__(self, database: DatabaseManager):
        self.database = database

    def export_json(self):

        tasks = self.database.get_tasks()

        data = [
            asdict(task)
            for task in tasks
        ]

        with open(
            JSON_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        logger.info("JSON exported.")

        print(
            f"\nJSON exported to: {JSON_FILE}"
        )

    def export_csv(self):

        tasks = self.database.get_tasks()

        with open(
            CSV_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "id",
                    "title",
                    "category",
                    "priority",
                    "completed",
                    "hours",
                    "created_at",
                    "email"
                ]
            )

            writer.writeheader()

            for task in tasks:
                writer.writerow(
                    asdict(task)
                )

        logger.info("CSV exported.")

        print(
            f"\nCSV exported to: {CSV_FILE}"
        )


# =============================================================
# ASYNC INTERNET SERVICE
# =============================================================

class AsyncInternetService:

    @staticmethod
    async def check_internet():

        loop = asyncio.get_running_loop()

        try:
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    "https://api.github.com",
                    timeout=5
                )
            )

            return {
                "online": True,
                "status_code": response.status_code
            }

        except requests.RequestException:

            return {
                "online": False,
                "status_code": None
            }

    @staticmethod
    async def get_github_api_info():

        loop = asyncio.get_running_loop()

        try:

            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    "https://api.github.com",
                    timeout=5
                )
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            return {
                "error": str(error)
            }


# =============================================================
# FASTAPI
# =============================================================

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="30 Days of Python final capstone API."
)


class TaskRequest(BaseModel):
    title: str
    category: str
    priority: str
    hours: float
    email: str = ""


database = DatabaseManager(DATABASE_FILE)
analytics = AnalyticsEngine(database)


@app.get("/")
def home():

    return {
        "application": APP_NAME,
        "version": VERSION,
        "message": "Python Productivity Hub API is running!",
        "endpoints": [
            "/tasks",
            "/statistics",
            "/health"
        ]
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/tasks")
def get_tasks():

    tasks = database.get_tasks()

    return [
        asdict(task)
        for task in tasks
    ]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    task = database.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found."
        )

    return asdict(task)


@app.post("/tasks")
def create_task(request: TaskRequest):

    title = Validator.clean_text(
        request.title
    )

    category = Validator.clean_text(
        request.category
    )

    priority = request.priority.lower()

    if not Validator.valid_priority(priority):
        raise HTTPException(
            status_code=400,
            detail="Priority must be low, medium, or high."
        )

    if request.hours < 0:
        raise HTTPException(
            status_code=400,
            detail="Hours cannot be negative."
        )

    if request.email and not Validator.valid_email(
        request.email
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid email address."
        )

    task = Task(
        id=None,
        title=title,
        category=category,
        priority=priority,
        completed=False,
        hours=request.hours,
        created_at=datetime.now().isoformat(),
        email=request.email
    )

    task_id = database.add_task(task)

    return {
        "message": "Task created successfully.",
        "task_id": task_id
    }


@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):

    if not database.complete_task(task_id):

        raise HTTPException(
            status_code=404,
            detail="Task not found."
        )

    return {
        "message": "Task marked as completed."
    }


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    if not database.delete_task(task_id):

        raise HTTPException(
            status_code=404,
            detail="Task not found."
        )

    return {
        "message": "Task deleted successfully."
    }


@app.get("/statistics")
def statistics_endpoint():

    return {
        "total_tasks": analytics.total_tasks(),
        "completed_tasks": analytics.completed_tasks(),
        "pending_tasks": analytics.pending_tasks(),
        "total_hours": analytics.total_hours(),
        "completed_hours": analytics.completed_hours(),
        "completion_rate": analytics.completion_rate(),
        "average_hours": analytics.average_hours(),
        "most_productive_category":
            analytics.most_productive_category()
    }


# =============================================================
# CLI DISPLAY
# =============================================================

def print_header():

    print("\n")
    print("=" * 65)
    print(f"  {APP_NAME}")
    print(f"  Version {VERSION}")
    print("=" * 65)


def print_task(task: Task):

    status = (
        "✓ COMPLETED"
        if task.completed
        else "○ PENDING"
    )

    print(
        f"""
ID       : {task.id}
Title    : {task.title}
Category : {task.category}
Priority : {task.priority}
Status   : {status}
Hours    : {task.hours:.2f}
Email    : {task.email or "None"}
Created  : {task.created_at}
"""
    )

    print("-" * 65)


def list_tasks():

    tasks = database.get_tasks()

    if not tasks:

        print("\nNo tasks found.")
        return

    print(
        f"\nFound {len(tasks)} tasks:\n"
    )

    for task in tasks:
        print_task(task)


# =============================================================
# ADD TASK
# =============================================================

def add_task_cli():

    print("\n--- ADD NEW TASK ---")

    title = input(
        "Task title: "
    ).strip()

    if not title:

        print("Title cannot be empty.")
        return

    category = input(
        "Category: "
    ).strip()

    if not category:

        category = "General"

    priority = input(
        "Priority (low/medium/high): "
    ).strip().lower()

    if not Validator.valid_priority(
        priority
    ):

        print(
            "Invalid priority."
        )

        return

    try:

        hours = float(
            input(
                "Estimated hours: "
            )
        )

        if hours < 0:
            raise ValueError

    except ValueError:

        print(
            "Hours must be a positive number."
        )

        return

    email = input(
        "Email (optional): "
    ).strip()

    if email and not Validator.valid_email(
        email
    ):

        print(
            "Invalid email format."
        )

        return

    task = Task(
        id=None,
        title=Validator.clean_text(title),
        category=Validator.clean_text(category),
        priority=priority,
        completed=False,
        hours=hours,
        created_at=datetime.now().isoformat(),
        email=email
    )

    task_id = database.add_task(
        task
    )

    print(
        f"\n✓ Task created successfully!"
    )

    print(
        f"Task ID: {task_id}"
    )


# =============================================================
# COMPLETE TASK
# =============================================================

def complete_task_cli():

    try:

        task_id = int(
            input(
                "Enter task ID: "
            )
        )

    except ValueError:

        print(
            "Please enter a valid ID."
        )

        return

    if database.complete_task(
        task_id
    ):

        print(
            "\n✓ Task completed!"
        )

    else:

        print(
            "\nTask not found."
        )


# =============================================================
# DELETE TASK
# =============================================================

def delete_task_cli():

    try:

        task_id = int(
            input(
                "Enter task ID: "
            )
        )

    except ValueError:

        print(
            "Please enter a valid ID."
        )

        return

    task = database.get_task(
        task_id
    )

    if not task:

        print(
            "\nTask not found."
        )

        return

    confirmation = input(
        f"Delete '{task.title}'? (y/n): "
    ).lower()

    if confirmation == "y":

        database.delete_task(
            task_id
        )

        print(
            "\n✓ Task deleted."
        )

    else:

        print(
            "\nDeletion cancelled."
        )


# =============================================================
# SEARCH
# =============================================================

def search_tasks():

    query = input(
        "\nSearch: "
    ).strip().lower()

    tasks = database.get_tasks()

    results = [
        task
        for task in tasks
        if query in task.title.lower()
        or query in task.category.lower()
        or query in task.priority.lower()
    ]

    if not results:

        print(
            "\nNo matching tasks."
        )

        return

    print(
        f"\nFound {len(results)} result(s):"
    )

    for task in results:

        print_task(task)


# =============================================================
# ANALYTICS DASHBOARD
# =============================================================

def show_analytics():

    print(
        "\n" + "=" * 65
    )

    print(
        "  PRODUCTIVITY ANALYTICS"
    )

    print(
        "=" * 65
    )

    total = analytics.total_tasks()
    completed = analytics.completed_tasks()
    pending = analytics.pending_tasks()
    hours = analytics.total_hours()
    completed_hours = analytics.completed_hours()
    rate = analytics.completion_rate()
    average = analytics.average_hours()
    category = analytics.most_productive_category()

    print(
        f"""
Total Tasks          : {total}
Completed Tasks      : {completed}
Pending Tasks        : {pending}

Total Study Hours    : {hours:.2f}
Completed Hours      : {completed_hours:.2f}
Average Task Hours   : {average:.2f}

Completion Rate      : {rate:.2f}%

Top Category         : {category}
"""
    )

    print(
        "\nCATEGORY BREAKDOWN"
    )

    category_stats = (
        analytics.category_statistics()
    )

    if not category_stats.empty:
        print(
            category_stats.to_string()
        )

    print(
        "\nPRIORITY BREAKDOWN"
    )

    priority_stats = (
        analytics.priority_statistics()
    )

    if not priority_stats.empty:
        print(
            priority_stats.to_string()
        )


# =============================================================
# INTERNET CHECK
# =============================================================

def internet_check():

    print(
        "\nChecking internet connection..."
    )

    result = asyncio.run(
        AsyncInternetService.check_internet()
    )

    if result["online"]:

        print(
            f"✓ Online "
            f"(HTTP {result['status_code']})"
        )

    else:

        print(
            "✗ No internet connection."
        )


# =============================================================
# GITHUB API
# =============================================================

def github_api_demo():

    print(
        "\nConnecting to GitHub API..."
    )

    result = asyncio.run(
        AsyncInternetService.get_github_api_info()
    )

    if "error" in result:

        print(
            f"API error: {result['error']}"
        )

        return

    print(
        "\nGitHub API information:"
    )

    print(
        f"Current API version: "
        f"{result.get('current_user_url', 'N/A')}"
    )

    print(
        f"Repository URL: "
        f"{result.get('repository_url', 'N/A')}"
    )

    print(
        "\n✓ Successfully connected to GitHub API."
    )


# =============================================================
# EXPORT MENU
# =============================================================

def export_menu():

    exporter = ExportManager(
        database
    )

    print(
        """
--- EXPORT DATA ---

1. Export JSON
2. Export CSV
3. Export both
"""
    )

    choice = input(
        "Choose: "
    ).strip()

    if choice == "1":

        exporter.export_json()

    elif choice == "2":

        exporter.export_csv()

    elif choice == "3":

        exporter.export_json()
        exporter.export_csv()

    else:

        print(
            "Invalid option."
        )


# =============================================================
# REPORT
# =============================================================

def generate_report():

    report = analytics.generate_report()

    print(report)

    print(
        f"\nReport saved to: {REPORT_FILE}"
    )


# =============================================================
# CHART
# =============================================================

def generate_chart():

    analytics.generate_chart()


# =============================================================
# FASTAPI SERVER
# =============================================================

def start_api_server():

    import uvicorn

    print(
        "\nStarting FastAPI server..."
    )

    print(
        f"API available at:"
        f" http://{API_HOST}:{API_PORT}"
    )

    print(
        f"Swagger documentation:"
        f" http://{API_HOST}:{API_PORT}/docs"
    )

    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT
    )


def start_api_in_background():

    thread = threading.Thread(
        target=start_api_server,
        daemon=True
    )

    thread.start()

    return thread


# =============================================================
# SYSTEM INFORMATION
# =============================================================

def show_system_info():

    print(
        "\n" + "=" * 65
    )

    print(
        "  SYSTEM INFORMATION"
    )

    print(
        "=" * 65
    )

    print(
        f"""
Application : {APP_NAME}
Version     : {VERSION}
Python      : {os.sys.version.split()[0]}
Database    : {DATABASE_FILE.name}
JSON File   : {JSON_FILE.name}
CSV File    : {CSV_FILE.name}
Report      : {REPORT_FILE.name}
Chart       : {CHART_FILE.name}
Log File    : {LOG_FILE.name}
"""
    )


# =============================================================
# MAIN MENU
# =============================================================

def show_menu():

    print(
        """
=============================================================
                         MAIN MENU
=============================================================

1.  Add task
2.  List tasks
3.  Complete task
4.  Delete task
5.  Search tasks
6.  Productivity analytics
7.  Generate report
8.  Generate chart
9.  Export data
10. Check internet
11. GitHub API demo
12. Start FastAPI server
13. System information
0.  Exit

=============================================================
"""
    )


# =============================================================
# MAIN APPLICATION
# =============================================================

def main():

    print_header()

    print(
        "\nInitializing application..."
    )

    SampleData.create(
        database
    )

    print(
        "✓ Database ready."
    )

    print(
        "✓ Analytics engine ready."
    )

    print(
        "✓ API ready."
    )

    while True:

        show_menu()

        choice = input(
            "Select an option: "
        ).strip()

        try:

            if choice == "1":

                add_task_cli()

            elif choice == "2":

                list_tasks()

            elif choice == "3":

                complete_task_cli()

            elif choice == "4":

                delete_task_cli()

            elif choice == "5":

                search_tasks()

            elif choice == "6":

                show_analytics()

            elif choice == "7":

                generate_report()

            elif choice == "8":

                generate_chart()

            elif choice == "9":

                export_menu()

            elif choice == "10":

                internet_check()

            elif choice == "11":

                github_api_demo()

            elif choice == "12":

                start_api_server()

            elif choice == "13":

                show_system_info()

            elif choice == "0":

                print(
                    "\nThank you for completing "
                    "30 Days of Python!"
                )

                print(
                    "Keep building. Keep learning. "
                    "Keep coding. 🚀"
                )

                logger.info(
                    "Application closed."
                )

                break

            else:

                print(
                    "\nInvalid option."
                )

        except KeyboardInterrupt:

            print(
                "\n\nApplication interrupted."
            )

            break

        except Exception as error:

            logger.exception(
                "Unexpected application error."
            )

            print(
                f"\nUnexpected error: {error}"
            )


# =============================================================
# ENTRY POINT
# =============================================================

if __name__ == "__main__":

    main()
```
