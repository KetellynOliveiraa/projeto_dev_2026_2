from app import app, db, Opcao, Administrador
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    if not Administrador.query.filter_by(username='admin').first():
        administrador = Administrador(username='admin', senha_hash=generate_password_hash('senha123'))
        db.session.add(administrador)
        print('Administrador criado: usuario=admin, senha=senha123')
    else:
        print('Administrador já existe, pulando.')

    if Opcao.query.count() == 0:
        opcoes = [
            Opcao(titulo='Barraca 2 pessoas', descricao='Barraca impermeável, fácil montagem', icone='⛺'),
            Opcao(titulo='Mochila 60L', descricao='Ideal para trilhas de vários dias', icone='🎒'),
            Opcao(titulo='Trilha da Pedra Azul', descricao='Trilha de nível intermediário, 8km', icone='🏔️'),
        ]
        db.session.add_all(opcoes)
        print('3 opções de exemplo criadas.')
    else:
        print('Já existem opções cadastradas, pulando.')

    db.session.commit()
    print('Seed finalizado.')