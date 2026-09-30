

import os
from flask import Flask, flash, redirect, render_template_string, request, send_from_directory, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

notes_db = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Global Notes Hub - MVP</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f9f9f9; color: #333; }
        h1, h2 { color: #2c3e50; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input, select, button { display: block; width: 100%; margin-bottom: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background: #3498db; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background: #2980b9; }
        .note-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .note-item:last-child { border-bottom: none; }
        .tag { background: #e0f7fa; color: #00796b; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }
    </style>
</head>
<body>
    <h1>📚 Global Notes Hub (MVP)</h1>
    
    <div class="card">
        <h2>Upload Lecture Notes</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="text" name="discipline" placeholder="Discipline (e.g., Clinical Medicine, Computer Science)" required>
            <input type="text" name="university" placeholder="University Name (e.g., University of Kabianga)" required>
            <input type="text" name="course_code" placeholder="Course Code & Title (e.g., MED 201 - Anatomy)" required>
            <input type="file" name="file" required>
            <button type="submit">Upload Notes</button>
        </form>
    </div>

    <div class="card">
        <h2>Available Notes</h2>
        <form method="GET" action="/">
            <input type="text" name="search" placeholder="Search by course code, university, or discipline..." value="{{ search_query }}">
        </form>

        {% if notes %}
            {% for note in notes %}
                <div class="note-item">
                    <strong>{{ note.course_code }}</strong> <span class="tag">{{ note.discipline }}</span><br>
                    <small>University: {{ note.university }} | Uploaded by Peer</small><br>
                    <a href="/download/{{ note.filename }}">📥 Download File ({{ note.filename }})</a>
                </div>
            {% endfor %}
        {% else %}
            <p>No notes found. Be the first to upload!</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("search", "").lower()
    if search_query:
        filtered_notes = [
            n for n in notes_db
            if search_query in n["course_code"].lower()
            or search_query in n["university"].lower()
            or search_query in n["discipline"].lower()
        ]
    else:
        filtered_notes = notes_db

    return render_template_string(HTML_TEMPLATE, notes=filtered_notes, search_query=search_query)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(url_for("index"))
    
    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))
    
    if file:
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
        notes_db.append({
            "discipline": request.form.get("discipline"),
            "university": request.form.get("university"),
            "course_code": request.form.get("course_code"),
            "filename": filename
        })
    return redirect(url_for("index"))

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

