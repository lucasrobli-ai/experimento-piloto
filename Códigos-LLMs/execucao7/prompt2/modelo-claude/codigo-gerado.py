from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Simulated user database (replace with real database in production)
users_db = {
    'user1': generate_password_hash('password123'),
    'user2': generate_password_hash('securepass456')
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users_db and check_password_hash(users_db[username], password):
            session['user_id'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials'), 401
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return f'Welcome, {session["user_id"]}! <a href="/logout">Logout</a>'


@app.route('/protected')
@login_required
def protected_route():
    return f'This is a protected route for {session["user_id"]}'


if __name__ == '__main__':
    app.run(debug=False)