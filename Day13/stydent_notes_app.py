from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from flask import Flask, request, redirect, render_template_string
import requests
import threading
import uvicorn

# =====================================================
# FASTAPI BACKEND
# =====================================================

api = FastAPI(title="Student Notes API")

class Note(BaseModel):
    id: int
    title: str
    content: str

# Temporary database
notes: List[Note] = [
    Note(id=1, title="Python", content="Practice loops and functions"),
    Note(id=2, title="Flask", content="Learn routes and templates")
]

@api.get("/notes")
def get_notes():
    return notes

@api.post("/notes")
def add_note(note: Note):
    notes.append(note)
    return {"message": "Note added successfully"}

# =====================================================
# FLASK FRONTEND
# =====================================================

web = Flask(__name__)

API_URL = "http://127.0.0.1:8000/notes"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Notes</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f2f2;
            margin: 40px;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 700px;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            margin-bottom: 15px;
        }
        button {
            padding: 10px 15px;
            background: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .note {
            border: 1px solid #ddd;
            padding: 15px;
            margin-top: 15px;
            border-radius: 8px;
            background: #fafafa;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📘 Student Notes Web App</h1>

        <form method="POST" action="/add">
            <input type="number" name="id" placeholder="Note ID" required>
            <input type="text" name="title" placeholder="Note title" required>
            <textarea name="content" placeholder="Write your note here" rows="4" required></textarea>
            <button type="submit">Add Note</button>
        </form>

        <h2>Saved Notes</h2>

        {% for note in notes %}
            <div class="note">
                <h3>{{ note.title }} (ID: {{ note.id }})</h3>
                <p>{{ note.content }}</p>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@web.route("/")
def home():
    response = requests.get(API_URL)
    all_notes = response.json()
    return render_template_string(HTML, notes=all_notes)

@web.route("/add", methods=["POST"])
def add():
    note = {
        "id": int(request.form["id"]),
        "title": request.form["title"],
        "content": request.form["content"]
    }

    requests.post(API_URL, json=note)
    return redirect("/")

# =====================================================
# RUN BOTH SERVERS TOGETHER
# =====================================================

def run_api():
    uvicorn.run(api, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    # Start FastAPI in background thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    print("FastAPI running on http://127.0.0.1:8000")
    print("Flask running on http://127.0.0.1:5000")

    # Start Flask
    web.run(port=5000, debug=False)
