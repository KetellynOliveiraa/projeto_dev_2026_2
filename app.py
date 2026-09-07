from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

gerenciador_login = LoginManager()
gerenciador_login.init_app(app)
gerenciador_login.login_view = 'login'

@gerenciador_login.user_loader
def carregar_usuario(user_id):
    return Administrador.query.get(int(user_id))


class Opcao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300))
    ativa = db.Column(db.Boolean, default=True)
    icone = db.Column(db.String(10), default='🎒')

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

class Administrador(db.Model, UserMixin):
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

        administrador = Administrador.query.filter_by(username=username).first()

        if administrador and check_password_hash(administrador.senha_hash, senha):
            login_user(administrador)
            return redirect(url_for('painel'))
        else:
            erro = 'Usuário ou senha inválidos.'

    return render_template('login.html', erro=erro)


@app.route('/painel')
@login_required
def painel():
    status_filtro = request.args.get('status', '')
    busca = request.args.get('busca', '').strip()
    pagina = request.args.get('pagina', 1, type=int)

    consulta = Registro.query

    if status_filtro:
        consulta = consulta.filter(Registro.status == status_filtro)

    if busca:
        termo = f'%{busca}%'
        consulta = consulta.filter(
            (Registro.nome.ilike(termo)) | (Registro.email.ilike(termo))
        )

    consulta = consulta.order_by(Registro.criado_em.desc())

    paginacao = consulta.paginate(page=pagina, per_page=10, error_out=False)

    return render_template('painel.html', paginacao=paginacao,
                            status_filtro=status_filtro, busca=busca)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/painel/registro/<int:registro_id>/status', methods=['POST'])
@login_required
def atualizar_status(registro_id):
    registro = Registro.query.get_or_404(registro_id)
    novo_status = request.form.get('status')

    if novo_status in ['confirmado', 'cancelado']:
        registro.status = novo_status
        db.session.commit()
        flash(f'Registro {novo_status} com sucesso.')

    return redirect(url_for('painel'))


@app.route('/painel/opcoes')
@login_required
def listar_opcoes():
    opcoes = Opcao.query.all()
    return render_template('opcoes.html', opcoes=opcoes)


@app.route('/painel/opcoes/nova', methods=['GET', 'POST'])
@app.route('/painel/opcoes/<int:opcao_id>/editar', methods=['GET', 'POST'])
@login_required
def form_opcao(opcao_id=None):
    opcao = Opcao.query.get(opcao_id) if opcao_id else None
    erros = []

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        icone = request.form.get('icone', '🎒').strip()

        if not titulo:
            erros.append('O título é obrigatório.')

        if not erros:
            if opcao:
                opcao.titulo = titulo
                opcao.descricao = descricao
                opcao.icone = icone
            else:
                opcao = Opcao(titulo=titulo, descricao=descricao, ativa=True, icone=icone)
                db.session.add(opcao)

            db.session.commit()
            flash('Opção salva com sucesso.')
            return redirect(url_for('listar_opcoes'))

    return render_template('opcao_form.html', erros=erros, opcao=opcao)


@app.route('/painel/opcoes/<int:opcao_id>/toggle', methods=['POST'])
@login_required
def toggle_opcao(opcao_id):
    opcao = Opcao.query.get_or_404(opcao_id)
    opcao.ativa = not opcao.ativa
    db.session.commit()
    flash('Opção atualizada com sucesso.')
    return redirect(url_for('listar_opcoes'))


if __name__ == '__main__':
    app.run(debug=True)