from flask import Flask, render_template, request, redirect, url_for, flash
from dao import add_employee, update_employee, delete_employee, get_employee_by_id, get_all_employees
from models import Employee
from db import init_db

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # for flash messages

# Initialize DB (run once at startup – optional)
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print("DB init error:", e)

@app.route("/")
def index():
    return redirect(url_for("list_employees"))

@app.route("/employees")
def list_employees():
    employees = get_all_employees()
    return render_template("employee_list.html", employees=employees)

@app.route("/employees/add", methods=["GET", "POST"])
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

    return render_template("employee_add.html")

@app.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
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

    return render_template("employee_edit.html", employee=emp)

@app.route("/employees/<int:emp_id>/delete", methods=["POST"])
def delete_employee_view(emp_id: int):
    if delete_employee(emp_id):
        flash("Employee deleted.", "success")
    else:
        flash("Failed to delete employee.", "error")
    return redirect(url_for("list_employees"))

if __name__ == "__main__":
    app.run(debug=True)








import os

if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
