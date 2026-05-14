from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)
# A chave secreta é essencial para a segurança das sessões.
# Em produção, use uma chave forte e gerada aleatoriamente.
app.secret_key = 'sua_chave_secreta_muito_forte_aqui_para_producao'

# Simula um banco de dados de usuários.
# Em uma aplicação real, você usaria um banco de dados persistente.
users = {}

# Pré-popula alguns usuários para demonstração.
# Em uma aplicação real, os usuários se registrariam através de uma rota '/register'.
# As senhas são armazenadas como hashes.
users['lucas'] = {'password_hash': generate_password_hash('senha123')}
users['admin'] = {'password_hash': generate_password_hash('adminseguro')}

# Decorator para proteger rotas, exigindo que o usuário esteja logado.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            # Se não estiver logado, redireciona para a página de login
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    """Redireciona para /home se já estiver logado, caso contrário para /login."""
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Permite que os usuários façam login.
    - GET: Exibe o formulário de login.
    - POST: Processa as credenciais enviadas.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = users.get(username)

        if user_data and check_password_hash(user_data['password_hash'], password):
            # Credenciais válidas: marca o usuário como logado na sessão e armazena o nome de usuário.
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            # Credenciais inválidas: exibe uma mensagem de erro.
            return render_template_string("""
                <h1>Login</h1>
                <p style="color:red;">Credenciais inválidas. Tente novamente.</p>
                <form method="post">
                    <label for="username">Usuário:</label><br>
                    <input type="text" id="username" name="username"><br>
                    <label for="password">Senha:</label><br>
                    <input type="password" id="password" name="password"><br><br>
                    <input type="submit" value="Login">
                </form>
            """)
    
    # GET request: exibe o formulário de login.
    return render_template_string("""
        <h1>Login</h1>
        <form method="post">
            <label for="username">Usuário:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Senha:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Login">
        </form>
    """)

@app.route('/home')
@login_required # Esta rota é protegida e só pode ser acessada por usuários logados.
def home():
    """Página inicial acessível apenas para usuários autenticados."""
    return render_template_string(f"""
        <h1>Bem-vindo, {session.get('username', 'Usuário')}!</h1>
        <p>Esta é uma página protegida. Você está logado com sucesso.</p>
        <p><a href="/logout">Logout</a></p>
    """)

@app.route('/logout')
def logout():
    """Desloga o usuário, limpando a sessão."""
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Execute a aplicação Flask.
    # Em produção, 'debug=True' deve ser desativado.
    app.run(debug=True)