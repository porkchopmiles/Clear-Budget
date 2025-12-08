# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for
from ..db import get_db_connection

faculty_bp = Blueprint('faculty', __name__, template_folder='../templates')

@faculty_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM faculty")
    faculty_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('faculty.html', faculty=faculty_list)

@faculty_bp.route('/add', methods=['POST'])
def add_faculty():
    name = request.form['name']
    title = request.form['title']
    salary = request.form['salary']
    fringe = request.form['fringe']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faculty (name, title, annual_salary, fringe_rate) VALUES (%s, %s, %s, %s)",
        (name, title, salary, fringe)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('faculty.index'))
