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
@app.route('/edit')
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود في الرابط", 400

    try:
        with open('employees.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('edit_employee.html', employee=row)
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

    return "الموظف غير موجود", 404

# -------------------------------
# حفظ التعديلات في ملف CSV
# -------------------------------
@app.route('/update', methods=['POST'])
def update_employee():
    form = request.form
    ccp = form['CCP']

    rows = []
    updated = False

    try:
        with open('employees.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            fieldnames = reader.fieldnames

            for row in reader:
                if row['CCP'] == ccp:
                    row['NIN'] = form['NIN']
                    row['poste_travail'] = form['poste_travail']
                    row['categorie'] = form['categorie']
                    row['daira'] = form['daira']
                    row['commune'] = form['commune']
                    row['ecole'] = form['ecole']
                    row['TEL'] = form['TEL']
                    row['employee_id'] = form['employee_id']
                    updated = True

                rows.append(row)

        if updated:
            with open('employees.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(rows)

    except Exception as e:
        return f"خطأ أثناء الحفظ: {e}", 500

    return redirect(url_for('admin_login'))

# -------------------------------
# تشغيل التطبيق
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
