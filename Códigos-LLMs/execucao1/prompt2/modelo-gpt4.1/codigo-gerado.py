from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

@app.before_first_request
def cria_bd():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        if Usuario.query.filter_by(username=username).first():
            flash('Usuário já existe.')
            return redirect(url_for('register'))
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(username=username, senha_hash=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login.')
        return redirect(url_for('login'))
    return render_template_string('''
        <h2>Registrar</h2>
        <form method="post">
            Usuário: <input name="username"><br>
            Senha: <input name="password" type="password"><br>
            <input type="submit" value="Registrar">
        </form>
        <a href="{{ url_for('login') }}">Login</a>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('home'))
        flash('Usuário ou senha inválidos.')
    return render_template_string('''
        <h2>Login</h2>
        <form method="post">
            Usuário: <input name="username"><br>
            Senha: <input name="password" type="password"><br>
            <input type="submit" value="Entrar">
        </form>
        <a href="{{ url_for('register') }}">Registrar</a>
    ''')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
@login_requerido
def home():
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template_string('''
        <h2>Bem-vindo, {{ usuario.username }}!</h2>
        <a href="{{ url_for('logout') }}">Sair</a>
    ''', usuario=usuario)

# Exemplo de rota protegida
@app.route('/protegido')
@login_requerido
def protegido():
    return 'Esta é uma rota protegida!'

if __name__ == '__main__':
    app.run(debug=True)