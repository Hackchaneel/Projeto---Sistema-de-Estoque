############################################
# IMPORTAÇÕES
############################################
# FastAPI: framework principal que cria e gerencia a API
# CORSMiddleware: permite que o frontend (React) acesse essa API
# database: importa a engine e a Base para criação das tabelas
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

# Importa o pacote de models para que todas as classes (Empresa,
# Funcionario, Categoria, Fornecedor, Produto) sejam registradas na
# Base do SQLAlchemy ANTES de chamarmos Base.metadata.create_all().
# Sem essa importação, as tabelas correspondentes não seriam criadas.
from app import models  # noqa: F401

# Importa os routers (grupos de rotas) do sistema. Conforme novos
# módulos forem criados (movimentações, dashboard...), seus routers
# serão importados e incluídos aqui do mesmo jeito.
from app.routes import (
    auth,
    empresas,
    funcionarios,
    categorias,
    fornecedores,
    produtos,
    movimentacoes,
    alertas,
    perfil,
)


############################################
# CONFIGURAÇÕES INICIAIS
############################################
# Cria a instância principal da aplicação FastAPI.
# title/description/version aparecem automaticamente na documentação
# gerada em /docs (Swagger) e /redoc.
app = FastAPI(
    title="Sistema de Estoque",
    description="API do sistema de gestão de estoque multiempresa",
    version="0.1.0",
)


############################################
# CORS (Cross-Origin Resource Sharing)
############################################
# Necessário para que o frontend React (rodando em outra porta/domínio,
# ex: Vercel) consiga se comunicar com essa API sem ser bloqueado pelo
# navegador. Em produção, o ideal é restringir "allow_origins" para o
# domínio real do frontend, em vez de usar "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # TODO: restringir para o domínio do frontend em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


############################################
# CRIAÇÃO DAS TABELAS
############################################
# Essa linha cria automaticamente, no banco de dados, todas as tabelas
# que forem definidas nos models (herdando de Base) e que ainda não
# existirem. Em um projeto mais maduro, isso normalmente é substituído
# por um sistema de migrações (ex: Alembic), mas para o início do
# projeto essa abordagem é suficiente.
Base.metadata.create_all(bind=engine)


############################################
# ROTAS
############################################
# Registra os routers na aplicação. Cada router agrupa as rotas de
# um módulo do sistema (autenticação, empresas, funcionários,
# categorias, fornecedores, produtos...).
app.include_router(auth.router)
app.include_router(empresas.router)
app.include_router(funcionarios.router)
app.include_router(categorias.router)
app.include_router(fornecedores.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)
app.include_router(alertas.router)
app.include_router(perfil.router)


############################################
# ROTA DE VERIFICAÇÃO (HEALTH CHECK)
############################################
# Rota simples para confirmar que a API está no ar. Útil para testar
# localmente e para serviços de hospedagem (Render) verificarem se a
# aplicação está saudável.
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "mensagem": "API do Sistema de Estoque rodando com sucesso.",
    }
