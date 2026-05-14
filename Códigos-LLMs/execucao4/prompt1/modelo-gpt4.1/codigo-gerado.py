from flask import Flask, render_template_string, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Troque por uma chave secreta forte

# Usuário de exemplo (em produção, use um banco de dados)
USUARIO = {
    'username': 'admin',
    'password': 'senha123'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USUARIO['username'] and password == USUARIO['password']:
            session['usuario'] = username
            return redirect(url_for('home'))
        else:
            erro = 'Usuário ou senha inválidos.'
    return render_template_string('''
        <h2>Login</h2>
        {% if erro %}<p style="color:red;">{{ erro }}</p>{% endif %}
        <form method="post">
            Usuário: <input type="text" name="username"><br>
            Senha: <input type="password" name="password"><br>
            <input type="submit" value="Entrar">
        </form>
    ''', erro=erro)

@app.route('/logout')
@login_required
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return f'Bem-vindo, {session["usuario"]}! <a href="/logout">Sair</a>'

if __name__ == '__main__':
    app.run(debug=True)