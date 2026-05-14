from flask import Flask, redirect, url_for, request, flash

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "sua_chave_secreta_aqui"  # Mude para uma chave secreta forte

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Rota para onde redirecionar se o usuário não estiver logado

# Um simples armazenamento de usuários em memória para este exemplo
users = {
    "usuario1": {"password": "senha1"},
    "admin": {"password": "admin"},
}


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_data = users.get(username)
        if user_data and user_data["password"] == password:
            user = User(username)
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            # Redireciona para a página originalmente acessada, se houver
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Nome de usuário ou senha inválidos.", "danger")
    # Em uma aplicação real, você renderizaria um template com um formulário de login aqui
    return """
        <h1>Página de Login</h1>
        <form method="POST">
            <label for="username">Usuário:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Senha:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Entrar">
        </form>
        <p>Usuários de teste: usuario1/senha1, admin/admin</p>
        {}
    """.format(
        "".join([f"<p style='color: {'green' if cat == 'success' else 'red'};'>{msg}</p>" for msg, cat in zip(request.with_entities(flash)().get_flashed_messages(with_categories=True), request.with_entities(flash)().get_flashed_messages(with_categories=True))])
    )


@app.route("/dashboard")
@login_required  # Esta rota requer autenticação
def dashboard():
    return f"""
        <h1>Bem-vindo, {current_user.id}!</h1>
        <p>Esta é a sua página de dashboard, acessível apenas para usuários autenticados.</p>
        <a href="{url_for('logout')}">Sair</a>
    """


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
