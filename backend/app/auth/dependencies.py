############################################
# IMPORTAÇÕES
############################################
# HTTPException, status, Depends: usados para retornar erros HTTP
#                                  e declarar dependências de rota
# HTTPBearer: extrai o token JWT do cabeçalho
#             "Authorization: Bearer <token>" e, no Swagger, exibe
#             um campo simples para colar o token diretamente
#             (diferente do OAuth2PasswordBearer, que espera um
#             fluxo de usuário/senha que não é o que usamos aqui).
# Session: tipo da sessão do banco de dados
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.security import decodificar_access_token
from app.models.funcionario import Funcionario, PerfilUsuario


############################################
# CONFIGURAÇÃO DO ESQUEMA DE AUTENTICAÇÃO
############################################
# Cria o esquema de segurança "Bearer Token" usado pelo Swagger.
# No botão "Authorize" da documentação, vai aparecer um único campo
# de texto ("Value"), onde você cola o token gerado pelo login.
esquema_bearer = HTTPBearer()


############################################
# DEPENDÊNCIA: OBTER USUÁRIO ATUAL
############################################
# Essa função é usada em qualquer rota que exija login, através de:
#
#   @router.get("/produtos")
#   def listar_produtos(funcionario_atual: Funcionario = Depends(obter_funcionario_atual)):
#       ...
#
# O FastAPI executa essa dependência ANTES da rota, extraindo o
# token do cabeçalho, validando, buscando o funcionário no banco e
# entregando o objeto já pronto para uso dentro da rota.
def obter_funcionario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Funcionario:

    token = credenciais.credentials

    credencial_invalida = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Tenta decodificar o token; se falhar (assinatura inválida,
    # token expirado, etc.), barra o acesso imediatamente.
    try:
        payload = decodificar_access_token(token)
        funcionario_id = payload.get("funcionario_id")
        if funcionario_id is None:
            raise credencial_invalida
    except JWTError:
        raise credencial_invalida

    # Busca o funcionário no banco para garantir que ele ainda
    # existe e está ativo (ex: caso tenha sido desativado depois
    # de o token ter sido emitido).
    funcionario = (
        db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    )
    if funcionario is None or not funcionario.ativo:
        raise credencial_invalida

    return funcionario


############################################
# DEPENDÊNCIA: EXIGIR PERFIL ESPECÍFICO
############################################
# Fábrica de dependências: gera uma função de validação que só
# libera o acesso se o funcionário logado tiver um dos perfis
# informados. Uso em uma rota:
#
#   @router.post("/funcionarios")
#   def criar_funcionario(
#       ...,
#       funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
#       _: None = Depends(exigir_perfil([PerfilUsuario.ADMINISTRADOR])),
#   ):
#       ...
#
# Assim, cada rota declara explicitamente quais perfis podem acessá-la.
def exigir_perfil(perfis_permitidos: List[PerfilUsuario]):
    def verificador(
        funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    ) -> None:
        if funcionario_atual.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para realizar esta ação.",
            )

    return verificador
