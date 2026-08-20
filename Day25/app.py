import http.server
import socketserver
import sqlite3
import urllib.parse
import json
import html
from datetime import datetime


# ============================================================
# Configuration
# ============================================================

HOST = "127.0.0.1"
PORT = 8000
DATABASE = "tasks.db"


# ============================================================
# Database
# ============================================================

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def get_all_tasks():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY id DESC
    """)

    tasks = cursor.fetchall()

    connection.close()

    return tasks


def get_task(task_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    task = cursor.fetchone()

    connection.close()

    return task


def create_task(title, description):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (title, description, completed, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        title,
        description,
        0,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()

    task_id = cursor.lastrowid

    connection.close()

    return task_id


def toggle_task(task_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed =
            CASE
                WHEN completed = 0 THEN 1
                ELSE 0
            END
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()


def delete_task(task_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()


# ============================================================
# HTML Helpers
# ============================================================

def page_template(title, content):
    return f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{html.escape(title)}</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #222;
        }}

        header {{
            background: #222;
            color: white;
            padding: 25px;
            text-align: center;
        }}

        header h1 {{
            margin: 0;
        }}

        nav {{
            margin-top: 12px;
        }}

        nav a {{
            color: white;
            margin: 0 10px;
            text-decoration: none;
        }}

        .container {{
            width: 90%;
            max-width: 900px;
            margin: 30px auto;
        }}

        .card {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        }}

        input,
        textarea {{
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 15px;
        }}

        textarea {{
            min-height: 100px;
            resize: vertical;
        }}

        button {{
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            background: #222;
            color: white;
        }}

        button:hover {{
            opacity: 0.8;
        }}

        .task {{
            border-left: 5px solid #222;
            padding: 15px;
            margin-bottom: 15px;
            background: #fafafa;
        }}

        .completed {{
            opacity: 0.6;
        }}

        .completed h3 {{
            text-decoration: line-through;
        }}

        .actions {{
            margin-top: 15px;
        }}

        .actions form {{
            display: inline;
        }}

        .delete {{
            background: #c0392b;
        }}

        .toggle {{
            background: #2980b9;
        }}

        .api-box {{
            background: #1e1e1e;
            color: #eee;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }}

        footer {{
            text-align: center;
            padding: 30px;
            color: #777;
        }}

    </style>
</head>

<body>

<header>

    <h1>Python Task Manager</h1>

    <nav>
        <a href="/">Home</a>
        <a href="/new">New Task</a>
        <a href="/api/tasks">JSON API</a>
    </nav>

</header>

<div class="container">

    {content}

</div>

<footer>
    Built with Python's standard library — no web framework.
</footer>

</body>

</html>
"""


def render_tasks(tasks):

    if not tasks:
        return """
        <div class="card">
            <h2>No tasks yet</h2>
            <p>Create your first task.</p>
        </div>
        """

    output = ""

    for task in tasks:

        task_class = "completed" if task["completed"] else ""

        status = (
            "Completed"
            if task["completed"]
            else "Pending"
        )

        output += f"""
        <div class="task {task_class}">

            <h3>
                {html.escape(task["title"])}
            </h3>

            <p>
                {html.escape(task["description"] or "")}
            </p>

            <small>
                Status: {status}<br>
                Created: {html.escape(task["created_at"])}
            </small>

            <div class="actions">

                <form method="POST"
                      action="/toggle">

                    <input type="hidden"
                           name="id"
                           value="{task["id"]}">

                    <button class="toggle">
                        Toggle
                    </button>

                </form>

                <form method="POST"
                      action="/delete">

                    <input type="hidden"
                           name="id"
                           value="{task["id"]}">

                    <button class="delete">
                        Delete
                    </button>

                </form>

            </div>

        </div>
        """

    return output


# ============================================================
# HTTP Server
# ============================================================

