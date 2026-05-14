from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Banco de dados simulado
users = {
    'usuario1': generate_password_hash('senha123'),
    'usuario2': generate_password_hash('senha456')
}

# Decorator para proteger rotas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Usuário ou senha inválidos')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Bem-vindo, {session["user"]}! <a href="{url_for("logout")}">Logout</a>'

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)