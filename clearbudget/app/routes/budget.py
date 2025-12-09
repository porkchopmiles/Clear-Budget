# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..db import get_db_connection
import pandas as pd
from flask import send_file
import io
from uuid import uuid4


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
    # Get current personnel from session
    selected_personnel = session.get('budget_personnel', [])
    travel_list = session.get('budget_travel', [])
    subawards = session.get('budget_subawards', [])

    if request.method == 'POST':

        # ---------------- Add new personnel ----------------
        if 'add_student' in request.form:
            name = request.form['name']
            role = request.form['role']
            fte = float(request.form['fte'])
            annual_salary = float(request.form['salary'])
            fringe_rate = float(request.form['fringe'])
            tuition = float(request.form.get('tuition', 0))
            
            #---  Tuition fields ---
            residency = request.form.get('residency', 'In-State')
            semester = request.form.get('semester', 'Fall')
            start_year = int(session.get('start_year', 2026))
            
            # Validate student FTE <= 50%
            if role == 'Student' and fte > 50:
                fte = 50
                
            # Calculate tuition
            tuition_amount = 0
            if role == 'Student':
                tuition_amount, projected_increase = get_tuition(residency, semester, start_year)
            
            selected_personnel.append({
                'id': str(uuid4()),  # unique ID
                'name': name,
                'role': role,
                'fte': fte,
                'salary': annual_salary,
                'fringe': fringe_rate,
                'residency': residency,
                'semester': semester,
                'tuition': tuition
            })
            
            session['budget_personnel'] = selected_personnel
            flash(f"{role} added to budget.")
            return redirect(url_for('budget.step2'))

        # ---------------- Delete individual personnel ----------------
        delete_id = request.form.get('delete_id')
        if delete_id:
            selected_personnel = [p for p in selected_personnel if p.get('id') != delete_id]
            session['budget_personnel'] = selected_personnel
            flash("Personnel removed from budget.")
            return redirect(url_for('budget.step2'))


        # ---------------- Delete All ----------------
        if 'delete_all' in request.form:
            selected_personnel = []
            session['budget_personnel'] = selected_personnel
            flash("All personnel removed from budget.")
            return redirect(url_for('budget.step2'))
        
        #----------------Travel-----------------
        if 'add_travel' in request.form:

           profile_id = request.form.get('travel_profile')
           days = int(request.form.get('travel_days'))

           db = get_db_connection()

           # Fetch travel profile from DB
           db = get_db_connection()
           cursor = db.cursor(dictionary=True)  # dictionary=True lets you access columns by name

           cursor.execute(
                "SELECT * FROM travel_profiles WHERE profile_id = %s", (profile_id,)
           )
           profile = cursor.fetchone()
           cursor.close()


           if not profile:
               flash("Invalid travel profile.", "error")
               return redirect(url_for('budget.step2'))

           travel_list.append({
               "profile_id": profile['profile_id'],
               "name": profile["name"],
               "type": profile["type"],
               "days": int(days),
               "airfare": float(profile["airfare"]),
               "per_diem": float(profile["per_diem"]),
               "lodging": float(profile["lodging_cap"]),
               "total": float(profile['airfare']) + float(profile['per_diem']) * days +float(profile['lodging_cap']) * days
           })

           session['budget_travel'] = travel_list
           flash("Travel added.")
           
           return redirect(url_for('budget.step2'))
       
        #----------- Delete Travel---------------
        if 'delete_travel' in request.form:

            index = int(request.form['delete_travel'])
            if 0 <= index < len(travel_list):
                travel_list.pop(index)

            session['budget_travel'] = travel_list
            flash("Travel entry removed.")
            return redirect(url_for('budget.step2'))
        
        #--------------Subawards----------
        if 'add_subaward' in request.form:
            institution = request.form['institution']
            fa_rate = float(request.form.get('fa_rate', 40))
            subaward = {
                'id': str(uuid4()),
                'institution': institution,
                'personnel': [],
                'travel': [],
                'fa_rate': fa_rate
            }
            subawards.append(subaward)
            session['budget_subawards'] = subawards
            flash(f"Subaward added for {institution}.")
            return redirect(url_for('budget.step2'))
        #---- Delete ----
        delete_subaward_id = request.form.get('delete_subaward')
        if delete_subaward_id:
            subawards = [s for s in subawards if s.get('id') != delete_subaward_id]
            session['budget_subawards'] = subawards
            flash("Subaward removed.")
            return redirect(url_for('budget.step2'))
        
    
        
    
    #render all
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
                   SELECT profile_id, name, type, airfare, per_diem, lodging_cap 
                   FROM travel_profiles
                   """)
    travel_profiles = cursor.fetchall()
    cursor.close()
    
    # fix type error
    for t in travel_list:
        t['airfare'] = float(t['airfare'])
        t['per_diem'] = float(t['per_diem'])
        t['lodging'] = float(t['lodging'])
        t['total'] = float(t['total'])

    return render_template(
        'budget_step2.html',         
        selected_personnel=selected_personnel,
        travel_list=travel_list,
        travel_profiles=travel_profiles,
        subawards=subawards
    )

@budget_bp.route('/step2/subaward/<subaward_id>/edit', methods=['GET', 'POST'])
def edit_subaward(subaward_id):
    # Get subawards from session
    subawards = session.get('budget_subawards', [])
    subaward = next((s for s in subawards if s['id'] == subaward_id), None)

    if not subaward:
        flash("Subaward not found.", "error")
        return redirect(url_for('budget.step2'))

    if request.method == 'POST':
        # Update subaward info
        subaward['institution'] = request.form.get('institution', subaward['institution'])
        subaward['fa_rate'] = float(request.form.get('fa_rate', subaward['fa_rate']))

        # Save back to session
        session['budget_subawards'] = subawards
        flash(f"Subaward for {subaward['institution']} updated.")
        return redirect(url_for('budget.step2'))

    return render_template('edit_subaward.html', subaward=subaward)

# Step 3: Review Budget
@budget_bp.route('/step3')
def step3():
    personnel = session.get('budget_personnel', [])
    travel_list = session.get('budget_travel', [])
    subawards = session.get('budget_subawards', [])

    # --- Prime Budget Totals ---
    total_salary = sum(float(p.get('salary', 0)) for p in personnel)
    total_fringe = sum(float(p.get('salary', 0)) * float(p.get('fringe', 0))/100 for p in personnel)
    total_tuition = sum(float(p.get('tuition',0)) for p in personnel)
    total_travel = sum(float(t.get('total',0)) for t in travel_list)
    fa_rate = float(session.get('fa_rate',10))  # default 10%


    direct_costs = total_salary + total_fringe + total_tuition + total_travel
    fa_cost = direct_costs * fa_rate / 100
    prime_total = direct_costs + fa_cost
    
    # Subawards
    subaward_totals = []
    for s in subawards:
        s_personnel = s.get('personnel', [])
        s_travel = s.get('travel', [])
        s_salary = sum(float(p.get('salary',0)) for p in s_personnel)
        s_fringe = sum(float(p.get('salary',0))*float(p.get('fringe',0))/100 for p in s_personnel)
        s_travel_total = sum(float(t.get('total',0)) for t in s_travel)
        s_direct = s_salary + s_fringe + s_travel_total
        s_fa = s_direct * s.get('fa_rate',40)/100
        s_total = s_direct + s_fa
        subaward_totals.append({
            'institution': s['institution'],
            'direct': s_direct,
            'fa': s_fa,
            'total': s_total
        })
    
    # Grand total includes prime + all subawards
    grand_total = prime_total + sum(s['total'] for s in subaward_totals)
    

    return render_template(
       'budget_step3.html',
       personnel=personnel,
       travel_list=travel_list,
       subaward_totals=subaward_totals,
       total_salary=total_salary,
       total_fringe=total_fringe,
       total_tuition=total_tuition,
       total_travel=total_travel,
       fa_rate=fa_rate,
       fa_cost=fa_cost,
       prime_total=prime_total,
       grand_total=grand_total
    )



@budget_bp.route('/delete_travel/<int:index>', methods=['POST'])
def delete_travel(index):
    travel_list = session.get("budget_travel", [])
    if 0 <= index < len(travel_list):
        travel_list.pop(index)
        session["budget_travel"] = travel_list
        session.modified = True

    return redirect(url_for('budget.step4'))



@budget_bp.route('/export')
def export_excel():
    
    personnel = session.get('budget_personnel', [])

    if not personnel:
        return "No personnel to export."

    # Create DataFrame
    df = pd.DataFrame(personnel)
    # Calculate fringe as separate column
    df['Fringe ($)'] = df['salary'] * df['fringe'] / 100
    df['Total ($)'] = df['salary'] + df['Fringe ($)'] + df['tuition']
    df.rename(columns={
        'name': 'Name',
        'type': 'Type',
        'fte': 'FTE (%)',
        'salary': 'Salary ($)',
        'fringe': 'Fringe Rate (%)',
        'tuition': 'Tuition ($)'
    }, inplace=True)

    # Calculate totals
    totals = {
        'Name': 'TOTAL',
        'Salary ($)': df['Salary ($)'].sum(),
        'Fringe ($)': df['Fringe ($)'].sum(),
        'Tuition ($)': df['Tuition ($)'].sum(),
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
        worksheet.write(last_row, 5, totals['Tuition ($)'])
        worksheet.write(last_row, 6, totals['Total ($)'])

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
    
    
def calculate_travel_total():
    travel_list = session.get("budget_travel", [])
    return sum(t['total'] for t in travel_list)
    
@budget_bp.route('/step2/clear', methods=['POST'])
def clear_personnel():
    session['budget_personnel'] = []
    flash("All personnel removed from the budget.")
    return redirect(url_for('budget.step2'))

