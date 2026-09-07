# Decisões técnicas

## Stack escolhida

Já tinha usado Flask antes, num projeto de cadastro de pessoas integrado com MySQL. Pra esse teste, optei por manter Flask (em vez de Django, que é o que a empresa mais usa) porque era a stack que eu já dominava, e pude focar o tempo aprendendo as partes que eram novas: autenticação de sessão com Flask-Login, e trabalhar com SQLite em vez de MySQL — mais simples pra quem for rodar o projeto localmente, sem precisar instalar nem configurar um servidor de banco separado.

## Modelagem de dados

Três tabelas: `Opcao` (equipamentos/trilhas), `Registro` (solicitações dos visitantes) e `Administrador`. `Registro` se relaciona com `Opcao` por chave estrangeira, permitindo acessar `registro.opcao.titulo` diretamente nos templates.

## Autenticação

Usei Flask-Login para gerenciar sessão do administrador, com `@login_required` protegendo as rotas do painel — inclusive a de logout, por consistência. Senha nunca é salva em texto puro, apenas como hash (`werkzeug.security`).

## Estrutura do projeto

Comecei desenhando uma estrutura com pastas separadas (`app/routes/`, `config.py` isolado, etc.), seguindo convenções comuns de projetos Flask maiores. Decidi voltar atrás e concentrar tudo em um único `app.py`. Preferi um projeto menor que eu dominasse de ponta a ponta a um "mais correto" tecnicamente que eu não soubesse explicar linha por linha.

## Filtro, busca e paginação

Implementados via query string (`/painel?status=pendente&busca=...`) e o método `.paginate()` do SQLAlchemy, que já resolve a paginação sem código manual de cálculo de offset.

## O que decidi não implementar

- Verificação de conflito de datas entre solicitações do mesmo equipamento.
- Edição de dados do visitante em um registro já enviado.
- Upload de fotos reais — usei emojis como identidade visual de cada item.
- Recuperação de senha do administrador (usuário único e fixo).

## Sobre o uso de IA

Já sabia Flask e integração com banco de dados de um projeto anterior (cadastro de pessoas com MySQL). Usei IA principalmente pra aprender a parte que era nova pra mim: autenticação de sessão com Flask-Login (login, logout, proteção de rota com `@login_required`), paginação de resultados via SQLAlchemy, e filtros de busca com `ilike`. Também deleguei a estrutura repetitiva das rotas (o "molde" de validar → salvar → redirecionar, que se repete em várias partes do projeto).

Um momento em que a sugestão veio com problema: em uma das primeiras versões da rota de envio do formulário, a lista `erros = []` foi colocada *depois* de um trecho que já tentava usar `erros.append(...)` dentro da conversão de data. Não quebrou de imediato, mas quebraria assim que alguém digitasse uma data num formato inválido. Percebi a ordem errada relendo o código antes de testar, e corrigi movendo a criação da lista pra antes de qualquer uso dela.

Uma decisão que tomei contra a sugestão inicial foi a estrutura de pastas: a sugestão original separava o projeto em vários arquivos e módulos (rotas em arquivos diferentes, config isolado), mais próximo do que um projeto Flask maior normalmente usa. Decidi voltar atrás e concentrar tudo em um `app.py` só, porque preferi entregar algo que eu dominasse de ponta a ponta a algo "mais correto" tecnicamente que eu não soubesse explicar se me perguntassem.