from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

# Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

# Criação do banco de dados
with app.app_context():
    db.create_all()

# Decorador para rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rota de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']
        if Usuario.query.filter_by(username=username).first():
            flash('Usuário já existe.')
            return redirect(url_for('register'))
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(username=username, senha_hash=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Registro realizado com sucesso. Faça login.')
        return redirect(url_for('login'))
    return render_template_string('''
        <h2>Registrar</h2>
        <form method="post">
            Usuário: <input name="username"><br>
            Senha: <input name="senha" type="password"><br>
            <input type="submit" value="Registrar">
        </form>
        <a href="{{ url_for('login') }}">Login</a>
    ''')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('home'))
        flash('Usuário ou senha inválidos.')
    return render_template_string('''
        <h2>Login</h2>
        <form method="post">
            Usuário: <input name="username"><br>
            Senha: <input name="senha" type="password"><br>
            <input type="submit" value="Entrar">
        </form>
        <a href="{{ url_for('register') }}">Registrar</a>
    ''')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

# Rota protegida
@app.route('/home')
@login_required
def home():
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template_string('''
        <h2>Bem-vindo, {{ usuario.username }}!</h2>
        <a href="{{ url_for('logout') }}">Sair</a>
    ''', usuario=usuario)

if __name__ == '__main__':
    app.run(debug=True)