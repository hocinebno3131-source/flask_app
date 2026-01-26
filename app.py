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
# صفحة تعديل بيانات الموظف
# -------------------------------
@app.route('/edit')
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

# -------------------------------
# حفظ التعديلات من استمارة edit_employee.html
# -------------------------------
@app.route('/edit_employee_save', methods=['POST'])
def edit_employee_save():
    ccp_original = request.form['CCP']
    updated_data = {
        'employee_id': '',  # لن نغيّرها، يمكن تركها فارغة أو الحفاظ على القديم
        'last_name': request.form.get('last_name', ''),
        'first_name': request.form.get('first_name', ''),
        'TEL': request.form.get('TEL', ''),
        'CCP': request.form.get('CCP_input', ''),
        'birth_date': request.form.get('birth_date', ''),
        'NIN': request.form.get('NIN', ''),
        'poste_travail': request.form.get('poste_travail', ''),
        'categorie': request.form.get('categorie', ''),
        'daira': request.form.get('daira', ''),
        'commune': request.form.get('commune', ''),
        'ecole': request.form.get('ecole', '')
    }

    try:
        rows = []
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['CCP'] == ccp_original:
                    # نحتفظ بالemployee_id القديمة إذا كانت موجودة
                    updated_data['employee_id'] = row.get('employee_id', '')
                    rows.append(updated_data)
                else:
                    rows.append(row)

        # كتابة الملف مجددًا مع التعديلات
        fieldnames = ['employee_id','last_name','first_name','TEL','CCP','birth_date','NIN',
                      'poste_travail','categorie','daira','commune','ecole']
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(rows)

        return redirect(f"/success?ccp={updated_data['CCP']}")

    except FileNotFoundError:
        return "ملف الموظفين غير موجود على السيرفر.", 500

# -------------------------------
# صفحة الملف الشخصي بعد تعديل الموظف
# -------------------------------
@app.route('/success')
def success():
    ccp = request.args.get('ccp')
    if not ccp:
        return "CCP غير موجود في الرابط", 400
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
