import csv
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ===== صفحة التحقق من CCP =====
@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    ccp = None
    if request.method == 'POST':
        ccp = request.form.get('ccp')
    elif request.method == 'GET':
        ccp = request.args.get('ccp')

    if not ccp:
        return render_template('verify_account.html')

    with open('employees.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row)

    return render_template('verify_account.html', message="رقم الحساب غير موجود")


# ===== صفحة ملف الموظف =====
@app.route('/success')
def success():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('verify_account'))

    with open('employees.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('success.html', employee=row)

    return redirect(url_for('verify_account'))


# ===== صفحة تعديل بيانات الموظف =====
@app.route('/edit')
def edit_employee():
    ccp = request.args.get('ccp')
    if not ccp:
        return redirect(url_for('verify_account'))

    with open('employees.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['CCP'] == ccp:
                return render_template('edit_employee.html', employee=row)

    return redirect(url_for('verify_account'))


# ===== حفظ التعديلات على employees.csv =====
@app.route('/update_employee', methods=['POST'])
def update_employee():
    ccp = request.form.get('CCP')
    if not ccp:
        return redirect(url_for('verify_account'))

    # قراءة جميع الموظفين
    employees = []
    with open('employees.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            employees.append(row)

    # تحديث بيانات الموظف المطلوب
    updated = False
    for row in employees:
        if row['CCP'] == ccp:
            row['NIN'] = request.form.get('NIN', '')
            row['last_name'] = request.form.get('last_name', '')
            row['first_name'] = request.form.get('first_name', '')
            row['birth_date'] = request.form.get('birth_date', '')
            row['poste_travail'] = request.form.get('poste_travail', '')
            row['categorie'] = request.form.get('categorie', '')
            row['daira'] = request.form.get('daira', '')
            row['commune'] = request.form.get('commune', '')
            row['ecole'] = request.form.get('ecole', '')
            row['TEL'] = request.form.get('TEL', '')
            updated = True
            break

    if updated:
        # كتابة التعديلات إلى ملف CSV
        with open('employees.csv', 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['employee_id','last_name','first_name','TEL','CCP','birth_date','NIN',
                          'poste_travail','categorie','daira','commune','ecole']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for row in employees:
                writer.writerow(row)

    # بعد الحفظ، العودة إلى صفحة ملف الموظف
    return redirect(url_for('success', ccp=ccp))


if __name__ == '__main__':
    app.run(debug=True)
