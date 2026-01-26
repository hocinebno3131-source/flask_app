from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

CSV_FILE = 'employees.csv'
ADMIN_PASSWORD = 'de@tggt'

# الصفحة الرئيسية
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

# منع الوصول المباشر إلى /admin
@app.route('/admin')
def admin_block():
    return "404 Not Found", 404

# التحقق من CCP
@app.route('/verify_account', methods=['POST', 'GET'])
def verify_account():
    if request.method == 'POST':
        ccp = request.form['ccp']
    else:  # GET من زر خروج
        ccp = request.args.get('ccp')

    try:
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('success.html', employee=row)
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500
    return "الموظف غير موجود", 404

# صفحة تعديل بيانات الموظف
@app.route('/edit', methods=['GET'])
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود في الرابط", 400
    try:
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('edit_employee.html', employee=row)
    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500
    return "الموظف غير موجود", 404

# حفظ التعديلات
@app.route('/update_employee', methods=['POST'])
def update_employee():
    form = request.form
    updated_data = {
        'CCP': form.get('CCP'),
        'NIN': form.get('NIN', ''),
        'last_name': form.get('last_name', ''),
        'first_name': form.get('first_name', ''),
        'birth_date': form.get('birth_date', ''),
        'rank': form.get('rank', ''),
        'institution': form.get('institution', ''),
        'TEL': form.get('TEL', '')
    }

    # قراءة كل الموظفين
    employees = []
    with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames
        for row in reader:
            if row['CCP'] == updated_data['CCP']:
                row.update(updated_data)  # تحديث الحقول
            employees.append(row)

    # كتابة الملف مرة أخرى
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(employees)

    # إعادة توجيه إلى صفحة الملف الشخصي للموظف
    return redirect(f"/verify_account?ccp={updated_data['CCP']}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
