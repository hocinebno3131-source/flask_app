from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

CSV_FILE = 'employees.csv'
ADMIN_PASSWORD = 'de@tggt'

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# تسجيل دخول المدير
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            return redirect(url_for('verify_account'))
        else:
            return render_template('admin_login.html', message="كلمة المرور غير صحيحة")
    return render_template('admin_login.html')

# صفحة التحقق من CCP
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    if request.method == 'POST':
        ccp = request.form.get('ccp')
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('success.html', employee=row)
        return render_template('verify_account.html', message="رقم الحساب غير موجود")
    return render_template('verify_account.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
