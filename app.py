from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'tasks.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == "POST":
        task = request.form.get("task")
        if task:
            c.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
            conn.commit()
        conn.close()
        return redirect(url_for("home"))

    c.execute("SELECT id, task, done FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return render_template("home.html", tasks=tasks)

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET done = NOT done WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/done/<int:task_id>")
def mark_done(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Toggle done status
    c.execute("""
        UPDATE tasks
        SET done = CASE WHEN done IS NULL OR done=0 THEN 1 ELSE 0 END
        WHERE id = ?
    """, (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    if request.method == "POST":
        new_text = request.form["task"]
        c.execute("UPDATE tasks SET task = ? WHERE id = ?", (new_text, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    c.execute("SELECT task FROM tasks WHERE id = ?", (task_id,))
    task = c.fetchone()
    conn.close()

    return render_template("edit.html", task=task, task_id=task_id)

if __name__ == "__main__":
    app.run(debug=True)
