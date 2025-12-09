import os
from functools import wraps
from collections import Counter

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from dao import add_employee, update_employee, delete_employee, get_employee_by_id, get_all_employees
from models import Employee
from db import init_db, get_connection

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # change in real app

# Initialize DB
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print("DB init error:", e)


# ---------- Decorators ---------- #

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("You are not allowed to perform this action.", "error")
            return redirect(url_for("list_employees"))
        return view_func(*args, **kwargs)
    return wrapper


# ---------- Auth ---------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()

        if not email or not phone:
            flash("Please enter both email and phone number.", "error")
            return redirect(url_for("login"))

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, email, phone, is_admin FROM users WHERE LOWER(email) = ? AND phone = ?",
                (email, phone),
            )
            row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            flash("Invalid email or phone. Access denied.", "error")
            return redirect(url_for("login"))

        user_id, name, _, _, is_admin = row

        session["user_id"] = user_id
        session["user_name"] = name
        session["is_admin"] = bool(is_admin)

        flash(f"Welcome, {name}!", "success")
        return redirect(url_for("list_employees"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ---------- Core pages ---------- #

@app.route("/")
def index():
    return redirect(url_for("list_employees"))


@app.route("/employees")
@login_required
def list_employees():
    employees = get_all_employees()
    return render_template(
        "employee_list.html",
        employees=employees,
        is_admin=session.get("is_admin", False),
        user_name=session.get("user_name", "User"),
    )


@app.route("/employees/add", methods=["GET", "POST"])
@admin_required
def add_employee_view():
    if request.method == "POST":
        try:
            emp = Employee(
                id=int(request.form["id"]),
                first_name=request.form["firstName"],
                last_name=request.form["lastName"],
                salary=float(request.form["salary"]),
                designation=request.form["designation"],
            )
        except (KeyError, ValueError):
            flash("Invalid input.", "error")
            return redirect(url_for("add_employee_view"))

        if add_employee(emp):
            flash("Employee added successfully!", "success")
        else:
            flash("Failed to add employee.", "error")
        return redirect(url_for("list_employees"))

    return render_template(
        "employee_add.html",
        is_admin=session.get("is_admin", False),
        user_name=session.get("user_name", "User"),
    )


@app.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_employee_view(emp_id: int):
    emp = get_employee_by_id(emp_id)
    if not emp:
        flash("Employee not found.", "error")
        return redirect(url_for("list_employees"))

    if request.method == "POST":
        try:
            emp.first_name = request.form["firstName"]
            emp.last_name = request.form["lastName"]
            emp.salary = float(request.form["salary"])
            emp.designation = request.form["designation"]
        except (KeyError, ValueError):
            flash("Invalid input.", "error")
            return redirect(url_for("edit_employee_view", emp_id=emp_id))

        if update_employee(emp):
            flash("Employee updated successfully!", "success")
        else:
            flash("Failed to update employee.", "error")
        return redirect(url_for("list_employees"))

    return render_template(
        "employee_edit.html",
        employee=emp,
        is_admin=session.get("is_admin", False),
        user_name=session.get("user_name", "User"),
    )


@app.route("/employees/<int:emp_id>/delete", methods=["POST"])
@admin_required
def delete_employee_view(emp_id: int):
    if delete_employee(emp_id):
        flash("Employee deleted.", "success")
    else:
        flash("Failed to delete employee.", "error")
    return redirect(url_for("list_employees"))


# ---------- Dashboard ---------- #

@app.route("/dashboard")
@admin_required
def dashboard():
    employees = get_all_employees()
    total = len(employees)
    total_salary = sum(e.salary for e in employees) if employees else 0
    avg_salary = total_salary / total if total else 0
    max_salary = max((e.salary for e in employees), default=0)
    min_salary = min((e.salary for e in employees), default=0)

    designation_counts = Counter(e.designation for e in employees)

    salary_buckets = {"< 3L": 0, "3L - 6L": 0, "6L - 10L": 0, "> 10L": 0}
    for e in employees:
        s = e.salary
        if s < 300000:
            salary_buckets["< 3L"] += 1
        elif s < 600000:
            salary_buckets["3L - 6L"] += 1
        elif s < 1000000:
            salary_buckets["6L - 10L"] += 1
        else:
            salary_buckets["> 10L"] += 1

    return render_template(
        "dashboard.html",
        total=total,
        total_salary=total_salary,
        avg_salary=avg_salary,
        max_salary=max_salary,
        min_salary=min_salary,
        designation_labels=list(designation_counts.keys()),
        designation_values=list(designation_counts.values()),
        bucket_labels=list(salary_buckets.keys()),
        bucket_values=list(salary_buckets.values()),
        is_admin=session.get("is_admin", False),
        user_name=session.get("user_name", "User"),
    )


if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