class TaskServer(http.server.BaseHTTPRequestHandler):

    # --------------------------------------------------------
    # Utility methods
    # --------------------------------------------------------

    def send_html(self, content, status=200):

        content = content.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.end_headers()

        self.wfile.write(content)


    def send_json(self, data, status=200):

        content = json.dumps(
            data,
            indent=4
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.end_headers()

        self.wfile.write(content)


    def redirect(self, location):

        self.send_response(303)

        self.send_header(
            "Location",
            location
        )

        self.end_headers()


    def parse_form(self):

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        body = self.rfile.read(
            content_length
        ).decode("utf-8")

        return urllib.parse.parse_qs(body)


    # --------------------------------------------------------
    # GET Requests
    # --------------------------------------------------------

    def do_GET(self):

        parsed_url = urllib.parse.urlparse(
            self.path
        )

        path = parsed_url.path

        # Home page
        if path == "/":

            tasks = get_all_tasks()

            content = """
            <div class="card">

                <h2>Task Manager</h2>

                <p>
                    A web application created entirely
                    with Python's standard library.
                </p>

                <a href="/new">
                    <button>Create New Task</button>
                </a>

            </div>
            """

            content += render_tasks(tasks)

            self.send_html(
                page_template(
                    "Task Manager",
                    content
                )
            )

        # New task page
        elif path == "/new":

            content = """
            <div class="card">

                <h2>Create New Task</h2>

                <form method="POST"
                      action="/create">

                    <label>
                        Task Title
                    </label>

                    <input
                        type="text"
                        name="title"
                        placeholder="Enter task title"
                        required
                    >

                    <label>
                        Description
                    </label>

                    <textarea
                        name="description"
                        placeholder="Describe your task"
                    ></textarea>

                    <button type="submit">
                        Create Task
                    </button>

                </form>

            </div>
            """

            self.send_html(
                page_template(
                    "New Task",
                    content
                )
            )

        # JSON API
        elif path == "/api/tasks":

            tasks = get_all_tasks()

            data = []

            for task in tasks:

                data.append({
                    "id": task["id"],
                    "title": task["title"],
                    "description": task["description"],
                    "completed": bool(
                        task["completed"]
                    ),
                    "created_at": task["created_at"]
                })

            self.send_json(data)

        # Individual task API
        elif path.startswith("/api/tasks/"):

            try:

                task_id = int(
                    path.split("/")[-1]
                )

                task = get_task(task_id)

                if task is None:

                    self.send_json(
                        {
                            "error": "Task not found"
                        },
                        404
                    )

                    return

                self.send_json({
                    "id": task["id"],
                    "title": task["title"],
                    "description": task["description"],
                    "completed": bool(
                        task["completed"]
                    ),
                    "created_at": task["created_at"]
                })

            except ValueError:

                self.send_json(
                    {
                        "error": "Invalid task ID"
                    },
                    400
                )

        # 404
        else:

            content = """
            <div class="card">

                <h2>404 - Page Not Found</h2>

                <p>
                    The page you requested does not exist.
                </p>

                <a href="/">
                    Go back home
                </a>

            </div>
            """

            self.send_html(
                page_template(
                    "404",
                    content
                ),
                404
            )


    # --------------------------------------------------------
    # POST Requests
    # --------------------------------------------------------

    def do_POST(self):

        parsed_url = urllib.parse.urlparse(
            self.path
        )

        path = parsed_url.path

        form = self.parse_form()

        # Create task
        if path == "/create":

            title = form.get(
                "title",
                [""]
            )[0].strip()

            description = form.get(
                "description",
                [""]
            )[0].strip()

            if not title:

                self.send_html(
                    page_template(
                        "Error",
                        """
                        <div class="card">
                            <h2>Error</h2>
                            <p>
                                Task title cannot be empty.
                            </p>
                            <a href="/new">
                                Go back
                            </a>
                        </div>
                        """
                    ),
                    400
                )

                return

            create_task(
                title,
                description
            )

            self.redirect("/")

        # Toggle task
        elif path == "/toggle":

            try:

                task_id = int(
                    form.get(
                        "id",
                        ["0"]
                    )[0]
                )

                toggle_task(task_id)

                self.redirect("/")

            except ValueError:

                self.send_html(
                    "<h1>Invalid task ID</h1>",
                    400
                )

        # Delete task
        elif path == "/delete":

            try:

                task_id = int(
                    form.get(
                        "id",
                        ["0"]
                    )[0]
                )

                delete_task(task_id)

                self.redirect("/")

            except ValueError:

                self.send_html(
                    "<h1>Invalid task ID</h1>",
                    400
                )

        # Unknown POST route
        else:

            self.send_html(
                page_template(
                    "404",
                    """
                    <div class="card">
                        <h2>404</h2>
                        <p>
                            POST endpoint not found.
                        </p>
                    </div>
                    """
                ),
                404
            )


# ============================================================
# Server Startup
# ============================================================

def main():

    initialize_database()

    print("=" * 55)
    print("Python Web App Without a Framework")
    print("=" * 55)
    print(f"Server running at:")
    print(f"http://{HOST}:{PORT}")
    print()
    print("Available routes:")
    print("/")
    print("/new")
    print("/api/tasks")
    print("/api/tasks/<id>")
    print()
    print("Press CTRL+C to stop the server.")
    print("=" * 55)

    with socketserver.ThreadingTCPServer(
        (HOST, PORT),
        TaskServer
    ) as server:

        server.serve_forever()


if __name__ == "__main__":
    main()