import os
import re
from functools import wraps

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session

from db import get_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM users WHERE user_id = %s", (session["user_id"],))
                if cur.fetchone() is None:
                    session.clear()
                    return redirect(url_for("login"))
        finally:
            conn.close()

        return view(*args, **kwargs)
    return wrapped


# ---------- Register ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("todos"))
        return render_template("register.html", errors={}, form={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = {}
    if not name:
        errors["name"] = "Name is required"
    if not email:
        errors["email"] = "Email is required"
    elif not EMAIL_RE.match(email):
        errors["email"] = "Please enter a valid email"
    if not password:
        errors["password"] = "Password is required"
    if not confirm_password:
        errors["confirm_password"] = "Confirm password is required"
    if password and confirm_password and password != confirm_password:
        errors["confirm_password"] = "Passwords do not match"

    if errors:
        return render_template(
            "register.html",
            errors=errors,
            form={"name": name, "email": email},
        )

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                    (email, name, password_hash),
                )
            except pymysql.err.IntegrityError:
                return render_template(
                    "register.html",
                    errors={"email": "Email Already Exists"},
                    form={"name": name, "email": email},
                )
            new_user_id = cur.lastrowid
    finally:
        conn.close()

    session["user_id"] = new_user_id
    session["name"] = name
    return redirect(url_for("todos"))


# ---------- Login ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("todos"))
        return render_template("login.html", errors={}, form={})

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = {}
    if not email:
        errors["email"] = "Email is required"
    if not password:
        errors["password"] = "Password is required"

    if errors:
        return render_template("login.html", errors=errors, form={"email": email})

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, name, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return render_template(
            "login.html",
            errors={"general": "Invalid email or password"},
            form={"email": email},
        )

    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect(url_for("todos"))


# ---------- Logout ----------

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- To-dos ----------

@app.route("/")
def index():
    return redirect(url_for("todos") if "user_id" in session else url_for("login"))


@app.route("/todos")
@login_required
def todos():
    user_id = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC",
                (user_id,),
            )
            todo_rows = cur.fetchall()
    finally:
        conn.close()

    filter_value = request.args.get("filter", "all")
    if filter_value == "open":
        visible = [t for t in todo_rows if not t["is_done"]]
    elif filter_value == "done":
        visible = [t for t in todo_rows if t["is_done"]]
    else:
        filter_value = "all"
        visible = todo_rows

    open_count = sum(1 for t in todo_rows if not t["is_done"])

    return render_template(
        "todos.html",
        todos=visible,
        open_count=open_count,
        total_count=len(todo_rows),
        filter_value=filter_value,
        name=session.get("name"),
        error=None,
    )


@app.route("/todos/add", methods=["POST"])
@login_required
def add_todo():
    user_id = session["user_id"]
    title = request.form.get("title", "").strip()

    error = None
    if not title:
        error = "Title is required"
    elif len(title) > 200:
        error = "Title is too long"

    if error:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC",
                    (user_id,),
                )
                todo_rows = cur.fetchall()
        finally:
            conn.close()
        open_count = sum(1 for t in todo_rows if not t["is_done"])
        return render_template(
            "todos.html",
            todos=todo_rows,
            open_count=open_count,
            total_count=len(todo_rows),
            filter_value="all",
            name=session.get("name"),
            error=error,
        )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (user_id, title) VALUES (%s, %s)",
                (user_id, title),
            )
    finally:
        conn.close()

    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
@login_required
def edit_todo(todo_id):
    user_id = session["user_id"]
    title = request.form.get("title", "").strip()

    if title and len(title) <= 200:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
                    (title, todo_id, user_id),
                )
        finally:
            conn.close()

    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
@login_required
def toggle_todo(todo_id):
    user_id = session["user_id"]
    is_done = 1 if request.form.get("is_done") == "1" else 0

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
                (is_done, todo_id, user_id),
            )
    finally:
        conn.close()

    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
@login_required
def delete_todo(todo_id):
    user_id = session["user_id"]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                (todo_id, user_id),
            )
    finally:
        conn.close()

    return redirect(url_for("todos"))


# ---------- Error pages ----------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="Something went wrong"), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=True, port=port)
