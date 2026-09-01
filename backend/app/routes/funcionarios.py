############################################
# IMPORTAÇÕES
############################################
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import JWTError

from app.database.database import get_db
from app.models.empresa import Empresa
from app.models.funcionario import Funcionario, PerfilUsuario
from app.auth.security import gerar_hash_senha, decodificar_access_token
from app.auth.dependencies import obter_funcionario_atual, exigir_perfil


############################################
# CONFIGURAÇÃO DO ROUTER
############################################
router = APIRouter(prefix="/funcionarios", tags=["Funcionários"])


############################################
# SCHEMAS (ENTRADA E SAÍDA)
############################################
class FuncionarioCreate(BaseModel):
    codigo_empresa: str
    codigo: str
    nome: str
    email: EmailStr
    senha: str
    perfil: PerfilUsuario = PerfilUsuario.FUNCIONARIO


class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    perfil: Optional[PerfilUsuario] = None
    ativo: Optional[bool] = None


class FuncionarioResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    empresa_id: int

    class Config:
        from_attributes = True


############################################
# FUNÇÃO AUXILIAR: TENTAR IDENTIFICAR QUEM ESTÁ LOGADO (OPCIONAL)
############################################
# Diferente de obter_funcionario_atual (que EXIGE login e barra a
# requisição se não houver token válido), esta função apenas TENTA
# identificar o funcionário logado, devolvendo None se não houver
# token, se o token for inválido, ou se o funcionário não existir/
# estiver inativo. É usada exclusivamente na rota de criação de
# funcionário, que precisa lidar com dois cenários: alguém já
# logado cadastrando um colega, OU ninguém logado ainda cadastrando
# o primeiro administrador de uma empresa nova (ver mais abaixo).
def _obter_funcionario_opcional(request: Request, db: Session) -> Optional[Funcionario]:
    cabecalho_auth = request.headers.get("Authorization")
    if not cabecalho_auth or not cabecalho_auth.startswith("Bearer "):
        return None

    token = cabecalho_auth.split(" ", 1)[1]
    try:
        payload = decodificar_access_token(token)
    except JWTError:
        return None

    funcionario_id = payload.get("funcionario_id")
    if not funcionario_id:
        return None

    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if funcionario and funcionario.ativo:
        return funcionario
    return None


############################################
# ROTA: CRIAR FUNCIONÁRIO
############################################
# Esta rota tem uma regra em duas camadas, para resolver o seguinte
# paradoxo: se SEMPRE exigirmos "só Administrador cadastra", uma
# empresa recém-criada (sem nenhum funcionário ainda) nunca
# conseguiria ter seu primeiro administrador — ninguém consegue
# fazer login para autorizar essa primeira criação.
#
# Regra aplicada:
# 1) Se a empresa AINDA NÃO TEM NENHUM funcionário: a criação é
#    permitida sem exigir login, e o perfil é sempre forçado para
#    ADMINISTRADOR (ignorando o que foi enviado no campo "perfil"),
#    já que essa pessoa está fundando o acesso da empresa.
# 2) Se a empresa JÁ TEM pelo menos um funcionário: a criação exige
#    estar logado E ser Administrador DAQUELA empresa, como antes.
@router.post(
    "/", response_model=FuncionarioResponse, status_code=status.HTTP_201_CREATED
)
def criar_funcionario(
    dados: FuncionarioCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    ########################################
    # 1) BUSCA A EMPRESA PELO CÓDIGO
    ########################################
    empresa = (
        db.query(Empresa).filter(Empresa.codigo == dados.codigo_empresa).first()
    )
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada para o código informado.",
        )

    ########################################
    # 2) VERIFICA SE É O PRIMEIRO FUNCIONÁRIO (BOOTSTRAP)
    ########################################
    ja_existe_algum_funcionario = (
        db.query(Funcionario).filter(Funcionario.empresa_id == empresa.id).first()
        is not None
    )

    perfil_a_atribuir = dados.perfil

    if not ja_existe_algum_funcionario:
        # Ninguém precisa estar logado neste caso — mas o perfil é
        # sempre Administrador, não importa o que foi enviado.
        perfil_a_atribuir = PerfilUsuario.ADMINISTRADOR
    else:
        # A partir do segundo funcionário em diante, exige login E
        # perfil Administrador da MESMA empresa.
        funcionario_atual = _obter_funcionario_opcional(request, db)
        if funcionario_atual is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não foi possível validar as credenciais.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if funcionario_atual.perfil != PerfilUsuario.ADMINISTRADOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para realizar esta ação.",
            )
        if funcionario_atual.empresa_id != empresa.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode cadastrar funcionários na sua própria empresa.",
            )

    ########################################
    # 3) VERIFICA DUPLICIDADE DENTRO DA EMPRESA
    ########################################
    funcionario_existente = (
        db.query(Funcionario)
        .filter(
            Funcionario.empresa_id == empresa.id,
            (Funcionario.codigo == dados.codigo) | (Funcionario.email == dados.email),
        )
        .first()
    )
    if funcionario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um funcionário com esse código ou email nessa empresa.",
        )

    ########################################
    # 4) CRIA O FUNCIONÁRIO COM SENHA JÁ EM HASH
    ########################################
    novo_funcionario = Funcionario(
        empresa_id=empresa.id,
        codigo=dados.codigo,
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil=perfil_a_atribuir,
    )

    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)

    return novo_funcionario


############################################
# ROTA: LISTAR FUNCIONÁRIOS DA PRÓPRIA EMPRESA
############################################
@router.get("/", response_model=List[FuncionarioResponse])
def listar_funcionarios(
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
):
    return (
        db.query(Funcionario)
        .filter(Funcionario.empresa_id == funcionario_atual.empresa_id)
        .all()
    )


############################################
# FUNÇÃO AUXILIAR: BUSCAR FUNCIONÁRIO DA PRÓPRIA EMPRESA
############################################
def _buscar_funcionario_da_empresa(
    funcionario_id: int, funcionario_atual: Funcionario, db: Session
) -> Funcionario:
    funcionario = (
        db.query(Funcionario)
        .filter(
            Funcionario.id == funcionario_id,
            Funcionario.empresa_id == funcionario_atual.empresa_id,
        )
        .first()
    )
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado.",
        )
    return funcionario


############################################
# ROTA: ATUALIZAR FUNCIONÁRIO
############################################
@router.put("/{funcionario_id}", response_model=FuncionarioResponse)
def atualizar_funcionario(
    funcionario_id: int,
    dados: FuncionarioUpdate,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil([PerfilUsuario.ADMINISTRADOR])),
):
    funcionario = _buscar_funcionario_da_empresa(funcionario_id, funcionario_atual, db)

    dados_para_atualizar = dados.model_dump(exclude_unset=True)

    if "senha" in dados_para_atualizar:
        senha_nova = dados_para_atualizar.pop("senha")
        if senha_nova:
            funcionario.senha_hash = gerar_hash_senha(senha_nova)

    for campo, valor in dados_para_atualizar.items():
        setattr(funcionario, campo, valor)

    db.commit()
    db.refresh(funcionario)
    return funcionario


############################################
# ROTA: DESATIVAR FUNCIONÁRIO
############################################
@router.delete("/{funcionario_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db),
    funcionario_atual: Funcionario = Depends(obter_funcionario_atual),
    _: None = Depends(exigir_perfil([PerfilUsuario.ADMINISTRADOR])),
):
    funcionario = _buscar_funcionario_da_empresa(funcionario_id, funcionario_atual, db)

    if funcionario.id == funcionario_atual.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode desativar a própria conta.",
        )

    funcionario.ativo = False
    db.commit()
    return None
