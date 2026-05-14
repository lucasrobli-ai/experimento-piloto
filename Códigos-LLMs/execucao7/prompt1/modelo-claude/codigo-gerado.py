from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Simulado banco de dados de usuários
users = {
    'usuario1': generate_password_hash('senha123'),
    'usuario2': generate_password_hash('senha456')
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return 'Usuário ou senha inválidos', 401
    
    return '''
    <form method="post">
        <input type="text" name="username" placeholder="Usuário" required>
        <input type="password" name="password" placeholder="Senha" required>
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return f'Bem-vindo, {session["username"]}! <a href="/logout">Logout</a>'

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Dashboard de {session["username"]} <a href="/logout">Logout</a>'

if __name__ == '__main__':
    app.run(debug=True)