from flask import Flask, render_template, request, redirect, url_for, send_file
from openpyxl import Workbook
import csv
import os

app = Flask(__name__)

EMPLOYEE_FILE = 'employees.csv'

# =================================
# عرض جميع الموظفين (الإدمن فقط)
# =================================
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

# =================================
# تسجيل دخول الإدمن
# =================================
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

# =================================
# تسجيل دخول المستخدم العادي
# =================================
@app.route('/user', methods=['GET', 'POST'])
def user_login():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'de@@55tggt':
            return redirect(url_for('edit_employee_user'))
        else:
            message = "كلمة المرور خاطئة"
    return render_template('user_login.html', message=message)

# =================================
# صفحة تعديل بيانات الموظف (الإدمن)
# =================================
@app.route('/edit')
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('admin'))
    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('edit_employee.html', employee=row)
    return redirect(url_for('admin'))

# =================================
# صفحة تعديل بيانات الموظف (المستخدم العادي)
# =================================
@app.route('/edit_user')
def edit_employee_user():
    ccp = request.args.get('ccp')
    if not ccp:
        # إذا لم يحدد CCP، نأخذ أول موظف (يمكن تعديله حسب حاجتك)
        with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            first_row = next(reader, None)
            if first_row:
                ccp = first_row['CCP']
            else:
                return "لا يوجد موظفون في الملف.", 500
    with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('edit_employee_user.html', employee=row)
    return "الموظف غير موجود", 404

# =================================
# حفظ التعديلات
# =================================
@app.route('/edit_employee_save', methods=['POST'])
def edit_employee_save():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('admin'))

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

    return redirect(url_for('edit_employee_user', ccp=ccp))

# =================================
# تنزيل الموظفين كملف Excel
# =================================
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
