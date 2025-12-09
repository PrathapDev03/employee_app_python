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


# --------- Helpers / Decorators --------- #

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)
    return wrapper

def access_required(view_func):
    """Visitor or admin must be logged in."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("role") not in ("visitor", "admin"):
            return redirect(url_for("visit"))
        return view_func(*args, **kwargs)
    return wrapper

def is_admin():
    return session.get("role") == "admin"


# --------- Visitor: Gate Page --------- #

@app.route("/")
def index():
    if is_admin():
        return redirect(url_for("dashboard"))
    if session.get("role") == "visitor":
        return redirect(url_for("employees"))
    return redirect(url_for("visit"))

@app.route("/visit", methods=["GET", "POST"])
def visit():
    # Visitor registration page
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()

        if not name or not email or not phone:
            flash("Please fill all fields.", "error")
            return redirect(url_for("visit"))

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO visitors (name, email, phone) VALUES (?, ?, ?)",
                (name, email, phone),
            )
            conn.commit()
        finally:
            conn.close()

        # create visitor session
        session["role"] = "visitor"
        session["visitor_name"] = name

        # redirect to "dashboard" = employees list (read-only)
        return redirect(url_for("employees"))

    return render_template("visit.html")


# --------- Admin Login / Logout --------- #

ADMIN_EMAIL = "prathap03.p@gmail.com"
ADMIN_PASSWORD = "root121@"

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if email == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            session.clear()
            session["role"] = "admin"
            session["admin_email"] = ADMIN_EMAIL
            session["admin_name"] = "Admin"
            flash("Logged in as admin.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid admin credentials.", "error")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("visit"))


# --------- Employee Pages --------- #

@app.route("/employees")
@access_required
def employees():
    employees = get_all_employees()
    role = session.get("role")
    name = session.get("admin_name") if is_admin() else session.get("visitor_name", "Visitor")

    return render_template(
        "employee_list.html",
        employees=employees,
        is_admin=is_admin(),
        user_name=name,
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
        return redirect(url_for("employees"))

    return render_template(
        "employee_add.html",
        is_admin=True,
        user_name=session.get("admin_name", "Admin"),
    )

@app.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_employee_view(emp_id: int):
    emp = get_employee_by_id(emp_id)
    if not emp:
        flash("Employee not found.", "error")
        return redirect(url_for("employees"))

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
        return redirect(url_for("employees"))

    return render_template(
        "employee_edit.html",
        employee=emp,
        is_admin=True,
        user_name=session.get("admin_name", "Admin"),
    )

@app.route("/employees/<int:emp_id>/delete", methods=["POST"])
@admin_required
def delete_employee_view(emp_id: int):
    if delete_employee(emp_id):
        flash("Employee deleted.", "success")
    else:
        flash("Failed to delete employee.", "error")
    return redirect(url_for("employees"))


# --------- Admin Dashboard + Visitors List --------- #

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
        is_admin=True,
        user_name=session.get("admin_name", "Admin"),
    )

@app.route("/admin/visitors")
@admin_required
def admin_visitors():
    conn = get_connection()
    visitors = []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name, email, phone, created_at FROM visitors ORDER BY id DESC"
        )
        rows = cur.fetchall()
        for row in rows:
            visitors.append(
                {
                    "name": row[0],
                    "email": row[1],
                    "phone": row[2],
                    "created_at": row[3],
                }
            )
    finally:
        conn.close()

    return render_template(
        "admin_visitors.html",
        visitors=visitors,
        is_admin=True,
        user_name=session.get("admin_name", "Admin"),
    )


if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
