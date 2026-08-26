# Sistema de Estoque

Sistema de gestão de estoque multiempresa, com controle de produtos,
fornecedores, movimentações, alertas e relatórios.

## Estrutura do projeto

```
sistema-estoque/
├── backend/
│   ├── app/
│   │   ├── auth/          -> autenticação e permissões (login, JWT)
│   │   ├── database/      -> conexão com o PostgreSQL (SQLAlchemy)
│   │   ├── models/        -> tabelas do banco (Empresa, Produto, etc.)
│   │   ├── routes/        -> endpoints da API (rotas do FastAPI)
│   │   ├── services/      -> regras de negócio (lógica das funcionalidades)
│   │   └── main.py        -> ponto de entrada da aplicação FastAPI
│   ├── .env.example       -> modelo de variáveis de ambiente
│   └── requirements.txt   -> dependências Python
├── frontend/               -> aplicação React (a ser criada)
├── docs/                   -> documentação do projeto
├── .gitignore
└── README.md
```

## Como rodar o backend localmente

1. Entre na pasta do backend:
   ```
   cd backend
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Copie o arquivo de variáveis de ambiente e preencha com seus dados:
   ```
   cp .env.example .env
   ```

5. Certifique-se de que o PostgreSQL está rodando e que o banco
   informado em `DATABASE_URL` já existe.

6. Rode a aplicação:
   ```
   uvicorn app.main:app --reload
   ```

7. Acesse a documentação automática da API em:
   ```
   http://localhost:8000/docs
   ```

## Próximos passos

- Criar os models (Empresa, Funcionário, Produto, Fornecedor, etc.)
- Criar o sistema de autenticação (login por código da empresa +
  código do funcionário + email + senha)
- Criar as rotas de CRUD para cada entidade
- Iniciar o frontend em React
