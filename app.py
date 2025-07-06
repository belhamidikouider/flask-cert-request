from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# الصفحة الرئيسية - نموذج الطلب
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'birth_date': request.form['birth_date'],
            'birth_place': request.form['birth_place'],
            'father_name': request.form['father_name'],
            'mother_name': request.form['mother_name'],
            'position': request.form['position'],
            'phone': request.form['phone'],
            'email': request.form['email']
        }

        conn = sqlite3.connect('requests.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                birth_date TEXT,
                birth_place TEXT,
                father_name TEXT,
                mother_name TEXT,
                position TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        c.execute('''
            INSERT INTO requests 
            (first_name, last_name, birth_date, birth_place, father_name, mother_name, position, phone, email)
            VALUES 
            (:first_name, :last_name, :birth_date, :birth_place, :father_name, :mother_name, :position, :phone, :email)
        ''', data)
        conn.commit()
        conn.close()
        return 'تم إرسال طلبك بنجاح!'
    return render_template('index.html')


# تسجيل دخول المسؤول
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'بيانات الدخول غير صحيحة'
    return render_template('login.html', error=error)


# لوحة التحكم
@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    c.execute('SELECT * FROM requests')
    requests_data = c.fetchall()
    conn.close()
    return render_template('admin.html', requests=requests_data)


# حذف طلب محدد
@app.route('/delete/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    c.execute('DELETE FROM requests WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)

