## TODO com Fast API

Projeto tem como objetivo contruir um api simples de To-Do utilizando o FastAPI.

Este projeto segue o tutorial de [FastAPI do Zero](https://fastapidozero.dunossauro.com/) feito pelo Dunossauro.

Apesar de já ter experiencia com desenvolvimento em FastAPI, resolvi reciclar o conhecimento que possuo realizando a última versão do curso disponível.

## Sumário
- [Status](#status)
- [Como executar](#como-executar)
- [Tasks disponíveis](#️-tasks-disponíveis)
- [Executando os testes](#-executando-os-testes)

## Status

Status e etapas que o curso propõe:
- ✅ _Configurando o ambiente de desenvolvimento_
- ✅ _Introdução ao desenvolvimento WEB_
- ✅ _Estruturando o projeto e criando rotas CRUD_
- ✅ _Configurando o banco de dados e gerenciando migrações com Alembic_
- ✅ _Integrando banco de dados à API_
- ✅ _Autenticação e Autorização com JWT_
- ✅ _Refatorando a estrutura do projeto_
- ✅ _Tornando o projeto assíncrono_
- ✅ _Tornando o sistema de autenticação robusto_
- ✅ _Criando rotas CRUD para gerenciamento de tarefas_
- ✅ _Dockerizando a nossa aplicação e introduzindo o PostgreSQL_
- ✅ _Automatizando os testes com Integração Contínua (CI)_
- ⏭️ _Fazendo deploy no Fly.io_ => validar se ainda é possível

### Sobre Fly.io

No momento do desenvolvimento, o Fly.io mudou sua forma de atuar, cobrando agora para ter uma versão do Postgres.
Como o projeto pretende ser simples apenas para a apresentação quando necessário, desconsiderei utilizar esse método.
Em projetos futuros, irei analisar formas de contronar isso (ex: usar fly.io só para app e outra plataforma como bd)

## Como Executar

### 🐳 Executando com Docker (Recomendado)

A forma mais simples de executar o projeto é usando Docker Compose, que irá configurar tanto a aplicação quanto o banco PostgreSQL:

```bash
# Clonar o repositório
git clone <url-do-repo>
cd fast_zero

# Criar arquivo .env com as variáveis necessárias
cp .env.example .env

# Executar com docker compose
docker compose up
```

A aplicação estará disponível em `http://localhost:8000` e a documentação da API em `http://localhost:8000/docs`.

### 🐍 Executando sem Docker

Para executar localmente sem Docker, você precisará ter Python 3.14+ e Poetry instalados, além de um banco PostgreSQL rodando.

#### Configurando o PostgreSQL

Você pode subir apenas o PostgreSQL via Docker:

```bash
# Executar apenas o banco de dados
docker run -d \
  --name postgres-fast-zero \
  -e POSTGRES_USER=app_user \
  -e POSTGRES_PASSWORD=app_password \
  -e POSTGRES_DB=app_db \
  -p 5432:5432 \
  postgres:16
```

#### Executando a aplicação

```bash
# Instalar dependências
poetry install

# Configurar variáveis de ambiente no .env
# DATABASE_URL=postgresql+psycopg://app_user:app_password@localhost:5432/app_db

# Executar migrações do banco
poetry run alembic upgrade head

# Iniciar a aplicação
poetry run task run
```

## 🛠️ Tasks Disponíveis

O projeto utiliza o Taskipy para gerenciar tarefas comuns. Aqui estão as principais:

| Task | Descrição |
|------|-----------|
| `task lint` | Executa verificação de código com Ruff |
| `task format` | Formata o código seguindo o padrão do projeto |
| `task run` | Inicia o servidor de desenvolvimento |
| `task test` | Executa todos os testes com coverage |

```bash
# Exemplos de uso
poetry run task lint     # Verificar código
poetry run task format   # Formatar código
poetry run task run      # Rodar aplicação
poetry run task test     # Executar testes
```

## 🧪 Executando os Testes

Para executar os testes, use:

```bash
poetry run task test
```

### O que acontece por trás dos panos:

1. **Lint automático**: Antes dos testes, o Ruff verifica a qualidade do código
2. **Testcontainers**: Os testes utilizam containers PostgreSQL isolados para cada execução
3. **Coverage**: Coleta métricas de cobertura do código
4. **Relatório HTML**: Após os testes, gera relatório visual em `htmlcov/index.html`

O uso do Testcontainers garante que os testes sejam executados em um ambiente limpo e isolado, sem interferir no banco de desenvolvimento.


## 🔮 Próximos passos

Vejo algumas opções que posso implementar como estudo:

- Alterar a arquitetura: Apesar de ser um projeto simples, não gosto que fique a camada de acesso ao banco nas rotas, devo revisar isso, algo como DDD.
- Adicionar logs: pretendo estudar e colocar o loguru
- Observabilidade: talvez implementar o envio de dados para o [OpenTelemetry](https://opentelemetry.io/)

## Outros projetos

Apesar de me empolgar com os próximos passos desse projeto, devo dar uma atenção em outros dois projetos:

- Criar uma API de acervo digital em python, como menciona [aqui](https://fastapidozero.dunossauro.com/estavel/15/)
- Criar uma [Leilão online](https://github.com/danielmsilverio/auction_app) em Elixir - só criei o repositório, ainda estou escrevendo os entregáveis
