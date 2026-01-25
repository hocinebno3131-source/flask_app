from flask import Flask, render_template, request, redirect, send_file, session, url_for
import csv
import os
from io import StringIO

app = Flask(__name__)
app.secret_key = "supersecretkey"  # ضروري لاستخدام session

# -------------------------------
# صفحة تسجيل الدخول للإدمن والمدير
# -------------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    message = ""
    if request.method == 'POST':
        password = request.form['password']
        if password == "de@tggt":
            session['role'] = 'manager'
            return redirect(url_for('verify_page'))
        elif password == "hocine":
            session['role'] = 'admin'
            return redirect(url_for('verify_page'))
        else:
            message = "كلمة المرور غير صحيحة."
    return render_template('admin_login.html', message=message)

# -------------------------------
# صفحة إدخال رقم الحساب (CCP)
# -------------------------------
@app.route('/verify_account', methods=['POST'])
def verify_account():
    ccp = request.form['ccp']
    try:
        with open('employees.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    role = session.get('role', 'manager')
                    return render_template('success.html', employee=row, role=role)
    except FileNotFoundError:
        message = "ملف الموظفين غير موجود على السيرفر."
        return render_template('verify_account.html', message=message)
    message = "رقم الحساب غير صحيح، حاول مرة أخرى."
    return render_template('verify_account.html', message=message)

# -------------------------------
# صفحة التحقق من رقم الحساب (الواجهة بعد تسجيل الدخول)
# -------------------------------
@app.route('/')
def verify_page():
    # تظهر نفس صفحة التحقق
    return render_template('verify_account.html')

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
            employee = None
            for row in reader:
                if row['CCP'] == ccp:
                    employee = row
                    break
            if employee is None:
                return "الموظف غير موجود", 404

            if request.method == 'POST':
                # تحديث البيانات حسب الحقول الموجودة في الفورم
                fields = ['NIN', 'last_name', 'first_name', 'birth_date', 
                          'poste_travail', 'categorie', 'daira', 'commune', 
                          'ecole', 'TEL', 'employee_id']
                for field in fields:
                    if field in request.form:
                        employee[field] = request.form[field]
                
                # حفظ التغييرات في employees.csv
                with open('employees.csv', 'w', newline='', encoding='utf-8-sig') as fw:
                    writer = csv.DictWriter(fw, fieldnames=reader[0].keys(), delimiter=';')
                    writer.writeheader()
                    for r in reader:
                        if r['CCP'] == ccp:
                            writer.writerow(employee)
                        else:
                            writer.writerow(r)
                
                return redirect(url_for('verify_account'))

            return render_template('edit_employee.html', employee=employee)

    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

# -------------------------------
# تحميل ملف employees.csv (للأدمن فقط)
# -------------------------------
@app.route('/download')
def download_file():
    role = session.get('role', None)
    if role != 'admin':
        return "غير مصرح لك بتحميل الملف", 403

    try:
        return send_file('employees.csv', as_attachment=True)
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

# -------------------------------
# تشغيل التطبيق
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
