from flask import Flask, render_template, request, redirect, url_for, send_file, session
from openpyxl import Workbook
import csv 
import os

app = Flask(__name__)
app.secret_key = "ma_super_cle_secrete_1234"
EMPLOYEE_FILE = 'employees.csv'

# صفحة عرض جميع الموظفين مع الترتيب
@app.route('/view_employees')
def view_employees():
    sort_by = request.args.get('sort_by')  # المتغير لتحديد نوع الترتيب
    employees = []

    try:
        with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                employees.append(row)
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

    # الترتيب حسب الاختيار
    if sort_by in ['CCP', 'last_name', 'ecole']:
        employees.sort(key=lambda x: x.get(sort_by) or '')

    return render_template('view_employees.html', employees=employees, sort_by=sort_by)

# باقي الدوال كما هي بدون تغيير ...
# تسجيل دخول الإدمن
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'de@tggt':
            session['is_admin'] = True
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
            session['is_admin'] = False
            return render_template('verify_account.html')
        else:
            message = "كلمة المرور خاطئة"
    return render_template('admin_login.html', message=message)

# التحقق من CCP
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    ccp = None
    if request.method == 'POST':
        ccp = request.form.get('ccp')
    elif request.method == 'GET':
        ccp = request.args.get('ccp')

    if not ccp:
        return render_template('verify_account.html', is_admin=session.get('is_admin', False))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row, is_admin=session.get('is_admin', False))

    return render_template('verify_account.html', message="رقم الحساب غير موجود", is_admin=session.get('is_admin', False))

# صفحة الملف الشخصي
@app.route('/success')
def success():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('verify_account'))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row, is_admin=session.get('is_admin', False))

    return render_template('verify_account.html', message="رقم الحساب غير موجود", is_admin=session.get('is_admin', False))

# بقية الدوال (edit, edit_employee_save, download_employees) كما هي
# ...
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
