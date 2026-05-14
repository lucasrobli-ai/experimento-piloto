from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
# Uma chave secreta é essencial para o gerenciamento de sessões no Flask.
# Em um ambiente de produção, use uma variável de ambiente para isso.
app.secret_key = 'uma_chave_secreta_muito_forte_e_aleatoria'

# Um armazenamento de usuários em memória para fins de demonstração.
# Em uma aplicação real, você usaria um banco de dados (ex: SQLAlchemy com SQLite/PostgreSQL).
users = {}

# Pré-popular um usuário para facilitar os testes iniciais.
# Usuário: testuser, Senha: password123
users["testuser"] = {"password_hash": generate_password_hash("password123")}

def login_required(f):
    """
    Decorador para proteger rotas que exigem autenticação do usuário.
    Redireciona para a página de login se o usuário não estiver logado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """
    Rota padrão. Redireciona para /home se logado, caso contrário para /login.
    """
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota para o registro de novos usuários.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('register.html')

        if username in users:
            flash('Nome de usuário já existe. Por favor, escolha outro.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        users[username] = {'password_hash': hashed_password}
        flash('Registro bem-sucedido! Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login de usuários.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('home')) # Redireciona para /home após o login
        else:
            flash('Credenciais inválidas. Por favor, tente novamente.', 'danger')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
@login_required # Garante que apenas usuários logados podem fazer logout
def logout():
    """
    Rota para o logout de usuários. Limpa a sessão.
    """
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/home')
@login_required # Esta rota é protegida e exige que o usuário esteja logado
def home():
    """
    Rota inicial protegida. Acessível apenas após o login.
    """
    return render_template('home.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)