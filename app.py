from flask import Flask, render_template, request, redirect, abort
import csv
import os

app = Flask(__name__)

CSV_FILE = 'employees.csv'

# -------------------------------
# الصفحة الرئيسية: تسجيل دخول المدير
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        password = request.form['password']
        if password == "de@tggt":
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
@app.route('/verify_account', methods=['POST'])
def verify_account():
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

# -------------------------------
# صفحة تعديل بيانات الموظف (GET + POST)
# -------------------------------
@app.route('/edit', methods=['GET', 'POST'])
def edit_employee():

    # ---------------- GET : عرض الاستمارة ----------------
    if request.method == 'GET':
        ccp = request.args.get('ccp')
        if not ccp:
            return "CCP غير موجود في الرابط", 400

        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('edit_employee.html', employee=row)

        return "الموظف غير موجود", 404

    # ---------------- POST : حفظ التعديلات ----------------
    if request.method == 'POST':
        updated_ccp = request.form.get('CCP')

        rows = []
        updated_employee = None

        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            fieldnames = reader.fieldnames

            for row in reader:
                if row['CCP'] == updated_ccp:
                    # تحديث القيم
                    for key in fieldnames:
                        if key in request.form:
                            row[key] = request.form.get(key)

                    updated_employee = row

                rows.append(row)

        # إعادة كتابة الملف بعد التعديل
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(rows)

        # الرجوع لصفحة ملف الموظف بعد الحفظ
        return render_template('success.html', employee=updated_employee)

# -------------------------------
# تشغيل التطبيق
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
