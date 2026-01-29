from flask import Flask, render_template, request, redirect, url_for, send_file, session
from openpyxl import Workbook
import csv 
import os

app = Flask(__name__)
app.secret_key = "ma_super_cle_secrete_1234"  # يمكنك وضع أي قيمة طويلة وسرية
EMPLOYEE_FILE = 'employees.csv'

# صفحة عرض جميع الموظفين
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
      session['is_admin'] = True  # حفظ نوع المستخدم في الجلسة
     return render_template('verify_account.html')
        else:
            message = "كلمة المرور خاطئة"
    return render_template('admin_login.html', message=message) 

# تسجيل دخول المستخدم العادي
@app.route('/user', methods=['GET', 'POST']) 
def user():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
       if password == 'de@@55tggt':
    session['is_admin'] = False  # حفظ نوع المستخدم في الجلسة
    return render_template('verify_account.html')
 
        else:
            message = "كلمة المرور خاطئة"
    return render_template('admin_login.html', message=message)

# التحقق من CCP
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    ccp = None
    is_admin = request.args.get('is_admin', 'False') == 'True'

    if request.method == 'POST':
        ccp = request.form.get('ccp')
    elif request.method == 'GET':
        ccp = request.args.get('ccp')

    if not ccp:
        return render_template('verify_account.html', is_admin=is_admin)

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row, is_admin=is_admin)

    return render_template('verify_account.html', message="رقم الحساب غير موجود", is_admin=is_admin)

# صفحة الملف الشخصي
@app.route('/success')
def success():
    ccp = request.args.get('ccp')
    is_admin = request.args.get('is_admin', 'False') == 'True'

    if not ccp:
        return redirect(url_for('verify_account', is_admin=is_admin))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row, is_admin=is_admin)

    return render_template('verify_account.html', message="رقم الحساب غير موجود", is_admin=is_admin)

# تعديل بيانات الموظف (الإدمن)
@app.route('/edit', methods=['GET', 'POST'])
def edit_employee():
    ccp = request.args.get('ccp')
    is_admin = True
    if not ccp:
        return redirect(url_for('verify_account', is_admin=is_admin))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                emp_data = row
                return render_template('edit_employee.html', employee=emp_data, is_admin=is_admin)

    return render_template('verify_account.html', message="الموظف غير موجود", is_admin=is_admin)

# تعديل بيانات الموظف (المستخدم)
@app.route('/user/edit', methods=['GET', 'POST'])
def edit_employee_user():
    ccp = request.args.get('ccp')
    is_admin = False
    if not ccp:
        return redirect(url_for('verify_account', is_admin=is_admin))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                emp_data = row
                return render_template('edit_employee.html', employee=emp_data, is_admin=is_admin)

    return render_template('verify_account.html', message="الموظف غير موجود", is_admin=is_admin)

# حفظ التعديلات
@app.route('/edit_employee_save', methods=['POST'])
def edit_employee_save():
    ccp = request.args.get('ccp')
    is_admin = request.args.get('is_admin', 'False') == 'True'

    if not ccp:
        return redirect(url_for('verify_account', is_admin=is_admin))

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

    return redirect(url_for('success', ccp=ccp, is_admin=is_admin))

# تنزيل الموظفين كملف Excel
@app.route('/download_employees')
def download_employees():
    csv_file = 'employees.csv'
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
