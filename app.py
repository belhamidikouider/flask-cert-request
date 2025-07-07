from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os   # ✅ مهم لقراءة المتغيرات

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# الصفحة الرئيسية
@app.route('/', methods=['GET', 'POST'])
def index():
    track_result = None
    if request.method == 'POST':
        if 'track' in request.form:
            phone = request.form['track_phone']
            conn = sqlite3.connect('requests.db')
            c = conn.cursor()
            c.execute('SELECT * FROM requests WHERE phone = ?', (phone,))
            result = c.fetchone()
            conn.close()
            if result:
                track_result = f"""
                تم العثور على طلب:
                الاسم: {result[1]} {result[2]}
                الوظيفة: {result[7]}
                الحالة: {result[11]}
                """
            else:
                track_result = 'لم يتم العثور على طلب برقم الهاتف هذا.'
        elif 'submit' in request.form:
            phone = request.form['phone']
            conn = sqlite3.connect('requests.db')
            c = conn.cursor()
            c.execute('SELECT * FROM requests WHERE phone = ?', (phone,))
            existing = c.fetchone()
            if existing:
                conn.close()
                return 'لقد قمت بإرسال طلب بالفعل بهذا الرقم.'
            data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'birth_date': request.form['birth_date'],
                'birth_place': request.form['birth_place'],
                'father_name': request.form['father_name'],
                'mother_name': request.form['mother_name'],
                'position': request.form['position'],
                'phone': phone,
                'email': request.form['email'],
                'status': 'قيد المعالجة'
            }
            c.execute('''
                INSERT INTO requests 
                (first_name, last_name, birth_date, birth_place, father_name, mother_name, position, phone, email, status)
                VALUES 
                (:first_name, :last_name, :birth_date, :birth_place, :father_name, :mother_name, :position, :phone, :email, :status)
            ''', data)
            conn.commit()
            conn.close()
            return 'تم إرسال طلبك بنجاح!'
    return render_template('index.html', track_result=track_result)

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # ✅ قراءة من Environment Variables
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')

        if username == admin_username and password == admin_password:
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
    c.execute('SELECT id, first_name, last_name, phone, status FROM requests')
    requests_data = c.fetchall()
    conn.close()
    return render_template('admin.html', requests=requests_data)

# تحديث الحالة
@app.route('/update_status/<int:request_id>', methods=['POST'])
def update_status(request_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    new_status = request.form['new_status']
    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    c.execute('UPDATE requests SET status = ? WHERE id = ?', (new_status, request_id))
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
