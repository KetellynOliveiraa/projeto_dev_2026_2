# Trilhas & Aventura

Sistema de aluguel de equipamentos e trilhas. Visitantes veem os itens disponíveis e solicitam aluguel; um administrador aprova ou cancela os pedidos e gerencia o catálogo de equipamentos.

## Pré-requisitos

- Python 3.13 (ou compatível 3.10+)
- pip
- Não é necessário instalar nenhum banco de dados separado — o projeto usa SQLite, que já vem embutido no Python.

## Instalação

```bash
git clone <url-do-seu-fork>
cd projeto_dev_2026_2
py -m venv venv
.\venv\Scripts\Activate.ps1    # Windows (PowerShell)
pip install -r requirements.txt
```

## Variáveis de ambiente

Copie o arquivo de exemplo e ajuste se quiser:

```bash
copy .env.example .env
```

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave usada pelo Flask para proteger a sessão de login. Troque por qualquer string aleatória própria. |
| `DATABASE_URL` | Caminho do banco SQLite. Padrão: `sqlite:///trilhas.db`. |

## Preparo do banco de dados

```bash
py seed.py
```

Esse comando cria as tabelas, o usuário administrador e 3 opções de exemplo (Barraca, Mochila, Trilha).

## Usuário administrador

- **Usuário:** `admin`
- **Senha:** `senha123`

Acesse em `/login` depois de subir a aplicação. Recomendo trocar essa senha diretamente no `seed.py` antes de qualquer uso além de teste local.

## Rodando a aplicação

```bash
py app.py
```

A aplicação responde em **http://127.0.0.1:5000**

Principais rotas:
- `/` — página pública
- `/enviar` — formulário de solicitação
- `/login` — login administrativo
- `/painel` — painel administrativo (requer login)
- `/painel/opcoes` — gerenciar equipamentos/trilhas (requer login)

## Rodando os testes

```bash
py -m unittest discover -s tests
```

## O que foi cortado ou simplificado (e por quê)

- **Conflito de datas**: não há verificação se o mesmo equipamento já está reservado no mesmo período. O enunciado não exigia isso explicitamente, e adicionaria complexidade de sobra para o prazo disponível.
- **Fotos reais dos equipamentos**: usei emojis como identidade visual de cada item, em vez de upload de imagens reais, para manter o escopo simples.
- **Edição de dados do registro após criado**: o admin pode confirmar/cancelar, mas não editar nome, email ou data de um registro já enviado.
- **Recuperação de senha do administrador**: não implementada, já que só existe um usuário administrador fixo.

Mais detalhes de decisões técnicas em `DECISOES.md`.