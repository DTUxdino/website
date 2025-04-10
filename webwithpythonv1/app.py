from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import json
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thay bằng key mạnh hơn

# Thiết lập Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Lớp User cho Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

# Hàm băm mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = sqlite3.connect('quiz.db')
        c = conn.cursor()
        c.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            login_user(User(user[0], user[1]))
            return redirect(url_for('index'))
        flash('Sai tên đăng nhập hoặc mật khẩu!')
    return render_template('login.html')

# Trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = sqlite3.connect('quiz.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Đăng ký thành công! Hãy đăng nhập.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Tên đăng nhập đã tồn tại!')
        conn.close()
    return render_template('register.html')

# Đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Trang chủ
@app.route('/')
@login_required
def index():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM subjects')
    subjects = c.fetchall()
    conn.close()
    return render_template('index.html', subjects=subjects)

# Trang quiz
@app.route('/quiz/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def quiz(subject_id):
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM subjects WHERE id = ?', (subject_id,))
    subject = c.fetchone()
    if not subject:
        flash('Môn học không tồn tại!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Chấm điểm
        score = 0
        answers = request.form
        c.execute('SELECT id, type, correct_answer, keywords FROM questions WHERE subject_id = ?', (subject_id,))
        questions = c.fetchall()
        for q in questions:
            q_id = str(q[0])
            user_answer = answers.get(q_id, '').lower().strip()
            if q[1] == 'multiple_choice' and user_answer == q[2]:
                score += 1
            elif q[1] in ['short_answer', 'essay'] and q[3]:
                keywords = q[3].lower().split(',')
                if all(keyword.strip() in user_answer for keyword in keywords):
                    score += 1

        # Lưu kết quả
        c.execute('INSERT INTO results (user_id, subject_id, score) VALUES (?, ?, ?)', (current_user.id, subject_id, score))
        conn.commit()
        conn.close()
        flash(f'Bạn được {score} điểm!')
        return redirect(url_for('index'))

    c.execute('SELECT id, type, content, options FROM questions WHERE subject_id = ?', (subject_id,))
    questions = [(q[0], q[1], q[2], json.loads(q[3]) if q[3] else None) for q in c.fetchall()]
    conn.close()
    return render_template('quiz.html', subject=subject, questions=questions)
# Trang xem điểm
@app.route('/results')
@login_required
def results():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('''
        SELECT r.score, s.name, r.id 
        FROM results r 
        JOIN subjects s ON r.subject_id = s.id 
        WHERE r.user_id = ?
        ORDER BY r.id DESC
    ''', (current_user.id,))
    results = c.fetchall()
    conn.close()
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)