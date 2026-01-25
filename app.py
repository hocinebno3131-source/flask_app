from flask import Flask, render_template, request, send_file, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"  # ضروري للجلسات

EMPLOYEE_FILE = "employees.csv"

# -------------------------------
# صفحة تسجيل الدخول (مدير / أدمن)
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        password = request.form.get('password')

        if password == "de@tggt":
            session['role'] = 'manager'
            return redirect(url_for('verify_page'))

        elif password == "hocine":
            session['role'] = 'admin'
            return redirect(url_for('verify_page'))

        else:
            message = "كلمة المرور غير صحيحة"

    return render_template('admin_login.html', message=message)


# -------------------------------
# صفحة إدخال CCP
# -------------------------------
@app.route('/verify')
def verify_page():
    if 'role' not in session:
        return redirect(url_for('login'))
    return render_template('verify_account.html')


# -------------------------------
# التحقق من CCP
# -------------------------------
@app.route('/verify_account', methods=['POST'])
def verify_account():
    if 'role' not in session:
        return redirect(url_for('login'))

    ccp = request.form['ccp']

    try:
        with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template(
                        'success.html',
                        employee=row,
                        role=session['role']
                    )
    except FileNotFoundError:
        message = "ملف الموظفين غير موجود."
        return render_template('verify_account.html', message=message)

    message = "رقم الحساب غير صحيح."
    return render_template('verify_account.html', message=message)


# -------------------------------
# تحميل ملف employees.csv (للأدمن فقط)
# -------------------------------
@app.route('/download')
def download_file():
    if session.get('role') != 'admin':
        return "غير مصرح لك بالدخول", 403

    return send_file(
        EMPLOYEE_FILE,
        as_attachment=True,
        download_name="employees.csv"
    )


# -------------------------------
# صفحة تعديل الموظف
# -------------------------------
@app.route('/edit')
def edit_employee():
    if 'role' not in session:
        return redirect(url_for('login'))

    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود", 400

    try:
        with open(EMPLOYEE_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('edit_employee.html', employee=row)
    except:
        return "خطأ في قراءة الملف", 500

    return "الموظف غير موجود", 404


# -------------------------------
# تشغيل التطبيق
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
