from typing import List, Optional
from db import get_connection
from models import Employee

def add_employee(emp: Employee) -> bool:
    sql = "INSERT INTO emp (id, firstName, lastName, salary, designation) VALUES (?, ?, ?, ?, ?)"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, (emp.id, emp.first_name, emp.last_name, emp.salary, emp.designation))
        conn.commit()
        return True
    except Exception as e:
        print("Error adding employee:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def update_employee(emp: Employee) -> bool:
    sql = "UPDATE emp SET firstName = ?, lastName = ?, salary = ?, designation = ? WHERE id = ?"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, (emp.first_name, emp.last_name, emp.salary, emp.designation, emp.id))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print("Error updating employee:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_employee(emp_id: int) -> bool:
    sql = "DELETE FROM emp WHERE id = ?"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, (emp_id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print("Error deleting employee:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def get_employee_by_id(emp_id: int) -> Optional[Employee]:
    sql = "SELECT id, firstName, lastName, salary, designation FROM emp WHERE id = ?"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, (emp_id,))
        row = cur.fetchone()
        if row:
            return Employee(
                id=row[0],
                first_name=row[1],
                last_name=row[2],
                salary=row[3],
                designation=row[4],
            )
        return None
    finally:
        conn.close()

def get_all_employees() -> List[Employee]:
    sql = "SELECT id, firstName, lastName, salary, designation FROM emp"
    conn = get_connection()
    employees: List[Employee] = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            employees.append(
                Employee(
                    id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    salary=row[3],
                    designation=row[4],
                )
            )
        return employees
    finally:
        conn.close()
