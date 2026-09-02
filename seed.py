from app import app, db, Opcao, Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(
            username='admin',
            senha_hash=generate_password_hash('senha123')
        )
        db.session.add(admin)
        print('Admin criado: usuario=admin, senha=senha123')
    else:
        print('Admin já existe, pulando.')

    if Opcao.query.count() == 0:
        opcoes = [
            Opcao(titulo='Barraca 2 pessoas', descricao='Barraca impermeável, fácil montagem', ativa=True),
            Opcao(titulo='Mochila 60L', descricao='Ideal para trilhas de vários dias', ativa=True),
            Opcao(titulo='Trilha da Pedra Azul', descricao='Trilha de nível intermediário, 8km', ativa=True),
        ]
        db.session.add_all(opcoes)
        print('3 opções de exemplo criadas.')
    else:
        print('Já existem opções cadastradas, pulando.')

    db.session.commit()
    print('Seed finalizado.')