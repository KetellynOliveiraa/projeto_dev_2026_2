from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

from datetime import datetime
from flask_login import UserMixin

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

if __name__ == '__main__':
    app.run(debug=True)