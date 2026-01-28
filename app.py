from flask import Flask, render_template, request, redirect, url_for, send_file
from openpyxl import Workbook
import csv 
import os

app = Flask(__name__)

EMPLOYEE_FILE = 'employees.csv'

# صفحة عرض جميع الموظفين بعد التعديل (للمسؤول فقط)
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

# صفحة تسجيل دخول الإدمن
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'de@tggt':
            return render_template('verify_account.html')
        else:
            message = "كلمة المرور خاطئة"
    return render_template('admin_login.html', message=message)

# صفحة تسجيل دخول المستخدم العادي
@app.route('/user', methods=['GET', 'POST'])
def user_login():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'de@@55tggt':
            # بعد تسجيل الدخول للمستخدم، نعرض الفورم مباشرة بدون زر طباعة القائمة
            return redirect(url_for('edit_employee_user'))
        else:
            message = "كلمة المرور خاطئة"
    return render_template('user_login.html', message=message)

# صفحة تعديل بيانات الموظف للمسؤول (مع زر الطباعة)
@app.route('/edit')
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('verify_account'))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('edit_employee.html', employee=row)
    return render_template('verify_account.html', message="الموظف غير موجود")

# صفحة تعديل بيانات الموظف للمستخدم العادي (بدون زر الطباعة)
@app.route('/edit_user', methods=['GET'])
def edit_employee_user():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('user_login'))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('edit_employee_user.html', employee=row)
    return render_template('user_login.html', message="الموظف غير موجود")

# حفظ التعديلات على employees.csv
@app.route('/edit_employee_save', methods=['POST'])
def edit_employee_save():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('verify_account'))

    # قراءة البيانات من الفورم
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

    # قراءة كل الموظفين وتعديل الموظف المستهدف
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

    # كتابة البيانات المحدثة مرة أخرى في الملف
    with open(EMPLOYEE_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(employees)

    # بعد الحفظ، العودة إلى صفحة الملف الشخصي
    return redirect(url_for('success', ccp=ccp))

# صفحة الملف الشخصي للموظف
@app.route('/success')
def success():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('verify_account'))

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row)
    return render_template('verify_account.html', message="رقم الحساب غير موجود")

# صفحة التحقق من CCP
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    ccp = None
    if request.method == 'POST':
        ccp = request.form.get('ccp')
    elif request.method == 'GET':
        ccp = request.args.get('ccp')

    if not ccp:
        return render_template('verify_account.html')

    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row)

    return render_template('verify_account.html', message="رقم الحساب غير موجود")

# تحميل الملف Excel
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
