from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

# -------------------------------
# الصفحة الرئيسية: تسجيل دخول المدير
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        password = request.form['password']
        if password == "de@tggt":
            # قراءة employees.csv لعرض صفحة verify_account
            return render_template('verify_account.html')
        else:
            message = "كلمة المرور غير صحيحة."
    return render_template('index.html', message=message)

# -------------------------------
# منع الوصول المباشر إلى /admin
# -------------------------------
@app.route('/admin')
def admin_redirect():
    # يمكن التحويل مباشرة إلى /
    return redirect('/')

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
        return render_template('index.html', message=message)
    message = "رقم الحساب غير صحيح، حاول مرة أخرى."
    return render_template('index.html', message=message)

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
# تشغيل التطبيق
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
