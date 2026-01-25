from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

# -------------------------------
# صفحة تسجيل الدخول للإدمن
# -------------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    message = ""
    if request.method == 'POST':
        password = request.form['password']
        if password == "de@tggt":
            return render_template('verify_account.html')
        else:
            message = "كلمة المرور غير صحيحة."
    return render_template('admin_login.html', message=message)

# -------------------------------
# صفحة التحقق من رقم الحساب (CCP)
# -------------------------------
@app.route('/verify_account', methods=['POST'])
def verify_account():
    ccp = request.form['ccp']
    try:
        with open('employees.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('success.html', employee=row)
    except FileNotFoundError:
        message = "ملف الموظفين غير موجود على السيرفر."
        return render_template('verify_account.html', message=message)

    message = "رقم الحساب غير صحيح، حاول مرة أخرى."
    return render_template('verify_account.html', message=message)

# -------------------------------
# الصفحة الرئيسية
# -------------------------------
@app.route('/')
def index():
    return render_template('admin_login.html')

# -------------------------------
# صفحة تعديل بيانات الموظف
# -------------------------------
@app.route('/edit', methods=['GET', 'POST'])
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود في الرابط", 400

    try:
        with open('employees.csv', newline='', encoding='utf-8-sig') as f:
            reader = list(csv.DictReader(f, delimiter=';'))
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

    employee = None
    for row in reader:
        if row['CCP'] == ccp:
            employee = row
            break
    if not employee:
        return "الموظف غير موجود", 404

    if request.method == 'POST':
        # استلام القيم الجديدة من الفورم
        employee['NIN'] = request.form.get('NIN', '').strip()
        employee['poste_travail'] = request.form.get('poste_travail', '').strip()
        employee['categorie'] = request.form.get('categorie', '').strip()
        employee['daira'] = request.form.get('daira', '').strip()
        employee['commune'] = request.form.get('commune', '').strip()
        employee['ecole'] = request.form.get('ecole', '').strip()
        employee['TEL'] = request.form.get('TEL', '').strip()
        employee['employee_id'] = request.form.get('employee_id', '').strip()
        employee['last_name'] = request.form.get('last_name', '').strip()
        employee['first_name'] = request.form.get('first_name', '').strip()
        employee['birth_date'] = request.form.get('birth_date', '').strip()

        # كتابة التعديلات في CSV
        fieldnames = reader[0].keys()
        with open('employees.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for r in reader:
                writer.writerow(r)

        return redirect(url_for('edit_employee', ccp=ccp))

    return render_template('edit_employee.html', employee=employee)
    

# -------------------------------
# تشغيل التطبيق
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
