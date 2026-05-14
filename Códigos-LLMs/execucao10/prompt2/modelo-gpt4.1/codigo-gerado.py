from flask import Flask, render_template_string, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua-chave-secreta'  # Troque por uma chave segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

@app.before_first_request
def cria_tabela():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        if Usuario.query.filter_by(username=username).first():
            return 'Usuário já existe'
        hash_senha = generate_password_hash(senha)
        novo_usuario = Usuario(username=username, password_hash=hash_senha)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string('''
        <form method="post">
            Usuário: <input name="username"><br>
            Senha: <input name="password" type="password"><br>
            <input type="submit" value="Registrar">
        </form>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and check_password_hash(usuario.password_hash, senha):
            session['usuario_id'] = usuario.id
            return redirect('/home')
        return 'Credenciais inválidas'
    return render_template_string('''
        <form method="post">
            Usuário: <input name="username"><br>
            Senha: <input name="password" type="password"><br>
            <input type="submit" value="Login">
        </form>
    ''')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
@login_required
def home():
    return 'Bem-vindo à página protegida!'

@app.route('/logout')
@login_required
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)