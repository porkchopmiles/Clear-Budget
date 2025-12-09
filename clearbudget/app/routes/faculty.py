# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..db import get_db_connection

faculty_bp = Blueprint('faculty', __name__, template_folder='../templates')

# gets all faculty

@faculty_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM faculty")
    faculty_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('faculty.html', faculty=faculty_list)


# faculty crud
@faculty_bp.route('/add', methods=['POST'])
def add_faculty():
    name = request.form['name']
    title = request.form['title']
    annual_salary = float(request.form['annual_salary'])
    fringe_rate = float(request.form['fringe_rate'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faculty (name, title, annual_salary, fringe_rate) VALUES (%s, %s, %s, %s)",
        (name, title, annual_salary, fringe_rate)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('faculty.index'))

@faculty_bp.route('/edit/<int:faculty_id>', methods=['GET', 'POST'])
def edit_faculty(faculty_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        annual_salary = float(request.form['annual_salary'])
        fringe_rate = float(request.form['fringe_rate'])
        cursor.execute(
            "UPDATE faculty SET name=%s, title=%s, annual_salary=%s, fringe_rate=%s WHERE faculty_id=%s",
            (name, title, annual_salary, fringe_rate, faculty_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Faculty updated successfully!")
        return redirect(url_for('faculty.index'))
    
    else:
        cursor.execute("SELECT * FROM faculty WHERE faculty_id=%s", (faculty_id,))
        faculty = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('faculty_form.html', action='Edit', faculty=faculty)
    
@faculty_bp.route('/delete/<int:faculty_id>', methods=['POST'])
def delete_faculty(faculty_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faculty WHERE faculty_id=%s", (faculty_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Faculty deleted successfully!")
    return redirect(url_for('faculty.index'))
