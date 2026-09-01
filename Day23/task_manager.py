import argparse
import json
import os
from datetime import datetime


DATA_FILE = "tasks.json"


# ---------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------

def load_tasks():
    """Load tasks from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read the task file.")
        return []


def save_tasks(tasks):
    """Save tasks to the JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4)
    except OSError as error:
        print(f"Error saving tasks: {error}")


def get_next_id(tasks):
    """Generate the next available task ID."""
    if not tasks:
        return 1

    return max(task["id"] for task in tasks) + 1


def current_time():
    """Return the current date and time as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_task(tasks, task_id):
    """Find a task by its ID."""
    for task in tasks:
        if task["id"] == task_id:
            return task

    return None


def print_task(task):
    """Display one task in a readable format."""
    status = "✓" if task["completed"] else " "

    print(
        f"[{status}] "
        f"#{task['id']} | "
        f"{task['title']} | "
        f"Priority: {task['priority']} | "
        f"Due: {task['due_date'] or 'None'}"
    )


# ---------------------------------------------------------
# Add Task
# ---------------------------------------------------------

def add_task(args):
    """Create a new task."""
    tasks = load_tasks()

    task = {
        "id": get_next_id(tasks),
        "title": args.title,
        "description": args.description or "",
        "priority": args.priority,
        "due_date": args.due,
        "completed": False,
        "created_at": current_time(),
        "completed_at": None
    }

    tasks.append(task)
    save_tasks(tasks)

    print("\nTask added successfully!")
    print_task(task)


# ---------------------------------------------------------
# List Tasks
# ---------------------------------------------------------

def list_tasks(args):
    """Display tasks based on filters."""
    tasks = load_tasks()

    if not tasks:
        print("No tasks found.")
        return

    filtered_tasks = tasks

    if args.status == "pending":
        filtered_tasks = [
            task for task in filtered_tasks
            if not task["completed"]
        ]

    elif args.status == "completed":
        filtered_tasks = [
            task for task in filtered_tasks
            if task["completed"]
        ]

    if args.priority:
        filtered_tasks = [
            task for task in filtered_tasks
            if task["priority"] == args.priority
        ]

    if not filtered_tasks:
        print("No tasks match your filters.")
        return

    print("\nYour Tasks")
    print("-" * 75)

    for task in filtered_tasks:
        print_task(task)

    print("-" * 75)
    print(f"Showing {len(filtered_tasks)} task(s).")


# ---------------------------------------------------------
# Complete Task
# ---------------------------------------------------------

def complete_task(args):
    """Mark a task as completed."""
    tasks = load_tasks()

    task = find_task(tasks, args.id)

    if task is None:
        print(f"Task #{args.id} does not exist.")
        return

    if task["completed"]:
        print(f"Task #{args.id} is already completed.")
        return

    task["completed"] = True
    task["completed_at"] = current_time()

    save_tasks(tasks)

    print(f"Task #{args.id} marked as completed.")


# ---------------------------------------------------------
# Reopen Task
# ---------------------------------------------------------

def reopen_task(args):
    """Reopen a completed task."""
    tasks = load_tasks()

    task = find_task(tasks, args.id)

    if task is None:
        print(f"Task #{args.id} does not exist.")
        return

    if not task["completed"]:
        print(f"Task #{args.id} is already pending.")
        return

    task["completed"] = False
    task["completed_at"] = None

    save_tasks(tasks)

    print(f"Task #{args.id} has been reopened.")


# ---------------------------------------------------------
# Delete Task
# ---------------------------------------------------------

def delete_task(args):
    """Delete a task."""
    tasks = load_tasks()

    task = find_task(tasks, args.id)

    if task is None:
        print(f"Task #{args.id} does not exist.")
        return

    print(f"\nDeleting task: {task['title']}")

    tasks.remove(task)
    save_tasks(tasks)

    print(f"Task #{args.id} deleted successfully.")


# ---------------------------------------------------------
# Search
# ---------------------------------------------------------

def search_tasks(args):
    """Search tasks by title or description."""
    tasks = load_tasks()

    query = args.query.lower()

    results = [
        task for task in tasks
        if query in task["title"].lower()
        or query in task["description"].lower()
    ]

    if not results:
        print(f'No tasks found for "{args.query}".')
        return

    print(f'\nSearch results for "{args.query}"')
    print("-" * 75)

    for task in results:
        print_task(task)

    print("-" * 75)
    print(f"Found {len(results)} task(s).")


# ---------------------------------------------------------
# Show Task Details
# ---------------------------------------------------------

def show_task(args):
    """Display complete information about a task."""
    tasks = load_tasks()

    task = find_task(tasks, args.id)

    if task is None:
        print(f"Task #{args.id} does not exist.")
        return

    print("\nTask Details")
    print("-" * 40)
    print(f"ID:           {task['id']}")
    print(f"Title:        {task['title']}")
    print(f"Description:  {task['description'] or 'None'}")
    print(f"Priority:     {task['priority']}")
    print(f"Due Date:     {task['due_date'] or 'None'}")
    print(f"Completed:    {'Yes' if task['completed'] else 'No'}")
    print(f"Created:      {task['created_at']}")
    print(f"Completed At: {task['completed_at'] or 'N/A'}")
    print("-" * 40)


# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

def show_stats(args):
    """Display statistics about the task list."""
    tasks = load_tasks()

    if not tasks:
        print("No tasks available.")
        return

    total = len(tasks)
    completed = sum(task["completed"] for task in tasks)
    pending = total - completed

    high = sum(
        task["priority"] == "high"
        for task in tasks
        if not task["completed"]
    )

    medium = sum(
        task["priority"] == "medium"
        for task in tasks
        if not task["completed"]
    )

    low = sum(
        task["priority"] == "low"
        for task in tasks
        if not task["completed"]
    )

    completion_rate = (completed / total) * 100

    print("\nTask Statistics")
    print("-" * 40)
    print(f"Total tasks:       {total}")
    print(f"Completed:         {completed}")
    print(f"Pending:           {pending}")
    print(f"Completion rate:   {completion_rate:.1f}%")
    print("\nPending priorities:")
    print(f"High:              {high}")
    print(f"Medium:            {medium}")
    print(f"Low:               {low}")
    print("-" * 40)


# ---------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------

def create_parser():
    """Create the command-line interface."""
    parser = argparse.ArgumentParser(
        description="A simple but powerful command-line task manager."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ---------------- ADD ----------------

    add_parser = subparsers.add_parser(
        "add",
        help="Add a new task."
    )

    add_parser.add_argument(
        "title",
        help="Title of the task."
    )

    add_parser.add_argument(
        "-d",
        "--description",
        help="Optional task description."
    )

    add_parser.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="Task priority."
    )

    add_parser.add_argument(
        "--due",
        help="Due date, e.g. 2026-08-25."
    )

    add_parser.set_defaults(function=add_task)

    # ---------------- LIST ----------------

    list_parser = subparsers.add_parser(
        "list",
        help="List your tasks."
    )

    list_parser.add_argument(
        "--status",
        choices=["all", "pending", "completed"],
        default="all",
        help="Filter tasks by status."
    )

    list_parser.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
        help="Filter tasks by priority."
    )

    list_parser.set_defaults(function=list_tasks)

    # ---------------- COMPLETE ----------------

    complete_parser = subparsers.add_parser(
        "done",
        help="Mark a task as completed."
    )

    complete_parser.add_argument(
        "id",
        type=int,
        help="ID of the task."
    )

    complete_parser.set_defaults(function=complete_task)

    # ---------------- REOPEN ----------------

    reopen_parser = subparsers.add_parser(
        "reopen",
        help="Reopen a completed task."
    )

    reopen_parser.add_argument(
        "id",
        type=int,
        help="ID of the task."
    )

    reopen_parser.set_defaults(function=reopen_task)

    # ---------------- DELETE ----------------

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task."
    )

    delete_parser.add_argument(
        "id",
        type=int,
        help="ID of the task."
    )

    delete_parser.set_defaults(function=delete_task)

    # ---------------- SEARCH ----------------

    search_parser = subparsers.add_parser(
        "search",
        help="Search your tasks."
    )

    search_parser.add_argument(
        "query",
        help="Text to search for."
    )

    search_parser.set_defaults(function=search_tasks)

    # ---------------- SHOW ----------------

    show_parser = subparsers.add_parser(
        "show",
        help="Show detailed information about a task."
    )

    show_parser.add_argument(
        "id",
        type=int,
        help="ID of the task."
    )

    show_parser.set_defaults(function=show_task)

    # ---------------- STATS ----------------

    stats_parser = subparsers.add_parser(
        "stats",
        help="Show task statistics."
    )

    stats_parser.set_defaults(function=show_stats)

    return parser


# ---------------------------------------------------------
# Main Program
# ---------------------------------------------------------

def main():
    parser = create_parser()
    args = parser.parse_args()

    args.function(args)


if __name__ == "__main__":
    main()
