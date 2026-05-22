from flask import Flask, render_template, request, redirect, url_for, make_response, session
import sqlite3
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "secretkey123"


def init_db():
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        category TEXT,
        priority TEXT,
        due_date TEXT,
        done INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("todo.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("todo.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = c.fetchone()

        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/")

        return "Invalid Login"

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("todo.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM tasks WHERE user_id=?",
        (user_id,)
    )

    tasks = c.fetchall()

    conn.close()

    total = len(tasks)

    completed = len(
        [t for t in tasks if t[6] == 1]
    )

    progress = 0

    if total > 0:
        progress = int(
            (completed/total)*100
        )

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        progress=progress
    )


@app.route("/add", methods=["POST"])
def add():

    user_id = session["user_id"]

    task = request.form["task"]
    category = request.form["category"]
    priority = request.form["priority"]
    due_date = request.form["due_date"]

    conn = sqlite3.connect("todo.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO tasks
    (user_id,task,category,priority,due_date)
    VALUES(?,?,?,?,?)
    """,
    (user_id,task,category,priority,due_date))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/done/<int:id>")
def done(id):

    conn = sqlite3.connect("todo.db")
    c = conn.cursor()

    c.execute(
        "UPDATE tasks SET done=1 WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("todo.db")
    c = conn.cursor()

    c.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    conn = sqlite3.connect("todo.db")
    c = conn.cursor()

    if request.method=="POST":

        task=request.form["task"]
        category=request.form["category"]
        priority=request.form["priority"]
        due_date=request.form["due_date"]

        c.execute("""
        UPDATE tasks
        SET task=?,category=?,priority=?,due_date=?
        WHERE id=?
        """,
        (task,category,priority,due_date,id))

        conn.commit()

        conn.close()

        return redirect("/")

    c.execute(
        "SELECT * FROM tasks WHERE id=?",
        (id,)
    )

    task=c.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        task=task
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)