from flask import Flask, render_template, request, redirect, abort
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
    ccp = None
    if request.method == 'POST':
        ccp = request.form.get('ccp')
    elif request.method == 'GET':
        ccp = request.args.get('ccp')

    if not ccp:
        return render_template('verify_account.html')

    with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row)

    return render_template('verify_account.html', message="رقم الحساب غير موجود")

# -------------------------------
# صفحة تعديل بيانات الموظف
# -------------------------------
@app.route('/edit', methods=['GET', 'POST'])
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود في الرابط", 400

    # إذا تم POST، احفظ التغييرات في employees.csv
    if request.method == 'POST':
        new_data = request.form.to_dict()
        updated = False
        employees = []
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    # تحديث كل الحقول الجديدة
                    for key in new_data:
                        row[key] = new_data[key]
                    updated = True
                employees.append(row)
        if updated:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=reader.fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(employees)
            return redirect(f"/edit?ccp={ccp}")  # إعادة تحميل الاستمارة بعد الحفظ
        else:
            return "الموظف غير موجود", 404

    # GET → عرض الاستمارة
    try:
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
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
