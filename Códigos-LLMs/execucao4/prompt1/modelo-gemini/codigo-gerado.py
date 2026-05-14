from flask import Flask, request, redirect, url_for, session, make_response
from functools import wraps

app = Flask(__name__)
# A chave secreta é essencial para a segurança das sessões no Flask.
# Em um ambiente de produção, use uma chave forte e gerada aleatoriamente.
app.secret_key = 'sua_chave_secreta_super_segura' # Mude esta chave!

# Simples banco de dados em memória para demonstração
# Em uma aplicação real, você usaria um banco de dados (SQLAlchemy, etc.)
users = {
    "admin": "password123",
    "user": "flaskpass"
}

def login_required(f):
    """
    Decorador para proteger rotas que exigem autenticação do usuário.
    Redireciona para a página de login se o usuário não estiver logado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # Redireciona para a página de login
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """
    Rota inicial que verifica se o usuário está logado.
    Se estiver, redireciona para o dashboard, caso contrário, para a página de login.
    """
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login do usuário.
    GET exibe o formulário de login.
    POST processa as credenciais enviadas.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['username'] = username # Armazena o usuário na sessão
            return redirect(url_for('dashboard'))
        else:
            # Em uma aplicação real, você pode renderizar um template com uma mensagem de erro.
            response = make_response("Usuário ou senha inválidos. <a href='/login'>Tentar novamente</a>")
            return response, 401 # 401 Unauthorized
    
    # Exibe o formulário de login para requisições GET
    return """
        <!doctype html>
        <title>Login</title>
        <h1>Login</h1>
        <form method="post">
            <p>
                <label for="username">Usuário:</label>
                <input type="text" name="username" id="username" required>
            </p>
            <p>
                <label for="password">Senha:</label>
                <input type="password" name="password" id="password" required>
            </p>
            <p><input type="submit" value="Entrar"></p>
        </form>
    """

@app.route('/dashboard')
@login_required # Protege esta rota com o decorador
def dashboard():
    """
    Rota protegida que só pode ser acessada por usuários logados.
    """
    return f"""
        <!doctype html>
        <title>Dashboard</title>
        <h1>Bem-vindo, {session['username']}!</h1>
        <p>Esta é sua área protegida.</p>
        <p><a href="/logout">Sair</a></p>
    """

@app.route('/logout')
def logout():
    """
    Rota para realizar o logout do usuário.
    Remove o usuário da sessão e redireciona para a página de login.
    """
    session.pop('username', None) # Remove 'username' da sessão
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)