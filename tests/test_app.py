import unittest
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from app import app, db, Opcao, Administrador, Registro


class TesteFluxosPrincipais(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.contexto = app.app_context()
        self.contexto.push()
        db.create_all()

        self.opcao = Opcao(titulo='Barraca teste', descricao='desc', ativa=True, icone='⛺')
        db.session.add(self.opcao)

        self.administrador = Administrador(username='admin_teste', senha_hash=generate_password_hash('senha123'))
        db.session.add(self.administrador)
        db.session.commit()

        self.cliente = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.contexto.pop()

    def test_visitante_envia_formulario_com_sucesso(self):
        resposta = self.cliente.post('/enviar', data={
            'nome': 'Maria',
            'email': 'maria@teste.com',
            'opcao_id': self.opcao.id,
            'data': (date.today() + timedelta(days=5)).isoformat(),
        }, follow_redirects=True)

        self.assertEqual(resposta.status_code, 200)
        registro = Registro.query.filter_by(email='maria@teste.com').first()
        self.assertIsNotNone(registro)
        self.assertEqual(registro.status, 'pendente')

    def test_painel_bloqueado_sem_login(self):
        resposta = self.cliente.get('/painel', follow_redirects=False)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/login', resposta.location)

    def test_login_e_confirmacao_de_registro(self):
        registro = Registro(nome='Joao', email='joao@teste.com', opcao_id=self.opcao.id, data=date.today())
        db.session.add(registro)
        db.session.commit()

        self.cliente.post('/login', data={'username': 'admin_teste', 'senha': 'senha123'}, follow_redirects=True)

        resposta = self.cliente.post(f'/painel/registro/{registro.id}/status',
                                      data={'status': 'confirmado'}, follow_redirects=True)
        self.assertEqual(resposta.status_code, 200)

        registro_atualizado = Registro.query.get(registro.id)
        self.assertEqual(registro_atualizado.status, 'confirmado')


if __name__ == '__main__':
    unittest.main()