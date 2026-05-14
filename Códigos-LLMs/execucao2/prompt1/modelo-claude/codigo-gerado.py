from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Simulando um banco de dados de usuários
users = {
    'user1': generate_password_hash('password123'),
    'user2': generate_password_hash('senha456')
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
        
        if username in users and check_password_hash(users[username], password):
            session['user_id'] = username
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    
    return '''
    <form method="post">
        <input type="text" name="username" placeholder="Usuário" required>
        <input type="password" name="password" placeholder="Senha" required>
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    return f'<h1>Bem-vindo, {session["user_id"]}!</h1><a href="/logout">Logout</a>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)