from flask import Flask, render_template_string, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Usuários de exemplo
USERS = {
    'usuario': 'senha123'
}

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
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('home'))
        return render_template_string(LOGIN_TEMPLATE, error='Usuário ou senha inválidos')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return f'Bem-vindo, {session["user"]}! <a href="/logout">Logout</a>'

LOGIN_TEMPLATE = '''
<!doctype html>
<title>Login</title>
<h2>Login</h2>
{% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
<form method="post">
  <input type="text" name="username" placeholder="Usuário" required>
  <input type="password" name="password" placeholder="Senha" required>
  <button type="submit">Entrar</button>
</form>
'''

if __name__ == '__main__':
    app.run(debug=True)