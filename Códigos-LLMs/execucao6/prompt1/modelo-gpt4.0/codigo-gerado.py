from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave secreta segura

# Usuários fictícios para autenticação
users = {
    "admin": "password123",
    "user": "userpass"
}

@app.route('/')
def home():
    if 'username' in session:
        return f"Bem-vindo, {session['username']}! <a href='/logout'>Logout</a>"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
    return '''
        <form method="post">
            <label for="username">Usuário:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Senha:</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/protegido')
def protegido():
    if 'username' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    return f"Esta é uma página protegida. Bem-vindo, {session['username']}!"

if __name__ == '__main__':
    app.run(debug=True)