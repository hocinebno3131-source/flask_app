from flask import Flask, render_template, request, redirect, url_for, abort
import csv
import os

app = Flask(__name__)

CSV_FILE = 'employees.csv'
ADMIN_PASSWORD = 'de@tggt'

# -------------------------------
# الصفحة الرئيسية: تسجيل دخول المدير
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            return render_template('verify_account.html')
        else:
            message = "كلمة المرور غير صحيحة."
    return render_template('index.html', message=message)

# -------------------------------
# منع الوصول المباشر إلى /admin
# -------------------------------
@app.route('/admin')
def admin_block():
    abort(404)

# -------------------------------
# صفحة التحقق من رقم الحساب (CCP)
# -------------------------------
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    if request.method == 'POST':
        ccp = request.form['ccp']
        try:
            with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    if row['CCP'] == ccp:
                        return render_template('success.html', employee=row)
        except FileNotFoundError:
            message = "ملف الموظفين غير موجود على السيرفر."
            return render_template('index.html', message=message)
        message = "رقم الحساب غير صحيح، حاول مرة أخرى."
        return render_template('index.html', message=message)
    return render_template('verify_account.html')

# -------------------------------
# صفحة تعديل بيانات الموظف
# -------------------------------
@app.route('/edit', methods=['GET', 'POST'])
def edit_employee():
    ccp = request.args.get('ccp') if request.method == 'GET' else request.form.get('ccp')
    if not ccp:
        return "CCP غير موجود", 400

    try:
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = list(csv.DictReader(f, delimiter=';'))
            fieldnames = reader[0].keys() if reader else []
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

    if request.method == 'POST':
        # تحديث البيانات حسب الحقول المرسلة
        updated = False
        for row in reader:
            if row['CCP'] == ccp:
                for key in fieldnames:
                    if key in request.form:
                        row[key] = request.form[key]
                updated = True
                break
        if not updated:
            return "الموظف غير موجود", 404

        # إعادة كتابة CSV بالقيم الجديدة
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(reader)

        # بعد الحفظ، إعادة توجيه المستخدم إلى صفحة الملف الشخصي
        return redirect(url_for('success_page', ccp=ccp))

    # GET → عرض الاستمارة
    for row in reader:
        if row['CCP'] == ccp:
            return render_template('edit_employee.html', employee=row)

    return "الموظف غير موجود", 404

# -------------------------------
# صفحة الملف الشخصي للموظف (success.html)
# -------------------------------
@app.route('/success')
def success_page():
    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود", 400
    try:
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('success.html', employee=row)
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500
    return "الموظف غير موجود", 404

# -------------------------------
# تشغيل التطبيق
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
