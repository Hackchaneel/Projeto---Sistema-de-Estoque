############################################
# IMPORTAÇÕES
############################################
# APIRouter: usado para agrupar as rotas de autenticação separadas
#            do resto da aplicação, e depois incluí-las no main.py
# Depends: injeta dependências do FastAPI (ex: sessão do banco)
# HTTPException, status: usados para retornar erros HTTP padronizados
# Session: tipo da sessão do banco de dados
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.empresa import Empresa
from app.models.funcionario import Funcionario
from app.auth.security import verificar_senha, criar_access_token
from app.auth.schemas import LoginRequest, TokenResponse


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
# prefix="/auth" -> todas as rotas aqui dentro começam com /auth
# tags=["Autenticação"] -> agrupa essas rotas na documentação Swagger
router = APIRouter(prefix="/auth", tags=["Autenticação"])


############################################
# ROTA DE LOGIN
############################################
# Recebe: código da empresa + código do funcionário + email + senha
# (nunca login apenas por email, conforme definido na arquitetura).
#
# Fluxo de validação:
# 1) Busca a empresa pelo código informado
# 2) Busca o funcionário DENTRO dessa empresa (empresa_id + código + email)
# 3) Verifica se o funcionário está ativo
# 4) Verifica se a senha informada bate com o hash salvo no banco
# 5) Se tudo estiver certo, gera e devolve um token JWT
@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):

    # Mensagem de erro genérica de propósito: não informamos qual
    # campo especificamente está errado (empresa, código, email ou
    # senha), para não dar pistas a quem estiver tentando adivinhar
    # credenciais válidas (boa prática de segurança).
    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Empresa, código, email ou senha inválidos.",
    )

    ########################################
    # 1) BUSCA A EMPRESA
    ########################################
    empresa = (
        db.query(Empresa).filter(Empresa.codigo == dados.codigo_empresa).first()
    )
    if not empresa:
        raise erro_credenciais

    ########################################
    # 2) BUSCA O FUNCIONÁRIO DENTRO DA EMPRESA
    ########################################
    funcionario = (
        db.query(Funcionario)
        .filter(
            Funcionario.empresa_id == empresa.id,
            Funcionario.codigo == dados.codigo_funcionario,
            Funcionario.email == dados.email,
        )
        .first()
    )
    if not funcionario:
        raise erro_credenciais

    ########################################
    # 3) VERIFICA SE O FUNCIONÁRIO ESTÁ ATIVO
    ########################################
    if not funcionario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este funcionário está inativo. Contate o administrador.",
        )

    ########################################
    # 4) VERIFICA A SENHA
    ########################################
    if not verificar_senha(dados.senha, funcionario.senha_hash):
        raise erro_credenciais

    ########################################
    # 5) GERA O TOKEN JWT
    ########################################
    # Guardamos dentro do token as informações mínimas necessárias
    # para identificar o funcionário e sua empresa/perfil em
    # requisições futuras, sem precisar consultar o banco toda vez
    # (exceto pela validação feita em obter_funcionario_atual).
    token = criar_access_token(
        dados={
            "funcionario_id": funcionario.id,
            "empresa_id": funcionario.empresa_id,
            "perfil": funcionario.perfil.value,
        }
    )

    return TokenResponse(access_token=token)
