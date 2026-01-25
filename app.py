from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

CSV_FILE = 'employees.csv'

def load_employees():
    employees = []
    with open(CSV_FILE, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            employees.append(row)
    return employees

def find_employee(ccp):
    employees = load_employees()
    for emp in employees:
        if emp['CCP'] == ccp:
            return emp
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'de@tggt':
            return redirect('/verify_account')
        else:
            message = "كلمة المرور خاطئة"
    return render_template('admin_login.html', message=message)

@app.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    message = None
    if request.method == 'POST':
        ccp = request.form.get('ccp')
        employee = find_employee(ccp)
        if employee:
            return render_template('success.html', employee=employee)
        else:
            message = "رقم الحساب البريدي غير موجود"
    return render_template('verify_account.html', message=message)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    ccp = request.args.get('ccp')
    employee = find_employee(ccp)
    if not employee:
        return "الموظف غير موجود"
    return render_template('edit_employee.html', employee=employee)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
