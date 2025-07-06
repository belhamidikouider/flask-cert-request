from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret-key'

# قاعدة البيانات
def init_db():
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
    conn.commit()
    conn.close()

init_db()

# الواجهة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# استقبال الطلب
@app.route('/submit', methods=['POST'])
def submit():
    data = (
        request.form['first_name'],
        request.form['last_name'],
        request.form['birth_date'],
        request.form['birth_place'],
        request.form['father_name'],
        request.form['mother_name'],
        request.form['position'],
        request.form['phone'],
        request.form['email']
    )
    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO requests (
            first_name, last_name, birth_date, birth_place,
            father_name, mother_name, position, phone, email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# تسجيل الدخول للمسؤول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'belhamidikouider' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('view_requests'))
        else:
            return "بيانات الدخول غير صحيحة"
    return render_template('login.html')

# عرض الطلبات
@app.route('/requests')
def view_requests():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    c.execute('SELECT * FROM requests')
    rows = c.fetchall()
    conn.close()
    return render_template('requests.html', rows=rows)

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

