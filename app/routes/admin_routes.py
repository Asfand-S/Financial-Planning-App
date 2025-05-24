from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.db_utils import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM admins WHERE username=%s", (username,))
        # print(cur.fetchone())
        row = cur.fetchone()
        cur.close()
        conn.close()
        print(generate_password_hash("admin123"))
        print(row, password)
        print(check_password_hash(row[0], password))

        if row and check_password_hash(row[0], password):
            session['admin'] = username
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', error="Μη έγκυρο όνομα χρήστη ή κωδικός πρόσβασης.")
    return render_template('admin/login.html')

@admin_bp.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin.login'))

    msg = None
    if request.method == 'POST':
        new_user = request.form['new_user']
        new_pass = request.form['new_pass']

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", 
                        (new_user, generate_password_hash(new_pass)))
            conn.commit()
            msg = "User added successfully!"
        except:
            msg = "Username already exists."
        cur.close()
        conn.close()

    return render_template('admin/dashboard.html', users=get_users(), msg=msg)

@admin_bp.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users")
    users = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return users
