from flask import Flask, request, redirect, url_for, render_template, session, flash, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'DBHW1'

# 設定 MySQL 資料庫連接
db_config = {
    'user': 'root',
    'password': 'vm3tj06jo3',
    'host': 'localhost',
    'database': 'hw1',
    'port': 3300
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/')
def index():
    if 'user_id' in session:
        education = session.get('education')
        logout_url = url_for('logout')
        name = session.get('name')
        
        if education == "teacher":
            message = f'{name}老師您好，歡迎使用本系統。'
            template = 'teacher_dashboard.html'
        else:
            message = f'{name}您好，歡迎使用本系統，請點選以下功能進行您的工作！'
            template = 'student_dashboard.html'
        
        return render_template(template, message=message, logout_url=logout_url)
    
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            flash('無法連接到數據庫。')
            return redirect(url_for('login'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = username
            session['name'] = user['name']  # 抓登入用戶的 name 並存入 session
            session['education'] = user['education'] # 抓登入用戶的身份並存入 session，用來辨識登入者身份
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        gender = request.form['gender']
        birth_year = request.form['birth_year']
        education = request.form['education']
        expert = request.form['expert']

        conn = get_db_connection()
        if conn is None:
            flash('無法連接到數據庫。')
            return redirect(url_for('register'))

        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('用戶名已存在，請選擇其他用戶名。')
            else:
                cursor.execute(
                    '''INSERT INTO users (username, password, email, name, gender, birth_year, education, expert)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (username, password, email, name, gender, birth_year, education, expert)
                )
                conn.commit()
                flash('註冊成功！請登入。')

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('處理請求時發生錯誤。')

        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('name', None)  # 登出時移除 name
    return redirect(url_for('index'))

@app.route('/check-username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data.get('username')

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '無法連接到資料庫。'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    existing_user = cursor.fetchone()
    conn.close()

    return jsonify({'exists': existing_user is not None})

if __name__ == '__main__':
    app.run(debug=True)
