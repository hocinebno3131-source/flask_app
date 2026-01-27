from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

# الصفحة الرئيسية
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

# منع الوصول المباشر إلى /admin
@app.route('/admin')
def admin_block():
    abort(404)

# صفحة التحقق من CCP
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    ccp = None
    if request.method == 'POST':
        ccp = request.form.get('ccp')
    elif request.method == 'GET':
        ccp = request.args.get('ccp')

    if not ccp:
        return render_template('verify_account.html')

    try:
        with open('employees.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp:
                    return render_template('success.html', employee=row)
    except FileNotFoundError:
        return render_template('index.html', message="ملف الموظفين غير موجود.")

    return render_template('verify_account.html', message="رقم الحساب غير موجود")

# صفحة الملف الشخصي
@app.route('/success')
def success():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect('/')
    with open('employees.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row)
    return "الموظف غير موجود", 404

# صفحة تعديل الموظف
@app.route('/edit')
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود", 400
    with open('employees.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('edit_employee.html', employee=row)
    return "الموظف غير موجود", 404

# حفظ التعديلات
@app.route('/edit_employee_save', methods=['POST'])
def edit_employee_save():
    ccp = request.form.get('CCP')
    if not ccp:
        return redirect('/')

    # قراءة جميع الموظفين
    employees = []
    with open('employees.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            employees.append(row)

    # تحديث بيانات الموظف
    for row in employees:
        if row['CCP'] == ccp:
            for field in ['NIN','last_name','first_name','birth_date','poste_travail',
                          'categorie','daira','commune','ecole','TEL']:
                row[field] = request.form.get(field, '')
            break

    # إعادة كتابة الملف
    with open('employees.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=employees[0].keys(), delimiter=';')
        writer.writeheader()
        writer.writerows(employees)

    return redirect(f"/success?ccp={ccp}")

# تشغيل التطبيق
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
