############################################
# IMPORTAÇÕES
############################################
# create_engine: cria a conexão com o banco de dados PostgreSQL
# sessionmaker: cria "fábricas" de sessões para conversar com o banco
# declarative_base: classe base que todos os models (tabelas) vão herdar
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv


############################################
# CONFIGURAÇÕES
############################################
# Carrega as variáveis de ambiente definidas no arquivo .env
# (nunca deixamos senha ou dados sensíveis direto no código)
load_dotenv()

# URL de conexão com o banco de dados PostgreSQL.
# Formato esperado:
# postgresql://usuario:senha@host:porta/nome_do_banco
# Exemplo local:
# postgresql://postgres:1234@localhost:5432/estoque_db
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "A variável de ambiente DATABASE_URL não foi definida. "
        "Configure o arquivo .env antes de iniciar o sistema."
    )


############################################
# ENGINE
############################################
# O "engine" é o núcleo de comunicação entre o SQLAlchemy e o PostgreSQL.
# pool_pre_ping=True evita erros de conexão "caída" (comum em hospedagens
# como Render, onde a conexão pode ser fechada por inatividade).
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


############################################
# SESSÃO
############################################
# SessionLocal é a fábrica de sessões que usaremos em cada requisição.
# autocommit=False -> nós controlamos manualmente quando salvar (commit)
# autoflush=False  -> evita envios automáticos e inesperados ao banco
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


############################################
# BASE DECLARATIVA
############################################
# Todos os models (Empresa, Funcionario, Produto, etc.) vão herdar
# dessa classe Base. É ela que permite ao SQLAlchemy saber quais
# classes Python representam tabelas do banco de dados.
Base = declarative_base()


############################################
# FUNÇÃO DE DEPENDÊNCIA (usada pelo FastAPI)
############################################
# Essa função é usada com o sistema de dependências do FastAPI
# (Depends(get_db)) dentro das rotas, garantindo que cada requisição
# abra sua própria sessão com o banco e a feche corretamente ao final,
# mesmo que ocorra algum erro no meio do caminho.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
