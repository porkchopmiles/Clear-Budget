# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, session
from ..db import get_db_connection
import pandas as pd
from flask import send_file
import io

# Create Blueprint
budget_bp = Blueprint('budget', __name__, template_folder='../templates')

# ----------------------------
# Budget Home (redirect to step1)
# ----------------------------
@budget_bp.route('/')
def budget_index():
    # Redirect to Step 1
    return redirect(url_for('budget.step1'))

# ----------------------------
# Step 1: Select PI and Budget Years
# ----------------------------
@budget_bp.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        # Save PI and budget years in session
        session['pi_id'] = request.form['pi_id']
        session['start_year'] = request.form['start_year']
        session['end_year'] = request.form['end_year']
        return redirect(url_for('budget.step2'))

    # GET: fetch all faculty to display in dropdown
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT faculty_id, name FROM faculty")
    pis = cursor.fetchall()
    cursor.close()
    conn.close()

    # Render Step 1 template
    return render_template('budget_step1.html', pis=pis)

# ----------------------------
# Step 2: Add Students / Postdocs
# ----------------------------
@budget_bp.route('/step2', methods=['GET', 'POST'])
def step2():
    if 'budget_personnel' not in session:
        session['budget_personnel'] = []

    if request.method == 'POST':
        #--- General Fields --
        name = request.form['name']
        ptype = request.form['type']
        fte = float(request.form['fte'])
        salary = float(request.form['salary'])
        fringe = float(request.form['fringe'])
        
        #---  Tuition fields ---
        residency = request.form.get('residency', 'In-State')
        semester = request.form.get('semester', 'Fall')
        start_year = int(session.get('start_year', 2026))
        
        # Validate student FTE <= 50%
        if ptype == 'Student' and fte > 50:
            fte = 50
            
        # Calculate tuition
        tuition_amount = 0
        if ptype == 'Student':
            tuition_amount, projected_increase = get_tuition(residency, semester, start_year)

        # Add personnel to session
        personnel = {
            'name': name,
            'type': ptype,
            'fte': float(fte),
            'salary': float(salary),
            'fringe': float(fringe),
            'residency': residency,
            'semester': semester,
            'tuition': tuition_amount
        }
        session['budget_personnel'].append(personnel)
        session.modified = True  # Tell Flask session changed

        return redirect(url_for('budget.step2'))

    return render_template('budget_step2.html')


# Step 3: Review Budget
@budget_bp.route('/step3')
def step3():
    personnel = session.get('budget_personnel', [])

    total_salary = 0.0
    total_fringe = 0.0

    # Calculate totals in Python
    for p in personnel:
       salary = float(p.get('salary', 0))
       fringe = float(p.get('fringe', 0))
       total_salary += salary
       total_fringe += salary * fringe / 100

    grand_total = total_salary + total_fringe

    return render_template(
       'budget_step3.html',
       personnel=personnel,
       total_salary=total_salary,
       total_fringe=total_fringe,
       grand_total=grand_total
    )


@budget_bp.route('/export')
def export_excel():
    
    personnel = session.get('budget_personnel', [])

    if not personnel:
        return "No personnel to export."

    # Create DataFrame
    df = pd.DataFrame(personnel)
    # Calculate fringe as separate column
    df['Fringe ($)'] = df['salary'] * df['fringe'] / 100
    df['Total ($)'] = df['salary'] + df['Fringe ($)']
    df.rename(columns={
        'name': 'Name',
        'type': 'Type',
        'fte': 'FTE (%)',
        'salary': 'Salary ($)',
        'fringe': 'Fringe Rate (%)'
    }, inplace=True)

    # Calculate totals
    totals = {
        'Name': 'TOTAL',
        'Salary ($)': df['Salary ($)'].sum(),
        'Fringe ($)': df['Fringe ($)'].sum(),
        'Total ($)': df['Total ($)'].sum()
    }

    # Create a BytesIO buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Personnel')
        # Add totals row at the bottom
        workbook  = writer.book
        worksheet = writer.sheets['Personnel']
        last_row = len(df) + 1
        worksheet.write(last_row, 0, totals['Name'])
        worksheet.write(last_row, 3, totals['Salary ($)'])
        worksheet.write(last_row, 4, totals['Fringe ($)'])
        worksheet.write(last_row, 5, totals['Total ($)'])

    output.seek(0)

    return send_file(output,
                     download_name='budget.xlsx',
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def get_tuition(student_type, semester, year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT tuition_amount, projected_increase FROM tuition "
        "WHERE student_type=%s AND semester=%s AND year=%s",
        (student_type, semester, year)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result['tuition_amount'], result['projected_increase']
    else:
        return 0, 0  # default if not found
