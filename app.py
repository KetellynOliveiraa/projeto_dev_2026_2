from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


class Opcao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300))
    ativa = db.Column(db.Boolean, default=True)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    opcao_id = db.Column(db.Integer, db.ForeignKey('opcao.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pendente')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    opcao = db.relationship('Opcao', backref='registros')

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)


@app.route('/')
def home():
    opcoes = Opcao.query.filter_by(ativa=True).all()
    return render_template('home.html', opcoes=opcoes)


@app.route('/enviar', methods=['GET', 'POST'])
def enviar():
    opcoes = Opcao.query.filter_by(ativa=True).all()

    if request.method == 'POST':
        erros = []

        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        opcao_id = request.form.get('opcao_id')

        data_str = request.form.get('data')
        data = None
        if data_str:
            try:
                data = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                erros.append('Data inválida.')

        if not nome:
            erros.append('O nome é obrigatório.')

        if not email or '@' not in email:
            erros.append('Informe um email válido.')

        if not opcao_id:
            erros.append('Escolha um equipamento ou trilha.')

        if not data:
            erros.append('Escolha uma data.')

        if erros:
            return render_template('formulario.html', opcoes=opcoes, erros=erros,
                                    nome=nome, email=email, data=data_str)

        novo_registro = Registro(
            nome=nome,
            email=email,
            opcao_id=opcao_id,
            data=data
        )
        db.session.add(novo_registro)
        db.session.commit()

        return redirect(url_for('sucesso'))

    return render_template('formulario.html', opcoes=opcoes)


@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '')

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.senha_hash, senha):
            login_user(admin)
            return redirect(url_for('painel'))
        else:
            erro = 'Usuário ou senha inválidos.'

    return render_template('login.html', erro=erro)

@app.route('/painel')
@login_required
def painel():
    registros = Registro.query.order_by(Registro.criado_em.desc()).all()
    return render_template('painel.html', registros=registros)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)