from flask import Flask, redirect, url_for, request, session, flash, escape
from functools import wraps

app = Flask(__name__)
# A chave secreta é essencial para a segurança das sessões no Flask.
# Em produção, use uma chave forte e armazene-a de forma segura (e.g., variável de ambiente).
app.secret_key = 'uma_chave_secreta_muito_segura_e_longa_para_o_seu_aplicativo'

# Dados de usuário fictícios para demonstração.
# Em um aplicativo real, você usaria um banco de dados e senhas com hash.
USERS = {
    "usuario1": "senha123",
    "admin": "admin123",
}

def login_required(f):
    """
    Um decorador para proteger rotas, exigindo que o usuário esteja logado.
    Se o usuário não estiver logado, ele é redirecionado para a página de login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """
    Rota inicial que verifica o status de login e redireciona.
    """
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login do usuário.
    - GET: Exibe o formulário de login.
    - POST: Processa as credenciais enviadas.
    """
    if 'logged_in' in session and session['logged_in']:
        flash('Você já está logado!', 'info')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash(f'Login bem-sucedido! Bem-vindo, {escape(username)}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
            return redirect(url_for('login'))
    
    # Renderiza um formulário HTML básico para o GET
    # Em um aplicativo real, você usaria render_template('login.html')
    # Adicionando um loop simples para exibir mensagens flash
    messages_html = ""
    for category, message in session.get('_flashes', []): # Acessa diretamente a lista de flashes
        messages_html += f'<li class="{escape(category)}">{escape(message)}</li>'
    session.pop('_flashes', None) # Limpa os flashes após exibi-los
    
    return f"""
        <!doctype html>
        <html lang="pt-BR">
        <head>
            <meta charset="utf-8">
            <title>Login</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                form div {{ margin-bottom: 10px; }}
                label {{ display: inline-block; width: 80px; }}
                .flashes {{ list-style: none; padding: 0; }}
                .flashes li {{ padding: 8px 15px; margin-bottom: 5px; border-radius: 4px; }}
                .success {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .warning {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
                .danger {{ background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .info {{ background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
            </style>
        </head>
        <body>
            <h1>Login</h1>
            <ul class="flashes">{messages_html}</ul>
            <form method="post">
                <div>
                    <label for="username">Usuário:</label>
                    <input type="text" name="username" id="username" required>
                </div>
                <div>
                    <label for="password">Senha:</label>
                    <input type="password" name="password" id="password" required>
                </div>
                <div>
                    <input type="submit" value="Entrar">
                </div>
            </form>
            <p><strong>Credenciais de teste:</strong></p>
            <ul>
                <li>usuario1 / senha123</li>
                <li>admin / admin123</li>
            </ul>
        </body>
        </html>
    """

@app.route('/dashboard')
@login_required # Protege esta rota, exigindo login
def dashboard():
    """
    Rota protegida, acessível apenas para usuários logados.
    """
    username = session.get('username', 'Usuário Desconhecido')
    
    messages_html = ""
    for category, message in session.get('_flashes', []):
        messages_html += f'<li class="{escape(category)}">{escape(message)}</li>'
    session.pop('_flashes', None)
    
    return f"""
        <!doctype html>
        <html lang="pt-BR">
        <head>
            <meta charset="utf-8">
            <title>Dashboard</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                .flashes {{ list-style: none; padding: 0; }}
                .flashes li {{ padding: 8px 15px; margin-bottom: 5px; border-radius: 4px; }}
                .success {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .warning {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
                .danger {{ background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .info {{ background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
            </style>
        </head>
        <body>
            <h1>Bem-vindo ao Dashboard, {escape(username)}!</h1>
            <ul class="flashes">{messages_html}</ul>
            <p>Esta é uma área protegida do sistema.</p>
            <p><a href="/logout">Sair (Logout)</a></p>
            <p><a href="/">Voltar para Início</a></p>
        </body>
        </html>
    """

@app.route('/logout')
def logout():
    """
    Rota para realizar o logout do usuário.
    Limpa a sessão e redireciona para a página de login.
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Execute o aplicativo no modo de depuração para desenvolvimento.
    # Em produção, use um servidor WSGI (e.g., Gunicorn, uWSGI).
    app.run(debug=True)