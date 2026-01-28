from flask import Flask, render_template, request, redirect, url_for, send_file
from openpyxl import Workbook
import csv 
import os

app = Flask(__name__)

EMPLOYEE_FILE = 'employees.csv'

# عرض جميع الموظفين بعد التعديل
@app.route('/view_employees')
def view_employees():
    employees = []
    try:
        with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                employees.append(row)
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

    return render_template('view_employees.html', employees=employees)

# تسجيل دخول الإدمن
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'de@tggt':
            return redirect(url_for('verify_account', role='admin'))
        else:
            message = "كلمة المرور خاطئة"
    return render_template('admin_login.html', message=message)

# تسجيل دخول المستخدم العادي
@app.route('/user', methods=['GET', 'POST'])
def user_login():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'de@@55tggt':
            return redirect(url_for('verify_account', role='user'))
        else:
            message = "كلمة المرور خاطئة"
    return render_template('admin_login.html', message=message)

# صفحة التحقق من CCP
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    ccp = request.form.get('ccp') or request.args.get('ccp')
    role = request.args.get('role', 'admin')  # تحديد الدور
    if not ccp:
        return render_template('verify_account.html', role=role)

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row, role=role)

    return render_template('verify_account.html', message="رقم الحساب غير موجود", role=role)

# صفحة الملف الشخصي للموظف
@app.route('/success')
def success():
    ccp = request.args.get('ccp')
    role = request.args.get('role', 'admin')
    if not ccp:
        return redirect(url_for('verify_account', role=role))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row, role=role)
    return render_template('verify_account.html', message="رقم الحساب غير موجود", role=role)

# صفحة تعديل بيانات الموظف
@app.route('/edit')
def edit_employee():
    ccp = request.args.get('ccp')
    role = request.args.get('role', 'admin')  # الدور لتحديد ظهور زر الطباعة
    if not ccp:
        return redirect(url_for('verify_account', role=role))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('edit_employee.html', employee=row, role=role)
    return render_template('verify_account.html', message="الموظف غير موجود", role=role)

# حفظ التعديلات على employees.csv
@app.route('/edit_employee_save', methods=['POST'])
def edit_employee_save():
    ccp = request.args.get('ccp')
    role = request.args.get('role', 'admin')
    if not ccp:
        return redirect(url_for('verify_account', role=role))

    updated_data = {
        'CCP': request.form.get('CCP', ''),
        'NIN': request.form.get('NIN', ''),
        'last_name': request.form.get('last_name', ''),
        'first_name': request.form.get('first_name', ''),
        'birth_date': request.form.get('birth_date', ''),
        'poste_travail': request.form.get('poste_travail', ''),
        'categorie': request.form.get('categorie', ''),
        'daira': request.form.get('daira', ''),
        'commune': request.form.get('commune', ''),
        'ecole': request.form.get('ecole', ''),
        'TEL': request.form.get('TEL', '')
    }

    employees = []
    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames
        for row in reader:
            if row['CCP'] == ccp:
                for key in updated_data:
                    if key in row:
                        row[key] = updated_data[key]
            employees.append(row)

    with open(EMPLOYEE_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(employees)

    return redirect(url_for('success', ccp=ccp, role=role))

# تنزيل ملف Excel
@app.route('/download_employees')
def download_employees():
    csv_file = EMPLOYEE_FILE
    excel_file = 'employees.xlsx'

    wb = Workbook()
    ws = wb.active
    ws.title = "Employees"

    with open(csv_file, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            ws.append(row)

    wb.save(excel_file)

    return send_file(
        excel_file,
        as_attachment=True,
        download_name="employees.xlsx"
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
