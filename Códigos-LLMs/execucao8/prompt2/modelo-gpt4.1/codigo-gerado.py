from flask import Flask, render_template_string, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Modelo de usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

# Cria o banco de dados
with app.app_context():
    db.create_all()

# Template simples para login e registro
login_template = '''
<form method="post">
    Usuário: <input type="text" name="username"><br>
    Senha: <input type="password" name="password"><br>
    <input type="submit" value="Entrar">
</form>
<a href="{{ url_for('register') }}">Registrar</a>
'''

register_template = '''
<form method="post">
    Usuário: <input type="text" name="username"><br>
    Senha: <input type="password" name="password"><br>
    <input type="submit" value="Registrar">
</form>
<a href="{{ url_for('login') }}">Login</a>
'''

home_template = '''
<h1>Bem-vindo, {{ username }}!</h1>
<a href="{{ url_for('logout') }}">Logout</a>
'''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'Usuário já existe.'
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string(register_template)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/home')
        return 'Credenciais inválidas.'
    return render_template_string(login_template)

@app.route('/home')
@login_required
def home():
    return render_template_string(home_template, username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)