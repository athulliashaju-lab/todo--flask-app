from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            task TEXT,
            done INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")

    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/done/<int:id>")
def done(id):
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET done = 1 WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))
@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    new_task = request.form.get("task")

    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET task=? WHERE id=?", (new_task, id))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)