# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..db import get_db_connection

student_bp = Blueprint('student', __name__, template_folder='../templates')

# ----------------------------
# List all students/postdocs
# ----------------------------
@student_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('students.html', students=students)

# ----------------------------
# Add new student/postdoc
# ----------------------------
@student_bp.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    role = request.form['role']
    fte = float(request.form['fte'])
    salary = float(request.form['salary'])
    tuition = float(request.form.get('tuition', 0))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, role, fte, salary, tuition) VALUES (%s,%s,%s,%s,%s)",
        (name, role, fte, salary, tuition)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash(f"{role} added successfully!")
    return redirect(url_for('student.index'))

# ----------------------------
# Edit student/postdoc
# ----------------------------
@student_bp.route('/edit/<int:student_id>', methods=['GET','POST'])
def edit_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        fte = float(request.form['fte'])
        salary = float(request.form['salary'])
        tuition = float(request.form.get('tuition', 0))

        cursor.execute(
            "UPDATE students SET name=%s, role=%s, fte=%s, salary=%s, tuition=%s WHERE student_id=%s",
            (name, role, fte, salary, tuition, student_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"{role} updated successfully!")
        return redirect(url_for('student.index'))

    cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('student_form.html', student=student)

# ----------------------------
# Delete student/postdoc
# ----------------------------
@student_bp.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Student/Postdoc deleted successfully!")
    return redirect(url_for('student.index'))


