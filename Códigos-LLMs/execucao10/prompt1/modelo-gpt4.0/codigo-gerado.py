from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave secreta segura

# Usuários fictícios para autenticação
usuarios = {
    "admin": "senha123",
    "usuario": "senha456"
}

@app.route('/')
def index():
    if 'usuario' in session:
        return f"Bem-vindo, {session['usuario']}! <a href='/logout'>Sair</a>"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in usuarios and usuarios[username] == password:
            session['usuario'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/protegido')
def protegido():
    if 'usuario' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    return f"Esta é uma página protegida, {session['usuario']}! <a href='/logout'>Sair</a>"

if __name__ == '__main__':
    app.run(debug=True)