############################################
# IMPORTAÇÕES
############################################
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.security import verificar_senha, gerar_hash_senha
from app.auth.dependencies import obter_funcionario_atual


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/perfil", tags=["Perfil"])


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
class PerfilResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    email: str
    perfil: PerfilUsuario
    empresa_id: int

    class Config:
        from_attributes = True


class TrocarSenhaRequest(BaseModel):
    senha_atual: str
    senha_nova: str


############################################
# ROTA: VER OS PRÓPRIOS DADOS
############################################
# Diferente da rota GET /funcionarios/{id} (que não existe, de
# propósito, para evitar que qualquer um veja dados de qualquer
# funcionário só pelo id), esta rota SEMPRE devolve os dados de
# quem está logado — identificado unicamente pelo token, nunca por
# um parâmetro na URL.
@router.get("/", response_model=PerfilResponse)
def ver_meu_perfil(
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return funcionario_atual


############################################
# ROTA: TROCAR A PRÓPRIA SENHA
############################################
# Exige a senha ATUAL como confirmação — evita que alguém que
# encontre uma sessão aberta (token válido, mas pessoa não
# presente) consiga trocar a senha sem saber a original.
@router.put("/senha", status_code=status.HTTP_204_NO_CONTENT)
def trocar_minha_senha(
    dados: TrocarSenhaRequest,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    if not verificar_senha(dados.senha_atual, funcionario_atual.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta.",
        )

    funcionario_atual.senha_hash = gerar_hash_senha(dados.senha_nova)
    db.commit()
    return None
