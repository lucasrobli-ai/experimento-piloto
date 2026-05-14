from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave secreta segura

# Usuários fictícios para autenticação
users = {
    "admin": "password123",
    "user": "mypassword"
}

# Decorador para proteger rotas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Você precisa fazer login para acessar esta página.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    return "Bem-vindo ao sistema! Você está logado."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('home'))
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")
    return '''
        <form method="post">
            <label for="username">Usuário:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Senha:</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)